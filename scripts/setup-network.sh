#!/usr/bin/env bash
# ==============================================================================
# 5G Network Slicing Lab - TUN Interface, NAT & Traffic Control Setup
# ==============================================================================
# Usage:
#   sudo ./setup-network.sh [start|stop|status]
# ==============================================================================

set -euo pipefail

ACTION="${1:-start}"

# Default outbound WAN interface for NAT (auto-detected if available)
WAN_IF="$(ip route show default 2>/dev/null | awk '/default/ {print $5}' | head -n 1 || true)"
if [[ -z "${WAN_IF}" ]]; then
  WAN_IF="eth0"
fi

create_tun() {
  local dev="$1"
  local ip_cidr="$2"

  if ! ip link show "${dev}" >/dev/null 2>&1; then
    echo "Creating TUN interface: ${dev}"
    ip tuntap add name "${dev}" mode tun
  fi
  
  # Assign IP if not already set
  if ! ip addr show dev "${dev}" | grep -q "${ip_cidr}"; then
    echo "Assigning ${ip_cidr} to ${dev}"
    ip addr add "${ip_cidr}" dev "${dev}"
  fi
  ip link set dev "${dev}" up
}

delete_tun() {
  local dev="$1"
  if ip link show "${dev}" >/dev/null 2>&1; then
    echo "Removing TUN interface: ${dev}"
    ip link set dev "${dev}" down || true
    ip tuntap del name "${dev}" mode tun || true
  fi
}

start() {
  echo "=== [1/4] Enabling IPv4 Forwarding ==="
  sysctl -w net.ipv4.ip_forward=1 >/dev/null

  echo "=== [2/4] Setting up TUN interfaces for 5G Slices ==="
  # Slice 1 (eMBB): 10.45.0.1/16
  create_tun "ogstun" "10.45.0.1/16"
  # Slice 2 (URLLC): 10.46.0.1/16
  create_tun "ogstun2" "10.46.0.1/16"
  # Slice 3 (MIoT): 10.47.0.1/16
  create_tun "ogstun3" "10.47.0.1/16"

  echo "=== [3/4] Configuring NAT (MASQUERADE) via ${WAN_IF} ==="
  for subnet in "10.45.0.0/16" "10.46.0.0/16" "10.47.0.0/16"; do
    if ! iptables -t nat -C POSTROUTING -s "${subnet}" -o "${WAN_IF}" -j MASQUERADE 2>/dev/null; then
      iptables -t nat -A POSTROUTING -s "${subnet}" -o "${WAN_IF}" -j MASQUERADE
    fi
  done

  echo "=== [4/4] Configuring Traffic Shaping (tc) per Slice ==="
  # SST 1 (eMBB): 1 Gbps DL / 100 Mbps UL limit
  tc qdisc replace dev ogstun root tbf rate 1000mbit burst 128kb latency 50ms 2>/dev/null || true

  # SST 2 (URLLC): 100 Mbps profile with low-latency priority
  tc qdisc replace dev ogstun2 root tbf rate 100mbit burst 32kb latency 10ms 2>/dev/null || true

  # SST 3 (MIoT): 1 Mbps rate limit for IoT telemetry
  tc qdisc replace dev ogstun3 root tbf rate 1mbit burst 16kb latency 50ms 2>/dev/null || true

  echo "Network setup successfully completed!"
}

stop() {
  echo "=== Cleaning up Traffic Shaping ==="
  tc qdisc del dev ogstun root 2>/dev/null || true
  tc qdisc del dev ogstun2 root 2>/dev/null || true
  tc qdisc del dev ogstun3 root 2>/dev/null || true

  echo "=== Cleaning up NAT Rules ==="
  for subnet in "10.45.0.0/16" "10.46.0.0/16" "10.47.0.0/16"; do
    iptables -t nat -D POSTROUTING -s "${subnet}" -o "${WAN_IF}" -j MASQUERADE 2>/dev/null || true
  done

  echo "=== Tearing down TUN interfaces ==="
  delete_tun "ogstun2"
  delete_tun "ogstun3"
  # ogstun is standard for Open5GS, we only tear it down if needed
  delete_tun "ogstun"

  echo "Network teardown completed."
}

status() {
  echo "=== TUN Interfaces ==="
  ip -br addr show dev ogstun 2>/dev/null || echo "ogstun: not found"
  ip -br addr show dev ogstun2 2>/dev/null || echo "ogstun2: not found"
  ip -br addr show dev ogstun3 2>/dev/null || echo "ogstun3: not found"

  echo -e "\n=== Traffic Control (tc) Disciplines ==="
  tc qdisc show dev ogstun 2>/dev/null || true
  tc qdisc show dev ogstun2 2>/dev/null || true
  tc qdisc show dev ogstun3 2>/dev/null || true

  echo -e "\n=== Active NAT POSTROUTING Rules ==="
  iptables -t nat -S POSTROUTING 2>/dev/null | grep -E '10\.4[567]\.0\.0' || echo "No slice NAT rules active."
}

case "${ACTION}" in
  start)
    start
    ;;
  stop)
    stop
    ;;
  status)
    status
    ;;
  *)
    echo "Usage: $0 {start|stop|status}"
    exit 1
    ;;
esac

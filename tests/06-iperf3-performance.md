# Test 06 — iperf3 Throughput across the Three Slices

> Run the infrastructure startup commands in **00-startup.md** before this test. Commands below use the original laboratory identifiers and Linux network namespaces. Run each terminal block in a separate terminal when indicated. Commands reconstructed beyond the report are identified as **reproduction commands**, not independently verified historical commands.

## 1. Start the 5G infrastructure

Execute `00-startup.md`. Confirm the three namespaces for UE1.

## 2. Start the iperf3 test servers

The report states that `iperf3-servers.service` launches servers on TCP ports 5201, 5202 and 5203.

```bash
sudo systemctl start iperf3-servers.service
sudo systemctl status iperf3-servers.service --no-pager
sudo ss -lntp | grep -E ':5201|:5202|:5203'
```

If that unit does not exist, start three **foreground servers in three separate terminals** (reproduction commands):

```bash
iperf3 -s -B 10.47.0.1 -p 5201
```

```bash
iperf3 -s -B 10.45.0.1 -p 5202
```

```bash
iperf3 -s -B 10.46.0.1 -p 5203
```

## 3. Uplink tests (UE1 → slice gateway)

**SST 1 / eMBB:**

```bash
sudo ip netns exec ueransim-999700000000001-internet-psi1 iperf3 -c 10.45.0.1 -p 5202 -t 10
```

**SST 2 / URLLC:**

```bash
sudo ip netns exec ueransim-999700000000001-internet-psi2 iperf3 -c 10.46.0.1 -p 5203 -t 10
```

**SST 3 / MIoT:**

```bash
sudo ip netns exec ueransim-999700000000001-internet-psi3 iperf3 -c 10.47.0.1 -p 5201 -t 10
```

## 4. Downlink tests (gateway → UE1, using iperf3 reverse mode)

```bash
sudo ip netns exec ueransim-999700000000001-internet-psi1 iperf3 -c 10.45.0.1 -p 5202 -R -t 10
sudo ip netns exec ueransim-999700000000001-internet-psi2 iperf3 -c 10.46.0.1 -p 5203 -R -t 10
sudo ip netns exec ueransim-999700000000001-internet-psi3 iperf3 -c 10.47.0.1 -p 5201 -R -t 10
```

## 5. Inspect traffic shaping

```bash
sudo tc -s qdisc show dev ogstun2
sudo tc -s qdisc show dev ogstun3
```

## Reported measurements (not new test results)

| Slice | Uplink | Downlink |
|---|---:|---:|
| SST 1 | 100 Mbit/s | 225 Mbit/s |
| SST 2 | 93.7 Mbit/s | 93.2 Mbit/s |
| SST 3 | 604 kbit/s | 978 kbit/s |

**Discrepancy:** the reported SST 3 uplink value of 604 kbit/s is higher than the configured 512 kbit/s uplink Session-AMBR. These measurements therefore do not unambiguously prove uplink enforcement; re-test and inspect directionality, measurement intervals and Linux `tc` rules.

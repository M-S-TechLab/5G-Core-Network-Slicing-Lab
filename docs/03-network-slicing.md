# 5G Network Slicing Implementation

This document explains the **three-slice 5G Standalone (SA) laboratory** implemented using Open5GS and UERANSIM. It focuses on the configuration actually present in this repository, rather than claiming performance properties that have not been measured.

For installation and overall configuration, see [01-installation.md](01-installation.md) and [02-network-configuration.md](02-network-configuration.md).

## 1. Laboratory objectives

The goal is to provide three logically distinct PDU Session paths for simulated user equipment (UE). The Open5GS configuration includes an independent **SMF–UPF pair**, UE address pool and TUN interface for each SST. The same DNN (`internet`) is used on all three slices.

The service scenarios used in the laboratory are:

- **SST 1 — eMBB-oriented:** Nextcloud file transfers and OBS-to-Owncast video streaming.
- **SST 2 — URLLC-oriented:** a separately configured path with its own SMF, UPF and subscriber QoS profile.
- **SST 3 — MIoT-oriented:** MQTT publish/subscribe traffic using a Mosquitto broker on TCP port 1883.

The terms *eMBB-oriented*, *URLLC-oriented* and *MIoT-oriented* describe intended laboratory use cases. Slice separation and assigned QoS parameters alone do **not** demonstrate guaranteed bandwidth, deterministic latency, radio scheduling, or end-to-end isolation.

## 2. Topology

```text
UERANSIM UE1 / UE2
       |
       | simulated NR radio link
       v
UERANSIM gNB  (PLMN 999/70, TAC 1)
       |
       +---- N2 / NGAP ----> Open5GS AMF
       |
       +---- N3 / GTP-U ---> selected UPF
                                   |
                  +----------------+----------------+
                  |                |                |
               SST 1            SST 2            SST 3
             SMF1/UPF1        SMF2/UPF2        SMF3/UPF3
               ogstun          ogstun2          ogstun3
            10.45.0.0/16    10.46.0.0/16    10.47.0.0/16
```

The diagram represents **three logical user-plane paths**, not three physical radio cells. The actual choice of session is driven by the requested S-NSSAI, subscriber authorization and core-network session selection.

## 3. Slice configuration summary

| Property | SST 1 | SST 2 | SST 3 |
| --- | --- | --- | --- |
| Intended use | eMBB | URLLC | MIoT |
| SMF file | [`smf.yaml`](../configs/open5gs/smf.yaml) | [`smf-sst2.yaml`](../configs/open5gs/smf-sst2.yaml) | [`smf-sst3.yaml`](../configs/open5gs/smf-sst3.yaml) |
| SMF SBI address | `127.0.0.4` | `127.0.0.24` | `127.0.0.34` |
| UPF file | [`upf.yaml`](../configs/open5gs/upf.yaml) | [`upf-sst2.yaml`](../configs/open5gs/upf-sst2.yaml) | [`upf-sst3.yaml`](../configs/open5gs/upf-sst3.yaml) |
| UPF PFCP address | `127.0.0.7` | `127.0.0.8` | `127.0.0.9` |
| UE address pool | `10.45.0.0/16` | `10.46.0.0/16` | `10.47.0.0/16` |
| Gateway | `10.45.0.1` | `10.46.0.1` | `10.47.0.1` |
| TUN device | `ogstun` | `ogstun2` | `ogstun3` |
| DNN | `internet` | `internet` | `internet` |

Every SMF config uses `mtu: 1400` and DNS resolvers `8.8.8.8` and `8.8.4.4`. Each SMF has a PFCP client pointing to the corresponding UPF.

## 4. AMF, NSSF and gNB support

The [AMF configuration](../configs/open5gs/amf.yaml) sets PLMN MCC `999` / MNC `70`, TAC `1`, and declares all three SST values under `plmn_support`:

```yaml
plmn_support:
  - plmn_id:
      mcc: 999
      mnc: 70
    s_nssai:
      - sst: 1
      - sst: 2
      - sst: 3
```

The [NSSF configuration](../configs/open5gs/nssf.yaml) also lists SST 1, 2 and 3 in its configured NSI entries. The [gNB configuration](../configs/ueransim/open5gs-gnb.yaml) advertises the same slices, PLMN and TAC and connects to AMF at `127.0.0.5:38412`.

Matching identifiers are necessary for registration and slice-aware session establishment. The YAML files document the intended configuration; runtime logs must be used to verify successful signaling.

## 5. Configuring SMF and UPF for each SST

The following excerpts illustrate the relationship between the SST, subscriber subnet, PFCP peer and UPF TUN device. They are **excerpts only**; use the complete YAML files for deployment.

**SST 2 SMF — `smf-sst2.yaml`:**

```yaml
smf:
  pfcp:
    client:
      upf:
        - address: 127.0.0.8
  session:
    - subnet: 10.46.0.0/16
      gateway: 10.46.0.1
  info:
    - s_nssai:
        - sst: 2
      dnn:
        - internet
```

**SST 2 UPF — `upf-sst2.yaml`:**

```yaml
upf:
  pfcp:
    server:
      - address: 127.0.0.8
  session:
    - subnet: 10.46.0.0/16
      gateway: 10.46.0.1
      dev: ogstun2
```

The other two SMF–UPF pairs follow the same pattern with their respective addresses, SST values and TUN interfaces. Distinct SMF/UPF configuration files do not automatically create or start additional processes; the service definitions or launch commands for those instances must also be provided.

## 6. UE PDU Session requests

Both [`ue1.yaml`](../configs/ueransim/ue1.yaml) and [`ue2.yaml`](../configs/ueransim/ue2.yaml) request three IPv4 PDU Sessions using the same DNN and different SST values:

```yaml
sessions:
  - type: IPv4
    apn: internet
    slice:
      sst: 1
  - type: IPv4
    apn: internet
    slice:
      sst: 2
  - type: IPv4
    apn: internet
    slice:
      sst: 3
```

`useNamespace: true` permits session interfaces to be managed in Linux network namespaces. The resulting namespace names and UE IP addresses must be verified on the running system rather than assumed from the YAML alone.

## 7. Subscriber QoS settings in MongoDB

The supplied subscriber export includes three profiles (IMSI ending `001`, `002` and `003`). All three advertise the same three SSTs. The first two correspond to the operational UERANSIM UE configurations. The third subscriber exists in the database export, but no corresponding operational UE3 configuration is included here.

For the exported profiles, the following values are configured on the `internet` session:

| Parameter | SST 1 | SST 2 | SST 3 |
| --- | --- | --- | --- |
| 5QI (`qos.index`) | `6` | `1` | `70` |
| ARP priority level | `4` | `1` | `12` |
| Downlink session AMBR | `1 Gbps` | `100 Mbps` | `1 Mbps` |
| Uplink session AMBR | `100 Mbps` | `100 Mbps` | `512 Kbps` |
| Default slice indicator | `true` | `false` | `false` |

The export stores AMBR units as Open5GS enum values: `1` = Kbps, `2` = Mbps, `3` = Gbps. **These are configured policy values, not measured throughputs.** They do not by themselves establish the latency or reliability of a working URLLC service.

The subscriber export also contains authentication material (`security.k` and `security.opc`). These values are part of an explicitly educational laboratory and should not be reused in external or production networks. A full MongoDB dump containing WebUI administrator password hashes should **not** be committed.

## 8. Laboratory application mapping

### SST 1: file transfer and streaming

The intended applications are Nextcloud file operations (upload, sharing and download between UEs) and OBS-to-Owncast live video streaming. Document the specific commands, endpoints and observed results in separate test notes under [`../tests/`](../tests/).

### SST 2: independent slice path

This slice has dedicated SMF/UPF configuration, an address pool and a different subscriber QoS policy. **Do not claim that URLLC latency or packet-error targets have been achieved** without a documented measurement setup and results.

### SST 3: MQTT traffic

The laboratory uses Mosquitto as an MQTT broker, with the publish/subscribe traffic associated with SST 3. MQTT runs over TCP port `1883` in the reported scenario. The MQTT protocol QoS levels 0, 1 and 2 are **application-layer delivery semantics**, distinct from 5G QoS and 5QI.

## 9. Runtime verification

The following read-only checks help confirm the configuration on a running Ubuntu host:

```bash
# Show the configured TUN interfaces
ip -br addr show ogstun
ip -br addr show ogstun2
ip -br addr show ogstun3

# List UERANSIM-created network namespaces
sudo ip netns list

# Inspect running Open5GS processes
pgrep -af 'open5gs-(amfd|smfd|upfd|nssfd|nrfd|scpd)'

# Verify the main Open5GS services
systemctl --no-pager status open5gs-amfd open5gs-smfd open5gs-upfd
```

Actual UE registration and session success should be demonstrated with gNB/UE terminal logs, Open5GS service logs and namespace interface assignments. The existence of the YAML files alone is not evidence that the services are currently running.

## 10. Reproduction notes and limitations

- The YAML configuration files are published under [`../configs/`](../configs/).
- Starting secondary SMF/UPF instances requires the specific launch procedure or systemd units used in the laboratory; that part must still be documented.
- Host setup for `ogstun`, `ogstun2`, `ogstun3`, forwarding, NAT and any relevant firewall rules must be documented separately.
- The MongoDB subscriber JSON is an export of laboratory data, **not** a guaranteed direct-import script. A reliable import/initialization procedure remains to be documented.
- Intended eMBB, URLLC and MIoT service labels should be distinguished from any measured KPIs.

## References

- [Open5GS documentation](https://open5gs.org/open5gs/docs/)
- [UERANSIM repository](https://github.com/aligungr/UERANSIM)
- 3GPP TS 23.501 — System architecture for the 5G System
- 3GPP TS 23.502 — Procedures for the 5G System

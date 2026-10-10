# 5G Standalone Network Configuration

This document describes the configuration used in our virtualized 5G Standalone (5G SA) laboratory, based on **Open5GS** and **UERANSIM**. It complements [01-installation.md](01-installation.md), which covers installation of the underlying software.

The configuration files referred to here are available under [`../configs/open5gs/`](../configs/open5gs/) and [`../configs/ueransim/`](../configs/ueransim/). All addresses, subscriber identities, and authentication parameters belong to the educational laboratory.

## 1. Laboratory topology

```text
UE1 (UERANSIM) ──┐
                 ├── simulated radio link ── gNB (UERANSIM)
UE2 (UERANSIM) ──┘                               │
                                               N2 / N3
                                                │
                         ┌────────── Open5GS 5G Core ──────────┐
                         │ AMF, AUSF, UDM, UDR, NRF, NSSF,     │
                         │ PCF and SCP                          │
                         │                                     │
                         │ SST 1: SMF1 ── UPF1 ── ogstun       │
                         │ SST 2: SMF2 ── UPF2 ── ogstun2      │
                         │ SST 3: SMF3 ── UPF3 ── ogstun3      │
                         └─────────────────────────────────────┘
                                            │
                                       Data networks
```

The diagram is conceptual: N2 carries control-plane signaling to the AMF, while N3 carries user-plane traffic toward the UPF. The three slice-specific UPF configurations use separate tunnel interfaces and address pools.

## 2. Common identifiers

| Parameter | Laboratory value |
| --- | --- |
| MCC | `999` |
| MNC | `70` |
| TAC | `1` |
| DNN / APN | `internet` |
| Slice identifiers | SST `1`, `2`, `3` |
| AMF NGAP endpoint | `127.0.0.5:38412` |
| gNB link, NGAP and GTP IP | `127.0.0.1` |
| SCP SBI endpoint | `http://127.0.0.200:7777` |
| NRF SBI endpoint | `http://127.0.0.10:7777` |

The configurations shown here assume that the gNB and Open5GS network functions can reach these loopback addresses in the same host network environment. Deployment across multiple VMs requires changing the interface addresses and routing accordingly.

## 3. AMF configuration

File: [`../configs/open5gs/amf.yaml`](../configs/open5gs/amf.yaml).

The AMF listens for NGAP signaling at `127.0.0.5` and advertises the laboratory PLMN and three supported slices:

```yaml
amf:
  ngap:
    server:
      - address: 127.0.0.5
  tai:
    - plmn_id:
        mcc: 999
        mnc: 70
      tac: 1
  plmn_support:
    - plmn_id:
        mcc: 999
        mnc: 70
      s_nssai:
        - sst: 1
        - sst: 2
        - sst: 3
```

This is an excerpt, not a replacement for the complete configuration. The gNB must use a matching PLMN and TAC and point to the AMF NGAP endpoint.

## 4. NRF, NSSF and service-based interfaces

The NRF is configured at `127.0.0.10:7777` and includes serving PLMN `999/70`. The SCP listens on `127.0.0.200:7777` and forwards service-based communications toward the NRF. Other network functions, including AUSF, UDM, UDR and PCF, reference the SCP in their active SBI client sections.

The NSSF configuration includes slice entries for **SST 1, 2 and 3**. See [`nrf.yaml`](../configs/open5gs/nrf.yaml), [`scp.yaml`](../configs/open5gs/scp.yaml) and [`nssf.yaml`](../configs/open5gs/nssf.yaml).

The UDR and PCF refer to the local MongoDB database using `mongodb://localhost/open5gs`. The UDM configuration also references Home Network private-key **file paths**; do not publish the private-key files themselves.

## 5. Slice-specific SMF and UPF configuration

Each slice has a distinct SMF, UPF, address pool and TUN interface:

| Slice | SMF config / SBI IP | UPF config / PFCP IP | Subscriber subnet | Gateway | TUN device |
| --- | --- | --- | --- | --- | --- |
| SST 1 | `smf.yaml` / `127.0.0.4` | `upf.yaml` / `127.0.0.7` | `10.45.0.0/16` | `10.45.0.1` | `ogstun` |
| SST 2 | `smf-sst2.yaml` / `127.0.0.24` | `upf-sst2.yaml` / `127.0.0.8` | `10.46.0.0/16` | `10.46.0.1` | `ogstun2` |
| SST 3 | `smf-sst3.yaml` / `127.0.0.34` | `upf-sst3.yaml` / `127.0.0.9` | `10.47.0.0/16` | `10.47.0.1` | `ogstun3` |

All three SMF configurations advertise DNN `internet`, assign MTU `1400`, and reference their corresponding UPF via PFCP. Example from the SST 2 SMF:

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

The matching SST 2 UPF declares:

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

**Important:** The YAML files define the intended IP pools and TUN device names, but they do not document how the Ubuntu interfaces were created, assigned IPs, or connected to external networks. The corresponding commands and NAT/forwarding rules must be documented separately in [`../scripts/`](../scripts/). Likewise, additional SMF/UPF processes require an explicit start procedure or service units; their actual startup method has not yet been verified from the submitted files.

## 6. UERANSIM gNB configuration

File: [`../configs/ueransim/open5gs-gnb.yaml`](../configs/ueransim/open5gs-gnb.yaml).

Relevant settings:

```yaml
mcc: '999'
mnc: '70'
tac: 1
linkIp: 127.0.0.1
ngapIp: 127.0.0.1
gtpIp: 127.0.0.1
amfConfigs:
  - address: 127.0.0.5
    port: 38412
slices:
  - sst: 1
  - sst: 2
  - sst: 3
```

The gNB uses a simulated radio link; this setup does not require physical 5G radio hardware.

## 7. UERANSIM UE configuration

Files: [`ue1.yaml`](../configs/ueransim/ue1.yaml) and [`ue2.yaml`](../configs/ueransim/ue2.yaml).

| UE | SUPI (IMSI) | DNN | Requested PDU sessions |
| --- | --- | --- | --- |
| UE1 | `imsi-999700000000001` | `internet` | IPv4 on SST 1, 2 and 3 |
| UE2 | `imsi-999700000000002` | `internet` | IPv4 on SST 1, 2 and 3 |

Both UE configurations enable Linux network namespaces (`useNamespace: true`), search for the gNB at `127.0.0.1`, include SST 1–3 in `configured-nssai`, and select SST 1 as the default NSSAI.

The UE authentication configuration (`key`, `op` with `opType: OPC`, and `amf`) must match the respective subscriber entry in MongoDB. These are **laboratory-only test credentials** and must not be reused in real networks.

## 8. MongoDB subscriber profiles and QoS

The supplied subscriber export contains **three** laboratory profiles (`999700000000001`, `999700000000002`, and `999700000000003`). UE1 and UE2 correspond to the first two; the third profile is present in the database export but no matching UE3 configuration is documented here.

For each of the three subscribers, the slice session settings include:

| Slice | DNN | 5QI | ARP priority level | Default slice |
| --- | --- | --- | --- | --- |
| SST 1 | `internet` | 6 | 4 | Yes |
| SST 2 | `internet` | 1 | 1 | No |
| SST 3 | `internet` | 70 | 12 | No |

The QoS values above are configured subscriber policies, **not experimental proof** of a particular latency, throughput or traffic isolation level.

The file `mongodb_subscribers.json` is an export of subscriber records, **not** a drop-in WebUI import specification. A reproducible subscriber provisioning/import procedure must be documented and validated separately. Do **not** commit the full MongoDB dump containing the WebUI administrator account password hash and salt.

## 9. Configuration deployment and verification

The repository contains reference copies of the laboratory configuration files. On a newly installed VM, the operator must back up the packaged defaults, place the Open5GS YAML files under `/etc/open5gs/`, and use the UERANSIM YAML files at their corresponding paths. Do not overwrite the configuration of an existing working installation without a backup.

Examples of **non-destructive checks** on Ubuntu:

```bash
ls /etc/open5gs/
ls ~/UERANSIM/config/
systemctl list-units 'open5gs-*' --type=service
ip -br addr
ip netns list
```

When the system is running, consult the Open5GS and UERANSIM logs to verify gNB association, UE registration, and the establishment of three PDU sessions per UE. Logs and service names depend on how the extra instances were started.

## 10. Reproducibility checklist

Before claiming full reproducibility, this repository still needs documented and tested instructions for:

1. Provisioning the subscribers in MongoDB/WebUI with synchronized authentication credentials.
2. Creating and assigning the three TUN interfaces (`ogstun`, `ogstun2`, `ogstun3`).
3. Configuring IPv4 forwarding, routing and NAT as used in the laboratory.
4. Starting all required Open5GS services, including extra SMF and UPF instances.
5. Starting the UERANSIM gNB and UEs with the correct configuration paths.
6. Verifying registration, PDU sessions and application-level connectivity.

## References

- [Open5GS documentation](https://open5gs.org/open5gs/docs/)
- [UERANSIM repository](https://github.com/aligungr/UERANSIM)
- [Laboratory installation guide](01-installation.md)

# 5G Core Network Slicing Lab

**A virtualized 5G Standalone (5G SA) testbed using Open5GS, UERANSIM, and MongoDB, with three network slices and application-level experiments.**

This project implements a single-node 5G laboratory on **Ubuntu 22.04 LTS**, deployed in a virtual machine (VirtualBox or UTM). The 5G Core is provided by **Open5GS**, while **UERANSIM** emulates a gNodeB and user equipment (UE). The project explores network slicing, subscriber authentication, PDU session establishment, differentiated QoS profiles, and application traffic over simulated 5G connections.

> **Scope:** Educational and research testbed. The radio access is simulated in software; no physical 5G radio hardware is involved. Network identifiers and subscriber credentials are laboratory-only examples.

## Network architecture

```text
         UE1 (UERANSIM)              UE2 (UERANSIM)
         IMSI ...001                 IMSI ...002
                \                     /
                 \-- simulated RAN --/
                          |
                    gNB (UERANSIM)
                      N2 / N3
                          |
              +-----------+------------+
              |      Open5GS 5GC       |
              | AMF, AUSF, UDM, UDR    |
              | NRF, NSSF, SCP, PCF    |
              +-----------+------------+
                          |
             +------------+------------+
             |            |            |
        SST 1 / eMBB  SST 2 / URLLC SST 3 / MIoT
          SMF + UPF    SMF + UPF     SMF + UPF
           ogstun       ogstun2       ogstun3
         10.45.0.0/16 10.46.0.0/16 10.47.0.0/16
             |            |            |
         Nextcloud    Asterisk +     Mosquitto
          / iperf3      Twinkle       / iperf3
```

All components run on the same Ubuntu guest. Control-plane signaling uses NGAP/SCTP and the 5G Service-Based Architecture; the user plane uses GTP-U and PFCP. Each slice has its own SMF/UPF configuration and IP address pool.

## Laboratory configuration

| Item | Value |
| --- | --- |
| Operating system | Ubuntu 22.04 LTS |
| Virtualization | VirtualBox or UTM |
| Core network | Open5GS (laboratory version 2.8.0) |
| RAN and UE emulator | UERANSIM |
| Subscriber database | MongoDB |
| MCC / MNC | `999` / `70` |
| TAC | `1` |
| DNN | `internet` |
| UEs | Two primary simulated subscribers |
| Network slices | SST `1`, `2`, `3` |

### Network slices and QoS

| Slice | Service profile | 5QI | ARP priority | Session-AMBR (DL / UL) | Subnet / UPF interface |
| --- | --- | ---: | ---: | --- | --- |
| SST 1 | eMBB | 6 | 4 | 1 Gbit/s / 100 Mbit/s | `10.45.0.0/16` / `ogstun` |
| SST 2 | URLLC-oriented | 1 | 1 | 100 Mbit/s / 100 Mbit/s | `10.46.0.0/16` / `ogstun2` |
| SST 3 | MIoT-oriented | 70 | 12 | 1 Mbit/s / 512 Kbit/s | `10.47.0.0/16` / `ogstun3` |

The values above are the configured subscriber QoS profiles. Slice labels describe the intended workload classes; they do **not** by themselves establish compliance with commercial URLLC or massive-IoT performance requirements.

## Automated UE Provisioning

The [`scripts/provision.py`](scripts/provision.py) script automates subscriber provisioning for Open5GS and UERANSIM.

It registers UE profiles in the MongoDB `open5gs.subscribers` collection and generates the corresponding UERANSIM YAML configuration files.

Each generated UE is configured with:

- Unique IMSI, IMEI, and IMEISV identifiers.
- Authentication credentials for the laboratory environment.
- Three network slice subscriptions (SST 1, 2, and 3).
- Slice-specific 5QI and ARP priority parameters.
- Uplink and downlink Session-AMBR limits.
- Three IPv4 PDU sessions using the `internet` DNN.

### Requirements

Python 3, PyMongo, PyYAML, and a running local MongoDB instance are required. The UERANSIM configuration directory and gNB search addresses must be adapted to the target environment.

### Usage

Create two new UEs:

```bash
python3 provision.py 2
```

This creates two additional subscribers, assigning the next available UE indices.

Update existing subscribers:

```bash
python3 provision.py update-all
```

**Warning:** The update operation replaces existing subscriber profiles and overwrites the corresponding UE YAML files. Back up existing configurations before execution.

The script uses demonstration authentication credentials intended exclusively for the virtual 5G laboratory.

## Experiments

The technical project report describes six experiments:

| Experiment | Purpose | Documentation |
| --- | --- | --- |
| Unauthorized UE | Reject registration of an IMSI absent from MongoDB | [Test 01](tests/01-unauthorized-ue.md) |
| Unsupported network slice | Request SST 4, which is not authorized | [Test 02](tests/02-unsupported-network-slice.md) |
| VoIP over SST 2 | SIP/RTP call using Asterisk and Twinkle | [Test 03](tests/03-voip-urllc.md) |
| File transfer over SST 1 | WebDAV upload and download using Nextcloud | [Test 04](tests/04-nextcloud-embb.md) |
| MQTT over SST 3 | Publish/subscribe sensor telemetry with Mosquitto | [Test 05](tests/05-mqtt-miot.md) |
| Performance measurements | iperf3 uplink/downlink tests on all three slices | [Test 06](tests/06-iperf3-performance.md) |

The original report includes measured throughput values and application-level observations. These are **reported experimental results**, not independent performance guarantees. In particular, the SST 3 uplink rate reported by iperf3 (604 kbit/s) exceeds its configured 512 kbit/s AMBR and warrants further verification.

## Getting started

1. Follow the [installation guide](docs/01-installation.md) to prepare Ubuntu, MongoDB, and Open5GS.
2. Review the [network configuration](docs/02-network-configuration.md) and place the supplied YAML configurations in the corresponding Open5GS and UERANSIM installations.
3. Provision the subscriber profiles using the [MongoDB subscriber data](configs/open5gs/mongodb_subscribers.json), if that file is included in your checkout. Do not import the full administrative database dump.
4. Review the [network slicing implementation](docs/03-network-slicing.md), including the required UPF interfaces and network policies.
5. Follow the [laboratory startup commands](tests/00-startup.md), then select an experiment from the table above.

**Reproduction note:** Dedicated SMF/UPF service units, TUN/NAT setup, traffic shaping, and some application-specific configurations may require adaptation to your installation. The repository documentation distinguishes verified configuration values from environment-dependent procedures.

## Repository contents

| Location | Contents |
| --- | --- |
| [`configs/open5gs/`](configs/open5gs/) | Open5GS Network Function YAML files and laboratory subscriber data |
| [`configs/ueransim/`](configs/ueransim/) | gNB, UE1, and UE2 configurations |
| [`docs/`](docs/) | Installation, network configuration, and slicing documentation |
| [`tests/`](tests/) | Startup instructions and six experimental procedures |
| [`images/`](images/) | Architecture diagrams and screenshots, when available |
| [`scripts/`](scripts/) | Optional executable helper scripts, when available |

## Technology references

- [Open5GS documentation](https://open5gs.org/open5gs/docs/)
- [UERANSIM repository](https://github.com/aligungr/UERANSIM)
- [MongoDB documentation](https://www.mongodb.com/docs/)
- 3GPP TS 23.501 — System architecture for the 5G System
- 3GPP TS 23.502 — Procedures for the 5G System

## Authors

- **Domenico Mallardo**
- **Vincenzo Santonicola**

Developed as a collaborative university networking and cloud infrastructures project.

## License

A license has not yet been selected. Please contact the authors before reusing original project material beyond what applicable law permits. Open5GS, UERANSIM, and other third-party software retain their respective licenses.


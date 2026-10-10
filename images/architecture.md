# 5G Standalone Network Slicing Laboratory - Architecture

The diagram reflects the single-VM Open5GS/UERANSIM testbed. Both simulated UEs can request a separate PDU session for each subscribed S-NSSAI (SST 1, 2, and 3). The simulated RAN and core functions are shared; slice-specific SMF/UPF instances and IP subnets are separate.

```mermaid
flowchart TB
  UE1["UE1 / UERANSIM<br/>IMSI ...001"]
  UE2["UE2 / UERANSIM<br/>IMSI ...002"]
  GNB["gNB / UERANSIM<br/>PLMN 999/70 · TAC 1"]

  UE1 -->|Simulated radio| GNB
  UE2 -->|Simulated radio| GNB

  subgraph CORE["Open5GS 5G Standalone Core - Ubuntu VM"]
    CP["Control plane<br/>AMF · AUSF · UDM · UDR<br/>NRF · SCP · NSSF · PCF"]
    DB[("MongoDB<br/>Subscriber profiles")]
    CP --- DB

    subgraph S1["SST 1 - eMBB"]
      SMF1["SMF 1"] -->|N4 / PFCP| UPF1["UPF 1<br/>ogstun<br/>10.45.0.0/16"]
    end

    subgraph S2["SST 2 - URLLC-oriented"]
      SMF2["SMF 2"] -->|N4 / PFCP| UPF2["UPF 2<br/>ogstun2<br/>10.46.0.0/16"]
    end

    subgraph S3["SST 3 - MIoT-oriented"]
      SMF3["SMF 3"] -->|N4 / PFCP| UPF3["UPF 3<br/>ogstun3<br/>10.47.0.0/16"]
    end

    CP --- SMF1
    CP --- SMF2
    CP --- SMF3
  end

  GNB -->|N2 / NGAP / SCTP| CP
  GNB -.->|N3 / GTP-U| UPF1
  GNB -.->|N3 / GTP-U| UPF2
  GNB -.->|N3 / GTP-U| UPF3

  UPF1 --> APP1["Nextcloud / iperf3"]
  UPF2 --> APP2["Asterisk / Twinkle / iperf3"]
  UPF3 --> APP3["Mosquitto MQTT / iperf3"]
```

# Test 02 — Unsupported Network Slice (SST 4)

## Objective

Check how the 5G Standalone core handles a PDU Session Establishment request for **SST 4**, which is not configured in the laboratory network and is not subscribed by the test UE.

The test uses an already-provisioned subscriber (IMSI `999700000000001`) with its existing authentication credentials. It is intended to distinguish successful subscriber registration from a rejected data-session request.

## Configuration

The ready-to-use test configuration is available at [`configs/ueransim/ue_sst4.yaml`](../configs/ueransim/ue_sst4.yaml). **Do not modify `ue1.yaml`.**

The important portion of `ue_sst4.yaml` is:

```yaml
sessions:
  - type: IPv4
    apn: internet
    slice:
      sst: 4

configured-nssai:
  - sst: 1
  - sst: 2
  - sst: 3

default-nssai:
  - sst: 1
```

The UE keeps the valid IMSI, authentication key, OPc, MCC `999`, MNC `70`, and gNB loopback address. SST 4 appears **only in the requested PDU session**; the registration's configured/default NSSAI still lists supported slices. This setup specifically probes the session request for SST 4 rather than requesting an unsupported NSSAI during registration.

## Procedure

### 1. Start the existing 5G infrastructure

Follow [00-startup.md](00-startup.md) to start the gNB and confirm the core is running. **Do not run the regular `ue1.yaml` process simultaneously**: both UE configurations use the same IMSI.

### 2. Start the SST 4 test UE

Run from the UERANSIM working directory where `build/` and `config/` are accessible; copy the repository's `ue_sst4.yaml` to the UERANSIM `config/` directory if needed.

```bash
sudo ./build/nr-ue -c config/ue_sst4.yaml
```

Keep this terminal open and examine the UE registration messages and PDU Session Establishment result.

### 3. Inspect the Open5GS logs

Use separate terminals:

```bash
sudo journalctl -u open5gs-amfd -f
```

```bash
sudo journalctl -u open5gs-smfd -f
```

The service-specific journal output depends on how the core was installed. If separate services are not used, consult the corresponding Open5GS log files.

### 4. Check the session namespaces

```bash
sudo ip netns list
```

The absence of a namespace for SST 4 is consistent with failed session establishment; namespace inspection alone does not prove the specific NAS rejection cause.

## Reported outcome and interpretation

The project report (section 4.2) describes successful subscriber authentication followed by a rejected PDU Session Establishment request for SST 4, reporting `DNN_NOT_SUPPORTED_OR_NOT_SUBSCRIBED` and no data tunnel for that session.

**Verify the actual NAS/SMF log messages in the running environment.** An unsupported SST can fail at different stages depending on the AMF/SMF/NSSF configuration and Open5GS version. Do not present a specific error cause as guaranteed without captured logs.

## Expected checks

- UE identity is recognized using the existing subscribed IMSI.
- SST 4 is not a subscribed or deployed slice in the testbed.
- No successful SST 4 PDU session, IP interface, or GTP-U tunnel is created.
- UE and core logs are retained as evidence of the actual rejection mechanism.

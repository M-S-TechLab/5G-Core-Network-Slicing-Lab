# Test 02 — Unsupported SST 4

> Run the infrastructure startup commands in **00-startup.md** before this test. Commands below use the original laboratory identifiers and Linux network namespaces. Run each terminal block in a separate terminal when indicated. Commands reconstructed beyond the report are identified as **reproduction commands**, not independently verified historical commands.

## 1. Start the network and the gNB

Run the relevant commands in `00-startup.md`. Keep the normal UE1 configuration unchanged; create a separate test configuration based on UE1 with the same valid credentials, but requesting **SST 4** in `sessions` and `configured-nssai` (and set a suitable `default-nssai` if needed). This modification is a required **configuration step**, not a shell command recorded in the report.

## 2. Start the test UE

```bash
sudo ./build/nr-ue -c config/ue_sst4.yaml
```

`ue_sst4.yaml` is a **new test configuration to create**; it is not among the YAML files you supplied.

## 3. Monitor AMF and SMF messages (separate terminals)

```bash
sudo journalctl -u open5gs-amfd -f
```

```bash
sudo journalctl -u open5gs-smfd -f
```

## 4. Verify no SST 4 PDU namespace was established

```bash
sudo ip netns list
```

## Outcome reported in the project report

The report records a failed SST 4 PDU Session Establishment with `DNN_NOT_SUPPORTED_OR_NOT_SUBSCRIBED`. Verify the actual reject message. This result does not by itself establish whether rejection came from AMF slice authorization or SMF/DNN/session selection.

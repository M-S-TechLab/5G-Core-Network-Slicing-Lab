# Test 01 — Unregistered UE (Rogue UE Reject)

> Run the infrastructure startup commands in **00-startup.md** before this test. Commands below use the original laboratory identifiers and Linux network namespaces. Run each terminal block in a separate terminal when indicated. Commands reconstructed beyond the report are identified as **reproduction commands**, not independently verified historical commands.

## 1. Start the gNB and Open5GS

Run the startup commands in `00-startup.md`, but the authorized UE processes are **not required** for this negative test.

## 2. Start the unauthorized UE (new terminal)

```bash
sudo ./build/nr-ue -c config/ue_test.yaml
```

The supplied `ue_test.yaml` requests registration with IMSI `999700000099999`, which is not present in the supplied subscriber JSON.

## 3. Observe the AMF log (second terminal)

```bash
sudo journalctl -u open5gs-amfd -f
```

## 4. Confirm that no namespace has been created for the rogue UE

```bash
sudo ip netns list
```

## Outcome reported in the project report

The report states that the unknown subscriber causes an authentication lookup failure and NAS registration rejection. Confirm the **actual reject cause** in the logs: do not assume the same NAS cause is produced in all Open5GS versions.

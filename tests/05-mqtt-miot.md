# Test 05 — MQTT Publish/Subscribe over SST 3

> Run the infrastructure startup commands in **00-startup.md** before this test. Commands below use the original laboratory identifiers and Linux network namespaces. Run each terminal block in a separate terminal when indicated. Commands reconstructed beyond the report are identified as **reproduction commands**, not independently verified historical commands.

## 1. Start the core, gNB and both UEs

Execute `00-startup.md`; both `psi3` namespaces must exist.

## 2. Start Mosquitto

```bash
sudo systemctl start mosquitto
sudo systemctl is-active mosquitto
sudo ss -lntp | grep ':1883'
```

Mosquitto must accept clients addressed to `10.47.0.1:1883` (not only `127.0.0.1`).

## 3. Start the subscriber from UE2 (terminal 1)

```bash
sudo ip netns exec ueransim-999700000000002-internet-psi3 \
  mosquitto_sub -h 10.47.0.1 -p 1883 -t 'sensori/telemetria' -v
```

## 4. Publish a telemetry message from UE1 (terminal 2)

```bash
sudo ip netns exec ueransim-999700000000001-internet-psi3 \
  mosquitto_pub -h 10.47.0.1 -p 1883 -t 'sensori/telemetria' \
  -m '{"temp":22.4,"umidita":60}'
```

## 5. Repeat periodically (optional reproduction procedure)

```bash
while true; do
  sudo ip netns exec ueransim-999700000000001-internet-psi3 \
    mosquitto_pub -h 10.47.0.1 -p 1883 -t 'sensori/telemetria' \
    -m '{"temp":22.4,"umidita":60}'
  sleep 2
done
```

Stop with `Ctrl+C`.

## 6. Inspect network traffic (optional)

```bash
sudo tcpdump -ni ogstun3 tcp port 1883
```

The report states that the subscriber received messages and measured latency below 0.5 ms; it does not include raw timing data.

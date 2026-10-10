# Test 03 — VoIP with Asterisk and Twinkle over SST 2

> Run the infrastructure startup commands in **00-startup.md** before this test. Commands below use the original laboratory identifiers and Linux network namespaces. Run each terminal block in a separate terminal when indicated. Commands reconstructed beyond the report are identified as **reproduction commands**, not independently verified historical commands.

## 1. Start the core, gNB and both UEs

Execute `00-startup.md`. Both `psi2` namespaces must be present.

## 2. Start the PBX and verify the SIP port

```bash
sudo systemctl start asterisk
sudo systemctl is-active asterisk
sudo ss -lunp | grep ':5060'
```

## 3. Inspect configured SIP extensions (PBX console)

```bash
sudo asterisk -rvvv
```

In the Asterisk console (command shown for inspection, depending on SIP driver):

```text
pjsip show endpoints
```

The Asterisk configuration files are provided in [`../configs/asterisk/`](../configs/asterisk/). Copy `pjsip.conf` and `extensions.conf` to `/etc/asterisk/` before starting Asterisk.

## 4. Start Twinkle for UE1 on SST 2 (terminal 1)

Twinkle profiles are provided in [`../configs/twinkle/`](../configs/twinkle/). Launch Twinkle under the active user's environment:

```bash
sudo ip netns exec ueransim-999700000000001-internet-psi2 sudo -u "$USER" twinkle -c -f configs/twinkle/ue1.cfg
```

## 5. Start Twinkle for UE2 on SST 2 (terminal 2)

Launch Twinkle for UE2 with a separate user profile directory:

```bash
mkdir -p "$HOME/ue2_home"
sudo ip netns exec ueransim-999700000000002-internet-psi2 sudo -u "$USER" env HOME="$HOME/ue2_home" twinkle -c -f configs/twinkle/ue2.cfg
```

## 6. Place the call, send DTMF tones, and terminate (UE1 / UE2 Twinkle console)

1. From UE1 Twinkle console, initiate the SIP call to UE2:
   ```text
   call 1002
   ```

2. When the call rings on UE2, answer:
   ```text
   answer
   ```

3. Once connected, send in-call DTMF tones from UE1:
   ```text
   dtmf 1234
   ```
   *(This transmits RFC 2833 / RFC 4733 RTP telephone-event packets for digits 1, 2, 3, and 4 over the URLLC slice).*

4. Terminate the VoIP session from UE1:
   ```text
   bye
   ```

## 7. Monitor SIP/RTP and DTMF during the test

Capture signaling and media on the SST 2 tunnel interface (`ogstun2`):

```bash
sudo tcpdump -ni ogstun2 'udp port 5060 or udp portrange 10000-20000'
```

Observed behavior:
- Successful SIP `INVITE` / `200 OK` session negotiation over UDP 5060.
- Low-latency bi-directional RTP audio stream (G.711 / G.722) over SST 2.
- Telephony event RTP packets representing DTMF tones `1234`.
- Clean session teardown with SIP `BYE` and `200 OK`.
- Average RTT measured around 1.1 ms with 0% packet loss.

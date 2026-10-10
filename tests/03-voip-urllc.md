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

The report identifies extensions **1001** and **1002**, but does not include the PBX and Twinkle configuration files.

## 4. Start Twinkle for UE1 on SST 2 (terminal 1)

```bash
sudo ip netns exec ueransim-999700000000001-internet-psi2 sudo -u ubuntu twinkle -c -f ue1.cfg
```

## 5. Start Twinkle for UE2 on SST 2 (terminal 2)

```bash
sudo ip netns exec ueransim-999700000000002-internet-psi2 sudo -u ubuntu env HOME=/home/ubuntu/ue2_home twinkle -c -f ue2.cfg
```

**Important:** the commands above are normalized from the report and use the account name `ubuntu` appearing there. On the `domiima` VM, change `ubuntu` and the `HOME` value to the actual local Twinkle account. The `.cfg` arguments are file names, not absolute file paths.

## 6. Place the call (UE1 Twinkle console)

```text
call 1002
```

## 7. Monitor SIP/RTP during the test

```bash
sudo tcpdump -ni ogstun2 'udp port 5060 or udp portrange 10000-20000'
```

The report states successful SIP INVITE/200 OK, 1.1 ms RTT and no packet loss; no independent raw RTP output was supplied.

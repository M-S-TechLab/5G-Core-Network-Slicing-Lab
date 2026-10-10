# 00 — Start the 5G Laboratory

The following commands start the existing installation. They **do not install or overwrite configuration files**. Execute the UERANSIM commands from the directory where the executable and `.yaml` files are accessible. Use the appropriate relative YAML filename for your environment.

## 1. Optional check of dedicated SMF/UPF instances

The project also uses dedicated SST 2 and SST 3 instances. **Their exact service unit names are not included in the exported YAML**, so first display what is available:

```bash
systemctl list-unit-files | grep -E 'open5gs.*(smf|upf)|smf[23]|upf[23]'
```

If the following units exist on your Ubuntu, start them:

```bash
sudo systemctl start open5gs-smf2d open5gs-smf3d open5gs-upf2d open5gs-upf3d
```

The previous command is **conditional**: use the actual service names if different; never assume these are installed by Open5GS itself.

## 2. Verify the UPF interfaces, forwarding and traffic control

```bash
ip -br addr show
sysctl net.ipv4.ip_forward
sudo iptables -t nat -S POSTROUTING
sudo tc qdisc show dev ogstun2
sudo tc qdisc show dev ogstun3
```

Expected addresses: `ogstun` → `10.45.0.1/16`; `ogstun2` → `10.46.0.1/16`; `ogstun3` → `10.47.0.1/16`. The report describes NAT and `tc` shaping, but does **not** provide the exact original setup commands. Do not blindly add interfaces or duplicate NAT rules on an existing VM.

## 3. Start the gNB (terminal 1)

```bash
sudo ./build/nr-gnb -c config/open5gs-gnb.yaml
```

## 4. Start UE1 (terminal 2)

```bash
sudo ./build/nr-ue -c config/ue1.yaml
```

## 5. Start UE2 (terminal 3)

```bash
sudo ./build/nr-ue -c config/ue2.yaml
```


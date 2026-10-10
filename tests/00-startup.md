# 00 — Start the 5G Laboratory

The following commands start the existing installation. They **do not install or overwrite configuration files**. Execute the UERANSIM commands from the directory where the executable and `.yaml` files are accessible. Use the appropriate relative YAML filename for your environment.

## 1. Start dedicated SMF/UPF instances for SST 2 and SST 3

The service unit files for SST 2 and SST 3 are available in [`../configs/systemd/`](../configs/systemd/). If not already installed:

```bash
sudo cp configs/systemd/open5gs-*.service /etc/systemd/system/
sudo systemctl daemon-reload
```

Start the dedicated slice core services:

```bash
sudo systemctl start open5gs-smf2d open5gs-smf3d open5gs-upf2d open5gs-upf3d
```

Check their status:

```bash
systemctl status open5gs-smf2d open5gs-smf3d open5gs-upf2d open5gs-upf3d --no-pager
```

## 2. Set up UPF TUN interfaces, forwarding and traffic control

Run the automated network setup script provided in [`../scripts/setup-network.sh`](../scripts/setup-network.sh):

```bash
sudo ./scripts/setup-network.sh start
```

Verify that interfaces (`ogstun`, `ogstun2`, `ogstun3`), forwarding, and traffic control rules are active:

```bash
sudo ./scripts/setup-network.sh status
```

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


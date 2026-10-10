# Environment Setup and Open5GS Installation

This document describes how to prepare an Ubuntu virtual machine and install the Open5GS 5G Core Network with MongoDB and the Open5GS WebUI.

## 1. Virtual Machine Setup

The laboratory environment is based on **Ubuntu 22.04 LTS**, installed from the official ISO image on a virtual machine.

The virtualization platform is not restricted to a specific hypervisor. In our implementation, **Oracle VirtualBox** was used.

### Requirements

- Ubuntu 22.04 LTS (64-bit)
- A compatible virtualization platform
- Internet connectivity
- Sufficient CPU, RAM and disk space for the 5G Core and additional services
- Administrator privileges (`sudo`)

Download the Ubuntu ISO from:

https://releases.ubuntu.com/22.04/

Create a virtual machine, attach the downloaded ISO image, and complete the standard Ubuntu installation.

After installation, open a terminal inside Ubuntu.

## 2. System Update

Update the package repositories and installed packages:

```bash
sudo apt update
sudo apt upgrade -y
```

Install the basic utilities required for the installation:

```bash
sudo apt install -y software-properties-common curl gnupg ca-certificates
```

## 3. MongoDB Installation

Open5GS uses MongoDB to store subscriber information and related network data.

In this laboratory, MongoDB 8.0 was used.

### 3.1 Import the MongoDB GPG Key

```bash
curl -fsSL https://pgp.mongodb.com/server-8.0.asc | \
sudo gpg --dearmor -o /usr/share/keyrings/mongodb-server-8.0.gpg
```

### 3.2 Add the MongoDB Repository

For Ubuntu 22.04 (Jammy):

```bash
echo "deb [ arch=amd64,arm64 signed-by=/usr/share/keyrings/mongodb-server-8.0.gpg] https://repo.mongodb.org/apt/ubuntu jammy/mongodb-org/8.0 multiverse" | \
sudo tee /etc/apt/sources.list.d/mongodb-org-8.0.list
```

### 3.3 Install MongoDB

```bash
sudo apt update
sudo apt install -y mongodb-org
```

### 3.4 Start MongoDB

```bash
sudo systemctl start mongod
sudo systemctl enable mongod
```

Verify that MongoDB is running:

```bash
sudo systemctl status mongod
```

The service should report `active (running)`.

## 4. Open5GS Installation

Open5GS provides the 5G Core Network Functions required for the simulated Standalone architecture.

### 4.1 Add the Official Open5GS PPA

```bash
sudo add-apt-repository ppa:open5gs/latest
```

### 4.2 Update the Package List

```bash
sudo apt update
```

### 4.3 Install Open5GS

```bash
sudo apt install -y open5gs
```

### 4.4 Verify the Installation

Check the Open5GS configuration directory:

```bash
ls /etc/open5gs/
```

Check the status of the main 5G Core Network Functions:

```bash
sudo systemctl status open5gs-nrfd
sudo systemctl status open5gs-amfd
sudo systemctl status open5gs-smfd
sudo systemctl status open5gs-upfd
```

These services provide network function discovery, access and mobility management, session management, and user-plane forwarding.

Additional Network Functions will be described in the network configuration documentation.

## 5. Open5GS WebUI Installation

The Open5GS WebUI provides a browser-based interface for managing subscriber profiles.

### 5.1 Install Node.js

```bash
sudo apt update
sudo apt install -y ca-certificates curl gnupg
sudo mkdir -p /etc/apt/keyrings
```

Import the NodeSource signing key:

```bash
curl -fsSL https://deb.nodesource.com/gpgkey/nodesource-repo.gpg.key | \
sudo gpg --dearmor -o /etc/apt/keyrings/nodesource.gpg
```

Configure the Node.js 20 repository:

```bash
NODE_MAJOR=20
echo "deb [signed-by=/etc/apt/keyrings/nodesource.gpg] https://deb.nodesource.com/node_$NODE_MAJOR.x nodistro main" | \
sudo tee /etc/apt/sources.list.d/nodesource.list
```

Install Node.js:

```bash
sudo apt update
sudo apt install -y nodejs
```

### 5.2 Install Open5GS WebUI

```bash
curl -fsSL https://open5gs.org/open5gs/assets/webui/install | sudo -E bash -
```

### 5.3 Access and Provisioning via WebUI (Port 9999)

Open a web browser on the Ubuntu machine and navigate to:

```text
http://localhost:9999
```

#### Default Credentials
* **Username:** `admin`
* **Password:** `1423`

*(Change default credentials in production environments).*

#### Single-Subscriber Manual Provisioning
The WebUI allows interactive creation and editing of individual subscriber profiles:

1. Click on **Subscribers** in the top navigation bar.
2. Click the **+** (New Subscriber) button.
3. Fill in the **Subscriber Identity**:
   * **IMSI:** `999700000000001`
4. Configure **Security Credentials**:
   * **K:** `465B5CE8 B199B49F AA5F0A2E E238A6BC`
   * **OPc:** `E8ED289D EBA952E4 283B54E8 8E6183CA`
   * **AMF:** `8000`
   * **SQN:** `000000000000` (or leave default counter)
5. Add the **Three Network Slices**:
   * **Slice 1 (eMBB):**
     * SST: `1`, Check *Default S-NSSAI*.
     * Session APN/DNN: `internet`, Type: `IPv4`.
     * QoS: 5QI `6`, ARP Priority `4`.
     * Session-AMBR: Downlink `1 Gbps` (`1` / `Gbps`), Uplink `100 Mbps` (`100` / `Mbps`).
   * **Slice 2 (URLLC):**
     * Click *+ S-NSSAI*.
     * SST: `2`, Uncheck *Default S-NSSAI*.
     * Session APN/DNN: `internet`, Type: `IPv4`.
     * QoS: 5QI `1`, ARP Priority `1`.
     * Session-AMBR: Downlink `100 Mbps`, Uplink `100 Mbps`.
   * **Slice 3 (MIoT):**
     * Click *+ S-NSSAI*.
     * SST: `3`, Uncheck *Default S-NSSAI*.
     * Session APN/DNN: `internet`, Type: `IPv4`.
     * QoS: 5QI `70`, ARP Priority `12`.
     * Session-AMBR: Downlink `1 Mbps`, Uplink `512 Kbps`.
6. Click **Save** at the bottom of the page.

> **Note:** Manual WebUI entry is recommended for inspection and individual subscriber testing. For automated bulk provisioning, use the included Python script [`../scripts/provision.py`](../scripts/provision.py) or import [`../configs/open5gs/mongodb_subscribers.json`](../configs/open5gs/mongodb_subscribers.json).

## 6. UERANSIM Installation and Build

UERANSIM simulates both the 5G gNodeB (gNB) and User Equipment (UE) terminals over a simulated radio link.

### 6.1 Install Build Dependencies

```bash
sudo apt update
sudo apt install -y make gcc g++ libsctp-dev lksctp-tools iproute2 cmake git
```

### 6.2 Clone and Build UERANSIM (v3.2.6)

Clone UERANSIM into the current user's home directory:

```bash
cd "$HOME"
git clone -b v3.2.6 https://github.com/aligungr/UERANSIM
cd "$HOME/UERANSIM"
make -j"$(nproc)"
```

Verify that the executables were built:

```bash
ls -lh "$HOME/UERANSIM/build/"nr-*
```
*(You should see `nr-gnb`, `nr-ue`, `nr-cli`, and `nr-binder`).*

### 6.3 Deploy Laboratory Configurations

Copy the laboratory configuration files from this repository:

```bash
# 1. Deploy Open5GS core configurations
sudo cp configs/open5gs/*.yaml /etc/open5gs/

# 2. Deploy UERANSIM configurations
mkdir -p "$HOME/UERANSIM/config"
cp configs/ueransim/*.yaml "$HOME/UERANSIM/config/"

# 3. Restart Open5GS Core Services
sudo systemctl restart open5gs-nrfd open5gs-scpd open5gs-amfd open5gs-smfd open5gs-upfd open5gs-ausfd open5gs-udmd open5gs-udrd open5gs-pcfd open5gs-nssfd
```

## 7. Experiment Applications and Tools Installation

The laboratory experiments require additional application servers, softphones, and testing tools:

```bash
sudo apt update
# 1. Performance test and IoT tools
sudo apt install -y iperf3 mosquitto mosquitto-clients

# 2. VoIP PBX and Softphone (SST 2 / URLLC)
sudo apt install -y asterisk twinkle

# 3. Python provisioning dependencies
sudo apt install -y python3-yaml python3-pymongo

# 4. Nextcloud (SST 1 / eMBB)
sudo snap install nextcloud
```

## 8. Installation Verification

Verify that MongoDB is running:

```bash
systemctl is-active mongod
```

List Open5GS services:

```bash
systemctl list-units 'open5gs-*' --type=service
```

Inspect the installed configuration files:

```bash
ls -l /etc/open5gs/
ls -l "$HOME/UERANSIM/config/"
```

Inspect the Open5GS installation version:

```bash
dpkg-query -W open5gs
```

## References

- [Open5GS Official Quickstart](https://open5gs.org/open5gs/docs/guide/01-quickstart/)
- [Open5GS Official Documentation](https://open5gs.org/open5gs/docs/)
- [UERANSIM Repository](https://github.com/aligungr/UERANSIM)
- [Ubuntu 22.04 LTS](https://releases.ubuntu.com/22.04/)
- [MongoDB Documentation](https://www.mongodb.com/docs/)

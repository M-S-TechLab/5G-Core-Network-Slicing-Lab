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

### 5.3 Access the WebUI

Open a web browser on the Ubuntu machine and navigate to:

```text
http://localhost:9999
```

The WebUI allows administrators to configure subscriber profiles, including IMSI, authentication parameters, DNN, network slices, and QoS policies.

Change any default administrative credentials before exposing the WebUI to other systems.

## 6. Installation Verification

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
ls /etc/open5gs/
```

Inspect the Open5GS installation version:

```bash
dpkg-query -W open5gs
```

The laboratory used Open5GS 2.8.0. Installing from the `latest` PPA does not guarantee the same version. For exact reproduction, the installed version should be checked and a compatible version selected.

## 7. Next Steps

After installing Open5GS, the 5G Core Network must be configured to support the laboratory topology.

The following steps are documented separately:

- Configuration of PLMN, TAC, and supported S-NSSAIs.
- Configuration of the AMF, SMFs, and UPFs.
- Setup of three network slices.
- Creation of subscriber profiles in MongoDB.
- Configuration of TUN interfaces, IP forwarding, and NAT.
- Installation and configuration of UERANSIM.
- Validation of UE registration and PDU Session establishment.

## References

- [Open5GS Official Quickstart](https://open5gs.org/open5gs/docs/guide/01-quickstart/)
- [Open5GS Official Documentation](https://open5gs.org/open5gs/docs/)
- [Ubuntu 22.04 LTS](https://releases.ubuntu.com/22.04/)
- [MongoDB Documentation](https://www.mongodb.com/docs/)

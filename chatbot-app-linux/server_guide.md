# Server Build Document

**Project:** AI Question Answering Web Application
**Operating System:** Red Hat Enterprise Linux 9
**Deployment Model:** Multi-VM Linux Infrastructure

---

# 1. Purpose

This document defines the **server build standards and base configuration procedures** for the infrastructure supporting the AI Question Answering Web Application.

The goal is to ensure that all servers are built in a **consistent, secure, and minimal configuration**, aligned with production deployment practices.

This document covers:

* operating system installation standards
* base system configuration
* network configuration
* security baseline
* package installation
* service preparation

All servers in this environment use **Red Hat Enterprise Linux 9 Minimal**.

---

# 2. Server Inventory

| Server | Role                    | Hostname    |
| ------ | ----------------------- | ----------- |
| VM-1   | Nginx Reverse Proxy     | proxy-01    |
| VM-2   | Frontend Application    | frontend-01 |
| VM-3   | Backend API             | backend-01  |
| VM-4   | PostgreSQL Database     | db-01       |
| VM-5   | Monitoring / Operations | ops-01      |

---

# 3. Base Operating System

All servers are installed with:

**RHEL 9 Minimal Installation**

The minimal installation profile ensures:

* reduced attack surface
* minimal background services
* lower memory footprint
* better performance
* easier patch management

No GUI components are installed.

---

# 4. System Requirements

### Minimum VM Specifications

| Role          | vCPU | RAM  | Disk  |
| ------------- | ---- | ---- | ----- |
| Reverse Proxy | 1    | 1 GB | 20 GB |
| Frontend      | 1    | 2 GB | 20 GB |
| Backend API   | 2    | 2 GB | 30 GB |
| Database      | 2    | 4 GB | 40 GB |
| Monitoring    | 2    | 2 GB | 30 GB |

---

# 5. Initial OS Configuration

After installing RHEL 9 minimal, the following steps must be completed on **all servers**.

---

# 6. Hostname Configuration

Each server must have a clear hostname aligned with its role.

Example:

```
hostnamectl set-hostname proxy-01
hostnamectl set-hostname frontend-01
hostnamectl set-hostname backend-01
hostnamectl set-hostname db-01
hostnamectl set-hostname ops-01
```

Verify hostname:

```
hostnamectl
```

---

# 7. Static Network Configuration

Each VM should have a static IP address.

Example configuration:

```
nmcli connection modify eth0 ipv4.method manual
nmcli connection modify eth0 ipv4.addresses 10.0.0.10/24
nmcli connection modify eth0 ipv4.gateway 10.0.0.1
nmcli connection modify eth0 ipv4.dns 8.8.8.8
nmcli connection up eth0
```

Verify connectivity:

```
ip a
ping 8.8.8.8
```

---

# 8. Local Host Resolution

Add internal hostnames for application servers.

Edit:

```
/etc/hosts
```

Example:

```
10.0.0.10 proxy-01
10.0.0.20 frontend-01
10.0.0.30 backend-01
10.0.0.40 db-01
10.0.0.50 ops-01
```

This allows services to communicate using hostnames.

---

# 9. System Updates

All systems must be updated immediately after installation.

```
dnf update -y
```

Reboot if kernel updates are applied.

```
reboot
```

---

# 10. Base Utility Packages

Install common administration tools on all servers.

```
dnf install -y \
vim \
wget \
curl \
git \
net-tools \
bind-utils \
lsof \
htop \
tar \
unzip
```

These tools assist with diagnostics and operational management.

---

# 11. Time Synchronization

Ensure accurate time across all servers.

Enable **chronyd**.

```
systemctl enable chronyd
systemctl start chronyd
```

Verify:

```
chronyc tracking
```

Time synchronization is critical for:

* logs
* database timestamps
* monitoring systems

---

# 12. Firewall Configuration

RHEL uses **firewalld**.

Enable and start the firewall.

```
systemctl enable firewalld
systemctl start firewalld
```

Verify:

```
firewall-cmd --state
```

Firewall rules will be applied later per server role.

---

# 13. SSH Hardening

Basic SSH security measures must be implemented.

Edit:

```
/etc/ssh/sshd_config
```

Recommended changes:

```
PermitRootLogin no
PasswordAuthentication yes
MaxAuthTries 3
```

Restart SSH service:

```
systemctl restart sshd
```

---

# 14. User Management

Create a dedicated administrative user.

Example:

```
useradd devopsadmin
passwd devopsadmin
```

Grant sudo access:

```
usermod -aG wheel devopsadmin
```

Verify sudo:

```
su - devopsadmin
sudo whoami
```

Root login should be avoided for daily administration.

---

# 15. SELinux Configuration

SELinux should remain **enabled and enforcing**.

Check status:

```
getenforce
```

Expected output:

```
Enforcing
```

If disabled, enable it by editing:

```
/etc/selinux/config
```

```
SELINUX=enforcing
```

---

# 16. Log Management

System logs are managed by **systemd journal**.

View logs:

```
journalctl
```

Check service logs:

```
journalctl -u nginx
journalctl -u postgresql
```

Log visibility is essential for debugging.

---

# 17. Disk Layout

Minimal disk layout is recommended.

Example partition structure:

```
/      15 GB
/var   10 GB
/tmp   2 GB
swap   2 GB
```

For database server:

```
/var/lib/pgsql   separate volume recommended
```

This improves database performance and manageability.

---

# 18. Role-Specific Package Preparation

After base configuration, servers will install packages according to their role.

| Server      | Packages            |
| ----------- | ------------------- |
| proxy-01    | nginx               |
| frontend-01 | nodejs, npm         |
| backend-01  | python3, pip        |
| db-01       | postgresql-server   |
| ops-01      | prometheus, grafana |

Detailed installation procedures are covered in the **Deployment Runbook**.

---

# 19. Connectivity Validation

Before deploying application components, verify connectivity between servers.

Example tests:

### Test proxy to frontend

```
ping frontend-01
```

### Test backend to database

```
ping db-01
```

### Test internet connectivity

```
curl https://api.openai.com
```

Connectivity must be confirmed before proceeding.

---

# 20. System Validation Checklist

Before moving to application deployment, verify the following on all servers:

| Check                | Command                    |
| -------------------- | -------------------------- |
| Hostname configured  | `hostnamectl`              |
| Static IP configured | `ip a`                     |
| System updated       | `dnf update`               |
| Firewall running     | `firewall-cmd --state`     |
| SSH hardened         | `sshd -T`                  |
| Chrony running       | `systemctl status chronyd` |
| SELinux enforcing    | `getenforce`               |

---

# 21. Build Completion Criteria

A server is considered ready for application deployment when:

* RHEL 9 minimal is installed
* hostname and network configuration are complete
* system updates are applied
* administrative access is configured
* firewall is enabled
* time synchronization is active
* connectivity with other infrastructure components is verified

Once these steps are completed, the infrastructure is ready for the **Application Deployment Phase**.

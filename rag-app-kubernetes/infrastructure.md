# RAG Application on Kubernetes — Infrastructure Requirements

## Overview

This project demonstrates deployment of a real-world microservices-based RAG (Retrieval Augmented Generation) application on Kubernetes using GitOps and CI/CD practices.

The environment includes:

* Jenkins for CI automation
* Kubernetes for container orchestration
* MetalLB for LoadBalancer IP allocation
* Multiple microservices for ingestion and querying
* Vector database integration
* GitOps-ready architecture with Argo CD compatibility

---

# Infrastructure Requirements

## 1. Jenkins Server VM

A dedicated Ubuntu VM is required for CI/CD automation.

### Purpose

* Run Jenkins
* Build container images
* Push images to registry
* Trigger GitOps workflow
* Execute CI pipelines

---

### Recommended Specifications

| Resource | Recommended           |
| -------- | --------------------- |
| OS       | Ubuntu 22.04 LTS      |
| RAM      | 2–4 GB                |
| CPU      | 2 vCPUs               |
| Storage  | 20 GB                 |
| Network  | Internet + LAN access |

---

### Required Software

* Jenkins
* Docker or Podman
* Git
* kubectl
* Helm (optional)

---

# 2. Kubernetes Cluster

A Kubernetes cluster is required to host the RAG application microservices.

---

## Minimum Available Resources

| Resource           | Requirement        |
| ------------------ | ------------------ |
| Available RAM      | 4–6 GB             |
| Available CPUs     | 2–4 CPUs           |
| Available Storage  | 15 GB              |
| Kubernetes Version | v1.28+ recommended |

---

## Cluster Components

The cluster will host:

| Component                 | Purpose                             |
| ------------------------- | ----------------------------------- |
| Frontend Service          | User GUI                            |
| Ingestor Service          | PDF ingestion and chunking          |
| Query Service             | User query processing               |
| Qdrant                    | Vector database                     |
| MetalLB                   | External LoadBalancer IP allocation |
| Argo CD (optional)        | GitOps deployments                  |
| Metrics Server (optional) | Resource metrics                    |

---

# 3. IPv4 Address Requirements

The environment requires multiple available IPv4 addresses from the local router/network.

---

## Required IP Addresses

| Usage             | Count    |
| ----------------- | -------- |
| Kubernetes Nodes  | Multiple |
| MetalLB Pool      | 4–6 IPs  |
| External Services | Optional |

---

## Why Multiple IPs Are Needed

MetalLB uses a pool of IP addresses to expose Kubernetes services externally using `LoadBalancer` services.

Example services:

* Argo CD UI
* Frontend GUI
* Monitoring dashboards
* Additional APIs

---

## Example IP Pool

```text
192.168.1.240 - 192.168.1.245
```

These IPs should:

* Belong to the same subnet
* Be unused by DHCP/router
* Be reachable from the local network

---

# 4. Workstation / Manager Node

A workstation or management VM is required for cluster administration.

---

## Purpose

Used for:

* Running kubectl commands
* Managing Argo CD
* Applying Kubernetes manifests
* Accessing cluster APIs
* Troubleshooting deployments

---

## Required Tools

| Tool          | Purpose               |
| ------------- | --------------------- |
| kubectl       | Kubernetes management |
| Git           | Source control        |
| Helm          | Helm deployments      |
| Argo CD CLI   | GitOps operations     |
| Docker/Podman | Image testing         |

---

## Supported Operating Systems

* Ubuntu
* macOS
* Windows with WSL2
* RHEL/Rocky Linux

---

# Recommended Deployment Topology

| Node                 | Role                  |
| -------------------- | --------------------- |
| Jenkins VM           | CI/CD Server          |
| Kubernetes Master    | Control Plane         |
| Kubernetes Worker(s) | Application Workloads |
| Workstation          | Cluster Management    |

---

# Network Requirements

## Required Connectivity

| Source       | Destination        | Purpose             |
| ------------ | ------------------ | ------------------- |
| Jenkins      | Container Registry | Push images         |
| Jenkins      | Git Repository     | Pull source code    |
| Workstation  | Kubernetes API     | Cluster management  |
| User Browser | MetalLB IPs        | Access applications |

---

# Storage Recommendations

## Persistent Storage Suggested For

| Component | Persistent Storage |
| --------- | ------------------ |
| Qdrant    | Yes                |
| Jenkins   | Yes                |
| Argo CD   | Recommended        |

---

# Optional Components

The following can also be deployed:

| Component          | Purpose               |
| ------------------ | --------------------- |
| Argo CD            | GitOps automation     |
| Prometheus         | Metrics collection    |
| Grafana            | Monitoring dashboards |
| Ingress Controller | HTTP routing          |
| Cert Manager       | TLS certificates      |

---

# Estimated Total Lab Requirements

| Resource            | Suggested Capacity |
| ------------------- | ------------------ |
| Total RAM           | 8–12 GB            |
| Total CPUs          | 4–6 CPUs           |
| Total Storage       | 40–60 GB           |
| Free IPv4 Addresses | 4–6                |

---

# Final Notes

This infrastructure is designed for:

* Learning Kubernetes GitOps workflows
* Deploying real-world AI/RAG applications
* CI/CD demonstrations
* Multi-service Kubernetes deployments
* Argo CD integration
* Enterprise-style DevOps training environments

The environment can run on:

* Physical servers
* Nested virtualization
* VMware Workstation
* Proxmox
* VirtualBox
* Cloud VMs
* Bare metal Kubernetes clusters

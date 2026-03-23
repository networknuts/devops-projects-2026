# Installation and Configuration Document

**Project:** AI Question Answering Web Application
**Operating System:** Red Hat Enterprise Linux 9
**Deployment Model:** Multi-VM Infrastructure

---

# 1. Purpose

This document defines the **installation and configuration procedures** for all software components required to run the AI Question Answering Web Application.

The document assumes that:

* all servers are built using **RHEL 9 Minimal**
* base system configuration has already been completed
* network connectivity between servers is operational

This document focuses specifically on:

* installing required software packages
* configuring application services
* preparing runtime environments
* configuring inter-service connectivity

---

# 2. Infrastructure Overview

| Server | Role                    | Hostname    |
| ------ | ----------------------- | ----------- |
| VM-1   | Reverse Proxy           | proxy-01    |
| VM-2   | Frontend Server         | frontend-01 |
| VM-3   | Backend API             | backend-01  |
| VM-4   | PostgreSQL Database     | db-01       |
| VM-5   | Monitoring / Operations | ops-01      |

---

# 3. Installation Order

The installation should follow the order below to ensure dependencies are satisfied.

1. Database Server
2. Backend API Server
3. Frontend Server
4. Reverse Proxy Server
5. Monitoring Server

---

# 4. Database Server Installation (VM-4)

## 4.1 Install PostgreSQL

Install PostgreSQL server packages.

```bash
dnf install -y postgresql-server postgresql
```

---

## 4.2 Initialize the Database

```bash
postgresql-setup --initdb
```

---

## 4.3 Enable and Start PostgreSQL

```bash
systemctl enable postgresql
systemctl start postgresql
```

Verify service status.

```bash
systemctl status postgresql
```

---

## 4.4 Configure Database Listening Address

Edit the PostgreSQL configuration file.

```
/var/lib/pgsql/data/postgresql.conf
```

Modify:

```
listen_addresses = '*'
```

---

## 4.5 Configure Database Authentication

Edit:

```
/var/lib/pgsql/data/pg_hba.conf
```

Add entry for backend server.

Example:

```
host    chatdb    chatuser    10.0.0.30/32    md5
```

---

## 4.6 Restart PostgreSQL

```bash
systemctl restart postgresql
```

---

## 4.7 Create Application Database

Switch to postgres user.

```bash
su - postgres
```

Create database user.

```bash
createuser chatuser
```

Create database.

```bash
createdb chatdb
```

Set password.

```sql
psql
ALTER USER chatuser WITH PASSWORD 'strongpassword';
\q
```

---

## 4.8 Firewall Configuration

Allow backend server access.

```bash
firewall-cmd --permanent --add-port=5432/tcp
firewall-cmd --reload
```

---

# 5. Backend API Installation (VM-3)

## 5.1 Install Python and Development Tools

```bash
dnf install -y python3 python3-pip python3-devel
```

Verify version.

```bash
python3 --version
```

---

## 5.2 Create Application Directory

```bash
mkdir -p /opt/chatapp/backend
```

---

## 5.3 Create Python Virtual Environment

```bash
python3 -m venv /opt/chatapp/backend/venv
```

Activate environment.

```bash
source /opt/chatapp/backend/venv/bin/activate
```

---

## 5.4 Install Application Dependencies

```bash
pip install fastapi
pip install uvicorn
pip install openai
pip install psycopg2-binary
pip install python-dotenv
pip install gunicorn
```

---

## 5.5 Application Environment Configuration

Create environment configuration file.

```
/opt/chatapp/backend/.env
```

Example contents:

```
OPENAI_API_KEY=your_openai_api_key
DATABASE_URL=postgresql://chatuser:strongpassword@db-01:5432/chatdb
```

Ensure correct permissions.

```bash
chmod 600 /opt/chatapp/backend/.env
```

---

## 5.6 Firewall Configuration

Allow API access from frontend server.

```bash
firewall-cmd --permanent --add-port=8000/tcp
firewall-cmd --reload
```

---

# 6. Frontend Installation (VM-2)

## 6.1 Install Node.js

Enable Node.js repository.

```bash
dnf module enable nodejs:18 -y
```

Install Node.js.

```bash
dnf install -y nodejs
```

Verify installation.

```bash
node -v
npm -v
```

---

## 6.2 Create Application Directory

```bash
mkdir -p /opt/chatapp/frontend
```

---

## 6.3 Install Frontend Dependencies

Navigate to application directory.

```bash
cd /opt/chatapp/frontend
```

Install dependencies.

```bash
npm install
```

---

## 6.4 Configure Backend API Endpoint

Ensure the frontend application points to the backend API.

Example configuration:

```
API_URL=http://backend-01:8000
```

---

## 6.5 Start Frontend Application

Run the Node.js application.

```bash
npm start
```

The application should listen on port:

```
3000
```

---

## 6.6 Firewall Configuration

Allow reverse proxy access.

```bash
firewall-cmd --permanent --add-port=3000/tcp
firewall-cmd --reload
```

---

# 7. Reverse Proxy Installation (VM-1)

## 7.1 Install Nginx

```bash
dnf install -y nginx
```

---

## 7.2 Enable and Start Service

```bash
systemctl enable nginx
systemctl start nginx
```

Verify status.

```bash
systemctl status nginx
```

---

## 7.3 Configure Reverse Proxy

Create configuration file.

```
/etc/nginx/conf.d/chatapp.conf
```

Example configuration:

```nginx
server {
    listen 80;

    location / {
        proxy_pass http://frontend-01:3000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    location /api/ {
        proxy_pass http://backend-01:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

---

## 7.4 Test Configuration

```bash
nginx -t
```

---

## 7.5 Reload Nginx

```bash
systemctl reload nginx
```

---

## 7.6 Firewall Configuration

Allow web traffic.

```bash
firewall-cmd --permanent --add-service=http
firewall-cmd --permanent --add-service=https
firewall-cmd --reload
```

---

# 8. Monitoring Server Installation (VM-5)

## 8.1 Install Prometheus

Create Prometheus user.

```bash
useradd --no-create-home --shell /bin/false prometheus
```

Download Prometheus binary.

```bash
wget https://github.com/prometheus/prometheus/releases/latest/download/prometheus-linux-amd64.tar.gz
```

Extract files.

```bash
tar -xvf prometheus-linux-amd64.tar.gz
```

Move binaries.

```bash
mv prometheus /usr/local/bin/
mv promtool /usr/local/bin/
```

---

## 8.2 Configure Prometheus Targets

Edit configuration file.

```
/etc/prometheus/prometheus.yml
```

Add servers as scrape targets.

Example:

```
scrape_configs:
  - job_name: servers
    static_configs:
      - targets:
        - proxy-01:9100
        - frontend-01:9100
        - backend-01:9100
        - db-01:9100
```

---

## 8.3 Install Node Exporter on All Servers

Download node exporter.

```bash
dnf install -y node_exporter
```

Enable service.

```bash
systemctl enable node_exporter
systemctl start node_exporter
```

---

# 9. Service Validation

Verify that each component is reachable.

## Backend API

```bash
curl http://backend-01:8000
```

---

## Frontend

```bash
curl http://frontend-01:3000
```

---

## Database Connectivity

```bash
psql -h db-01 -U chatuser -d chatdb
```

---

## Reverse Proxy

Access the application through a browser:

```
http://proxy-01
```

---

# 10. Installation Completion Criteria

The installation is considered complete when:

* PostgreSQL database is operational
* backend API service starts successfully
* frontend application loads correctly
* Nginx reverse proxy routes requests properly
* OpenAI API communication is functioning
* monitoring services are collecting metrics

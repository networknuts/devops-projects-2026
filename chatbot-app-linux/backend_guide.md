# Backend Setup Guide (FastAPI)

This document describes how to set up, run, and manage the FastAPI backend service for the AI Question Answering application.

---

# 1. Create Application Directory

Create the backend directory structure:

```bash
mkdir -p /opt/chatapp/backend
cd /opt/chatapp/backend
```

Ensure proper ownership (recommended for production):

```bash
chown -R chatapp:chatapp /opt/chatapp
```

---

# 2. Create Python Virtual Environment

Create a virtual environment:

```bash
python3 -m venv venv
```

Activate the environment:

```bash
source venv/bin/activate
```

Upgrade pip:

```bash
pip install --upgrade pip
```

---

# 3. Create `.env` File

Create an environment configuration file:

```bash
vi /opt/chatapp/backend/.env
```

Example:

```env
OPENAI_API_KEY=your_openai_api_key
DATABASE_URL=postgresql://chatuser:strongpassword@db-01:5432/chatdb
OPENAI_MODEL=gpt-4.1-mini
```

Set secure permissions:

```bash
chmod 600 /opt/chatapp/backend/.env
```

---

# 4. Create `requirements.txt`

Create the dependency file:

```bash
vi /opt/chatapp/backend/requirements.txt
```

Example contents:

```txt
fastapi
uvicorn
gunicorn
psycopg2-binary
python-dotenv
openai==1.30.0
httpx==0.27.0
```

Install dependencies:

```bash
pip install -r requirements.txt
```

---

# 5. Test Application Locally

Run the FastAPI server:

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

---

## Health Check

```bash
curl http://localhost:8000/health
```

Expected output:

```json
{"status":"ok"}
```

---

## Test Chat Endpoint

```bash
curl -X POST http://localhost:8000/chat \
-H "Content-Type: application/json" \
-d '{"question":"What is DevOps?"}'
```

---

# 6. Create systemd Service

Create a systemd service file:

```bash
vi /etc/systemd/system/chatapp-backend.service
```

---

## Service Configuration

```ini
[Unit]
Description=ChatApp FastAPI Backend
After=network.target

[Service]
User=chatapp
WorkingDirectory=/opt/chatapp/backend

EnvironmentFile=/opt/chatapp/backend/.env

ExecStart=/opt/chatapp/backend/venv/bin/gunicorn \
    -k uvicorn.workers.UvicornWorker \
    app.main:app \
    --bind 0.0.0.0:8000 \
    --workers 2

Restart=always
RestartSec=5

StandardOutput=journal
StandardError=journal

LimitNOFILE=65535

[Install]
WantedBy=multi-user.target
```

---

## Reload systemd

```bash
systemctl daemon-reexec
systemctl daemon-reload
```

---

## Start Service

```bash
systemctl start chatapp-backend
```

---

## Enable Auto Start

```bash
systemctl enable chatapp-backend
```

---

## Check Status

```bash
systemctl status chatapp-backend
```

---

## View Logs

```bash
journalctl -u chatapp-backend -f
```

---

# Final Validation

Verify that the backend is accessible:

```bash
curl http://localhost:8000/health
```

---

# Summary

This setup ensures:

* isolated Python environment
* secure handling of API keys
* reproducible dependency installation
* production-ready service management
* centralized logging via systemd

The backend is now ready for integration with the frontend and reverse proxy.

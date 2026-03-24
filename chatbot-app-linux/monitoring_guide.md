# Nginx Monitoring with Prometheus

## 📌 1. Enable Nginx `stub_status`

### Step 1: Update Nginx Configuration

Edit your Nginx config (e.g., `/etc/nginx/conf.d/ai-chat-app.conf`) and add the following block **inside the `server {}` section**:

```nginx
location /nginx_status {
    stub_status;

    # Allow only local access and Prometheus server
    allow 127.0.0.1;
    allow <PROMETHEUS_SERVER_IP>;
    deny all;
}
```

> Replace `<PROMETHEUS_SERVER_IP>` with your Prometheus server IP.

---

### Step 2: Validate and Reload Nginx

```bash
nginx -t
systemctl reload nginx
```

---

### Step 3: Test Endpoint

```bash
curl http://localhost/nginx_status
```

Expected output:

```
Active connections: 2
server accepts handled requests
 100 100 200
Reading: 0 Writing: 1 Waiting: 1
```

---

## 📌 2. Deploy Nginx Prometheus Exporter

The exporter converts Nginx metrics into Prometheus format.

---

### Option A: Using Docker (Recommended)

```bash
docker run -d \
  --name nginx-exporter \
  -p 9113:9113 \
  nginx/nginx-prometheus-exporter \
  --nginx.scrape-uri http://localhost/nginx_status
```

---

### Option B: Using Binary

```bash
wget https://github.com/nginxinc/nginx-prometheus-exporter/releases/latest/download/nginx-prometheus-exporter-linux-amd64.tar.gz

tar -xvf nginx-prometheus-exporter-linux-amd64.tar.gz
cd nginx-prometheus-exporter*

./nginx-prometheus-exporter \
  --nginx.scrape-uri http://localhost/nginx_status
```

---

### Step 2: Verify Exporter

```bash
curl http://localhost:9113/metrics
```

Example output:

```
nginx_connections_active 2
nginx_connections_reading 0
nginx_connections_writing 1
nginx_connections_waiting 1
nginx_http_requests_total 1200
```

---

## 📌 3. Configure Prometheus Scraping

Edit your `prometheus.yml`:

```yaml
scrape_configs:
  - job_name: 'nginx'
    static_configs:
      - targets:
          - 'proxy-01:9113'
```

> Replace `proxy-01` with your Nginx server hostname/IP.

---

### Reload Prometheus

```bash
systemctl restart prometheus
```

---

## 📊 Useful Prometheus Queries

### 🔹 Active Connections (Real-time)

```promql
nginx_connections_active
```

### 🔹 Requests Per Second

```promql
rate(nginx_http_requests_total[1m])
```

### 🔹 Total Requests (Last 5 Minutes)

```promql
increase(nginx_http_requests_total[5m])
```

### 🔹 Peak Connections (Last 5 Minutes)

```promql
max_over_time(nginx_connections_active[5m])
```

---

## 🔐 Security Best Practices

* Never expose `/nginx_status` publicly
* Restrict access using `allow` and `deny`
* Keep exporter port (9113) internal or firewall-restricted

---

## 🧠 Architecture Overview

```
Client → Nginx → FastAPI Backend
           ↓
     /nginx_status
           ↓
Nginx Prometheus Exporter (9113)
           ↓
        Prometheus
           ↓
         Grafana
```

---

## ✅ Summary

| Component     | Purpose                               |
| ------------- | ------------------------------------- |
| `stub_status` | Provides raw Nginx metrics            |
| Exporter      | Converts metrics to Prometheus format |
| Prometheus    | Collects and stores metrics           |
| Grafana       | Visualization (optional)              |

---

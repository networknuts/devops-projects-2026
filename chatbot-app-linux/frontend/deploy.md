# Deployment Guide — AI Question Answering App (RHEL 9.0)

This guide covers a three-VM setup:

| VM | Role | Example IP |
|---|---|---|
| **Frontend Build Server** | Node.js build only | `10.0.0.10` |
| **API Server** | Backend API (already deployed) | `10.0.0.30` |
| **Nginx Server** | Reverse proxy, serves static files | `10.0.0.20` |

Replace the example IPs with your actual values throughout.

---

# Frontend Build Server

## 1. Install Node.js (v20 LTS)

```bash
sudo dnf module disable nodejs -y
curl -fsSL https://rpm.nodesource.com/setup_20.x | sudo bash -
sudo dnf install -y nodejs

node -v   # v20.x.x
npm -v
```

## 2. Create Application Directory

```bash
sudo mkdir -p /opt/ai-chat-app

# Set ownership (replace 'deployer' with your deploy user)
sudo chown -R deployer:deployer /opt/ai-chat-app
```

## 3. Copy Application Files & Build

```bash
# Copy project files to the build server (from your local machine)
# scp -r ./* deployer@10.0.0.10:/opt/ai-chat-app/

# On the build server
cd /opt/ai-chat-app

npm install
npm run build

# The built files are in /opt/ai-chat-app/dist/
# They will be copied to the Nginx server in a later step.
```

---

# Nginx Server

## 4. Install Nginx

```bash
sudo dnf install -y nginx
sudo systemctl enable nginx
```

## 5. Create Web Root & Copy Built Files

```bash
sudo mkdir -p /var/www/ai-chat-app
sudo chown -R nginx:nginx /var/www/ai-chat-app

# Copy built files from the build server
scp -r deployer@10.0.0.10:/opt/ai-chat-app/dist/* /tmp/ai-chat-build/
sudo cp -r /tmp/ai-chat-build/* /var/www/ai-chat-app/
sudo chown -R nginx:nginx /var/www/ai-chat-app
```

## 6. Create the API Config File

Create `/var/www/ai-chat-app/config.js` pointing to the Nginx server itself (which will proxy to the API):

```bash
sudo tee /var/www/ai-chat-app/config.js > /dev/null << 'EOF'
window.APP_CONFIG = {
  API_BASE_URL: "/api"
};
EOF
```

## 7. Configure Nginx

Create `/etc/nginx/conf.d/ai-chat-app.conf`:

```nginx
server {
    listen       80;
    server_name  your-domain.com;

    root /var/www/ai-chat-app;
    index index.html;

    # SPA — route all paths to index.html
    location / {
        try_files $uri $uri/ /index.html;
    }

    # Reverse-proxy API requests to the API server
    location /api/ {
        proxy_pass         http://10.0.0.30:8000/;
        proxy_set_header   Host $host;
        proxy_set_header   X-Real-IP $remote_addr;
        proxy_set_header   X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_read_timeout 120s;
    }

    # Cache static assets
    location ~* \.(js|css|png|jpg|jpeg|gif|ico|svg|woff2?)$ {
        expires 30d;
        add_header Cache-Control "public, immutable";
    }
}
```

Test and reload:

```bash
sudo nginx -t
sudo systemctl restart nginx
```

## 8. Open Firewall Ports (Nginx Server)

```bash
# HTTP
sudo firewall-cmd --permanent --add-service=http

# HTTPS (if using TLS)
sudo firewall-cmd --permanent --add-service=https

sudo firewall-cmd --reload
sudo firewall-cmd --list-all
```

## 9. SELinux Permissions (Nginx Server)

```bash
# Allow Nginx to connect to the upstream API server
sudo setsebool -P httpd_can_network_connect 1

# Label the web root
sudo semanage fcontext -a -t httpd_sys_content_t "/var/www/ai-chat-app(/.*)?"
sudo restorecon -Rv /var/www/ai-chat-app
```

## 10. (Optional) Enable HTTPS with Let's Encrypt

```bash
sudo dnf install -y certbot python3-certbot-nginx
sudo certbot --nginx -d your-domain.com
sudo systemctl enable certbot-renew.timer
```

---

## Quick Verification Checklist

### Frontend Build Server

| Check | Command |
|---|---|
| Node.js installed | `node -v` |
| Build succeeded | `ls /opt/ai-chat-app/dist/index.html` |

### Nginx Server

| Check | Command |
|---|---|
| Nginx running | `systemctl status nginx` |
| Static files present | `ls /var/www/ai-chat-app/index.html` |
| Proxy to API works | `curl -s http://localhost/api/health` |
| Site loads | `curl -I http://localhost` |
| SELinux OK | `getsebool httpd_can_network_connect` |

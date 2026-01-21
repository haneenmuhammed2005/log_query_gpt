# 🚀 Deployment Guide

Complete guide for deploying ICS-LogQueryGPT in various environments.

---

## 📋 Table of Contents

- [Local Development](#-local-development)
- [Docker Deployment](#-docker-deployment)
- [Production Deployment](#-production-deployment)
- [Cloud Deployment](#-cloud-deployment)
- [Security Considerations](#-security-considerations)
- [Monitoring & Maintenance](#-monitoring--maintenance)

---

## 💻 Local Development

### Quick Setup

```bash
# Clone and setup
git clone https://github.com/yourusername/ICS-LogQueryGPT.git
cd ICS-LogQueryGPT

# Create environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Setup Ollama
ollama pull llama3.1:8b

# Prepare data
python src/preprocessing/download_data.py
python src/preprocessing/process_all_data.py
python src/embeddings/enhanced_embedder.py

# Launch
streamlit run src/ui/enhanced_app_ollama.py
```

---

## 🐳 Docker Deployment

### Option 1: Docker Compose (Recommended)

**File: `docker-compose.yml`**

```yaml
version: '3.8'

services:
  ics-logquery:
    build: .
    container_name: ics-logquery-app
    ports:
      - "8501:8501"      # Streamlit
      - "11434:11434"    # Ollama
    volumes:
      - ./data:/app/data
      - ollama-data:/root/.ollama
      - ./logs:/app/logs
    environment:
      - STREAMLIT_SERVER_PORT=8501
      - STREAMLIT_SERVER_ADDRESS=0.0.0.0
      - OLLAMA_HOST=http://localhost:11434
      - PYTHONUNBUFFERED=1
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8501/_stcore/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s

volumes:
  ollama-data:
    driver: local
```

**File: `Dockerfile`**

```dockerfile
FROM python:3.10-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    git \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Install Ollama
RUN curl -fsSL https://ollama.com/install.sh | sh

# Set working directory
WORKDIR /app

# Copy requirements first (for caching)
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create necessary directories
RUN mkdir -p data/raw data/processed_logs data/embeddings logs

# Download and setup model
RUN ollama serve & \
    sleep 5 && \
    ollama pull llama3.1:8b

# Expose ports
EXPOSE 8501 11434

# Create startup script
RUN echo '#!/bin/bash\n\
ollama serve &\n\
sleep 5\n\
streamlit run src/ui/enhanced_app_ollama.py\n\
' > /app/start.sh && chmod +x /app/start.sh

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
  CMD curl -f http://localhost:8501/_stcore/health || exit 1

# Start application
CMD ["/app/start.sh"]
```

**Deploy:**

```bash
# Build and start
docker-compose up -d

# View logs
docker-compose logs -f

# Stop
docker-compose down

# Rebuild after changes
docker-compose up -d --build
```

### Option 2: Multi-Stage Dockerfile (Optimized)

**File: `Dockerfile.optimized`**

```dockerfile
# Stage 1: Builder
FROM python:3.10-slim as builder

WORKDIR /app

# Install build dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Install Python packages
COPY requirements.txt .
RUN pip install --no-cache-dir --user -r requirements.txt

# Stage 2: Runtime
FROM python:3.10-slim

# Install runtime dependencies
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install Ollama
RUN curl -fsSL https://ollama.com/install.sh | sh

# Copy Python packages from builder
COPY --from=builder /root/.local /root/.local

# Set PATH
ENV PATH=/root/.local/bin:$PATH

WORKDIR /app

# Copy application
COPY . .

# Create directories
RUN mkdir -p data/raw data/processed_logs data/embeddings logs

# Setup Ollama model
RUN ollama serve & sleep 5 && ollama pull llama3.1:8b

EXPOSE 8501 11434

# Startup script
COPY docker-entrypoint.sh /
RUN chmod +x /docker-entrypoint.sh

ENTRYPOINT ["/docker-entrypoint.sh"]
```

**File: `docker-entrypoint.sh`**

```bash
#!/bin/bash
set -e

# Start Ollama in background
echo "Starting Ollama..."
ollama serve &

# Wait for Ollama to be ready
echo "Waiting for Ollama to be ready..."
sleep 10

# Verify model
ollama list

# Start Streamlit
echo "Starting Streamlit..."
exec streamlit run src/ui/enhanced_app_ollama.py \
    --server.port=8501 \
    --server.address=0.0.0.0
```

---

## 🏭 Production Deployment

### Prerequisites

- Linux server (Ubuntu 20.04+ recommended)
- 16GB+ RAM
- 50GB+ storage
- Domain name (optional)
- SSL certificate (optional)

### Step 1: Server Setup

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install dependencies
sudo apt install -y python3-pip python3-venv git nginx

# Create application user
sudo useradd -m -s /bin/bash icslog
sudo su - icslog

# Clone repository
git clone https://github.com/yourusername/ICS-LogQueryGPT.git
cd ICS-LogQueryGPT

# Setup virtual environment
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### Step 2: Install Ollama

```bash
# Install Ollama
curl -fsSL https://ollama.com/install.sh | sh

# Pull model
ollama pull llama3.1:8b

# Verify
ollama list
```

### Step 3: Systemd Service

**File: `/etc/systemd/system/ollama.service`**

```ini
[Unit]
Description=Ollama Service
After=network.target

[Service]
Type=simple
User=icslog
Environment="OLLAMA_HOST=0.0.0.0:11434"
ExecStart=/usr/local/bin/ollama serve
Restart=always
RestartSec=3

[Install]
WantedBy=multi-user.target
```

**File: `/etc/systemd/system/ics-logquery.service`**

```ini
[Unit]
Description=ICS-LogQueryGPT Application
After=network.target ollama.service
Requires=ollama.service

[Service]
Type=simple
User=icslog
WorkingDirectory=/home/icslog/ICS-LogQueryGPT
Environment="PATH=/home/icslog/ICS-LogQueryGPT/venv/bin"
ExecStart=/home/icslog/ICS-LogQueryGPT/venv/bin/streamlit run src/ui/enhanced_app_ollama.py --server.port=8501 --server.address=0.0.0.0
Restart=always
RestartSec=3

[Install]
WantedBy=multi-user.target
```

**Enable and Start:**

```bash
sudo systemctl daemon-reload
sudo systemctl enable ollama
sudo systemctl enable ics-logquery
sudo systemctl start ollama
sudo systemctl start ics-logquery

# Check status
sudo systemctl status ollama
sudo systemctl status ics-logquery
```

### Step 4: Nginx Reverse Proxy

**File: `/etc/nginx/sites-available/ics-logquery`**

```nginx
server {
    listen 80;
    server_name your-domain.com;

    # Redirect to HTTPS
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name your-domain.com;

    # SSL Configuration
    ssl_certificate /etc/letsencrypt/live/your-domain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/your-domain.com/privkey.pem;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;

    # Security headers
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header Referrer-Policy "no-referrer-when-downgrade" always;

    # Streamlit proxy
    location / {
        proxy_pass http://localhost:8501;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_read_timeout 86400;
    }

    # WebSocket support
    location /_stcore/stream {
        proxy_pass http://localhost:8501/_stcore/stream;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_read_timeout 86400;
    }

    # Access logs
    access_log /var/log/nginx/ics-logquery-access.log;
    error_log /var/log/nginx/ics-logquery-error.log;
}
```

**Enable Site:**

```bash
sudo ln -s /etc/nginx/sites-available/ics-logquery /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

### Step 5: SSL Certificate (Let's Encrypt)

```bash
sudo apt install certbot python3-certbot-nginx
sudo certbot --nginx -d your-domain.com
```

---

## ☁️ Cloud Deployment

### AWS EC2

**Instance Requirements:**
- **Type**: t3.xlarge or better (4 vCPU, 16GB RAM)
- **Storage**: 50GB EBS
- **OS**: Ubuntu 20.04 LTS
- **Security Group**: Allow ports 22, 80, 443

**Setup Script:**

```bash
#!/bin/bash
# AWS EC2 Setup Script

# Update system
sudo apt update && sudo apt upgrade -y

# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker ubuntu

# Install Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# Clone and deploy
git clone https://github.com/yourusername/ICS-LogQueryGPT.git
cd ICS-LogQueryGPT
docker-compose up -d

echo "Deployment complete! Access at http://$(curl -s http://169.254.169.254/latest/meta-data/public-ipv4):8501"
```

### Azure VM

**VM Requirements:**
- **Size**: Standard_D4s_v3 (4 vCPU, 16GB RAM)
- **OS**: Ubuntu 20.04 LTS
- **Disk**: 128GB Premium SSD
- **Network**: Allow HTTP/HTTPS

**Deploy with Azure CLI:**

```bash
# Create resource group
az group create --name ics-logquery-rg --location eastus

# Create VM
az vm create \
  --resource-group ics-logquery-rg \
  --name ics-logquery-vm \
  --image UbuntuLTS \
  --size Standard_D4s_v3 \
  --admin-username azureuser \
  --generate-ssh-keys

# Open ports
az vm open-port --port 80 --resource-group ics-logquery-rg --name ics-logquery-vm
az vm open-port --port 443 --resource-group ics-logquery-rg --name ics-logquery-vm

# SSH and deploy
ssh azureuser@<VM-IP>
# Follow production deployment steps
```

### Google Cloud Platform (GCP)

**Compute Engine:**
- **Machine Type**: n2-standard-4 (4 vCPU, 16GB)
- **Boot Disk**: Ubuntu 20.04, 50GB
- **Firewall**: Allow HTTP/HTTPS

**Deploy with gcloud:**

```bash
# Create instance
gcloud compute instances create ics-logquery \
  --machine-type=n2-standard-4 \
  --image-family=ubuntu-2004-lts \
  --image-project=ubuntu-os-cloud \
  --boot-disk-size=50GB \
  --tags=http-server,https-server

# SSH and deploy
gcloud compute ssh ics-logquery
# Follow production deployment steps
```

---

## 🔒 Security Considerations

### 1. Authentication

**Basic Auth with Nginx:**

```bash
# Install htpasswd
sudo apt install apache2-utils

# Create password file
sudo htpasswd -c /etc/nginx/.htpasswd admin

# Update Nginx config
location / {
    auth_basic "Restricted Access";
    auth_basic_user_file /etc/nginx/.htpasswd;
    proxy_pass http://localhost:8501;
}
```

### 2. Firewall

```bash
# UFW (Ubuntu)
sudo ufw allow 22/tcp
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw enable

# Block Ollama from external access
sudo ufw deny 11434/tcp
```

### 3. SSL/TLS

Always use HTTPS in production:
- Use Let's Encrypt for free certificates
- Renew certificates automatically
- Enforce HTTPS redirects

### 4. Data Security

```bash
# Restrict file permissions
chmod 600 data/processed_logs/*.csv
chmod 600 data/embeddings/*.npy

# Backup sensitive data
tar -czf backup.tar.gz data/
gpg -c backup.tar.gz
```

---

## 📊 Monitoring & Maintenance

### Logging

**Centralized Logging:**

```bash
# View application logs
sudo journalctl -u ics-logquery -f

# View Ollama logs
sudo journalctl -u ollama -f

# Nginx logs
sudo tail -f /var/log/nginx/ics-logquery-access.log
sudo tail -f /var/log/nginx/ics-logquery-error.log
```

### Monitoring Script

**File: `monitor.sh`**

```bash
#!/bin/bash
# System monitoring script

echo "=== ICS-LogQueryGPT Health Check ==="
echo "Date: $(date)"
echo ""

# Check services
echo "Services Status:"
systemctl is-active ollama && echo "✅ Ollama: Running" || echo "❌ Ollama: Stopped"
systemctl is-active ics-logquery && echo "✅ App: Running" || echo "❌ App: Stopped"
systemctl is-active nginx && echo "✅ Nginx: Running" || echo "❌ Nginx: Stopped"
echo ""

# Check ports
echo "Port Status:"
nc -zv localhost 11434 &>/dev/null && echo "✅ Ollama port (11434): Open" || echo "❌ Ollama port: Closed"
nc -zv localhost 8501 &>/dev/null && echo "✅ App port (8501): Open" || echo "❌ App port: Closed"
echo ""

# Check disk space
echo "Disk Usage:"
df -h / | tail -1
echo ""

# Check memory
echo "Memory Usage:"
free -h | grep Mem
echo ""

# Check CPU
echo "CPU Load:"
uptime
```

### Backup Strategy

```bash
#!/bin/bash
# Backup script

BACKUP_DIR="/backup/ics-logquery"
DATE=$(date +%Y%m%d_%H%M%S)

mkdir -p $BACKUP_DIR

# Backup data
tar -czf $BACKUP_DIR/data_$DATE.tar.gz data/

# Backup configuration
cp -r src/ $BACKUP_DIR/src_$DATE/

# Keep only last 7 days
find $BACKUP_DIR -type f -mtime +7 -delete

echo "Backup completed: $DATE"
```

### Updates

```bash
#!/bin/bash
# Update script

cd /home/icslog/ICS-LogQueryGPT

# Stop services
sudo systemctl stop ics-logquery

# Pull updates
git pull origin main

# Update dependencies
source venv/bin/activate
pip install -r requirements.txt

# Update Ollama model (if needed)
ollama pull llama3.1:8b

# Restart services
sudo systemctl start ics-logquery

echo "Update completed"
```

---

## 🧪 Production Checklist

Before going live, verify:

- [ ] All tests pass (`python tests/test_complete_system.py`)
- [ ] Ollama service running and stable
- [ ] Application accessible via domain
- [ ] SSL certificate valid
- [ ] Authentication configured
- [ ] Firewall rules applied
- [ ] Monitoring in place
- [ ] Backup system configured
- [ ] Documentation updated
- [ ] Team trained

---

## 📞 Support

For deployment issues:
- GitHub Issues: [Report problems](https://github.com/yourusername/ICS-LogQueryGPT/issues)
- Email: team@example.com

---

**Version**: 1.0.0  
**Last Updated**: January 21, 2026  
**License**: MIT
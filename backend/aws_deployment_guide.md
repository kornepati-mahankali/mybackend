# AWS EC2 Deployment Guide for Lavangam Backend

This guide explains how to deploy all Lavangam backend services to AWS EC2 instance.

## 🚀 Quick Deployment

### Option 1: Automated Deployment (Recommended)

```bash
# Run the automated deployment script
./deploy_to_aws.sh
```

### Option 2: Manual Deployment

Follow the step-by-step instructions below.

## 📋 Prerequisites

1. **AWS Account** with EC2 access
2. **AWS CLI** installed and configured
3. **SSH Key Pair** created in AWS
4. **Security Group** configured for your services
5. **Domain Name** (optional, for production)

## 🔧 Step 1: Create EC2 Instance

### Using AWS Console

1. **Launch EC2 Instance:**
   - AMI: Ubuntu 22.04 LTS (recommended)
   - Instance Type: t3.medium or larger (2+ vCPUs, 4+ GB RAM)
   - Storage: 20+ GB SSD
   - Security Group: Configure ports (see below)

2. **Security Group Configuration:**
   ```
   SSH (22): 0.0.0.0/0 (or your IP)
   HTTP (80): 0.0.0.0/0
   HTTPS (443): 0.0.0.0/0
   Custom TCP (8000): 0.0.0.0/0 (Main API)
   Custom TCP (5022): 0.0.0.0/0 (Scrapers API)
   Custom TCP (5024): 0.0.0.0/0 (System Usage API)
   Custom TCP (8004): 0.0.0.0/0 (Dashboard API)
   Custom TCP (5000): 0.0.0.0/0 (File Manager)
   Custom TCP (5001): 0.0.0.0/0 (Scraper WebSocket)
   Custom TCP (5025): 0.0.0.0/0 (Admin Metrics API)
   Custom TCP (5002): 0.0.0.0/0 (E-Procurement Server)
   Custom TCP (8765): 0.0.0.0/0 (Dashboard WebSocket)
   Custom TCP (3307): 0.0.0.0/0 (MySQL Database)
   ```

### Using AWS CLI

```bash
# Create security group
aws ec2 create-security-group \
    --group-name lavangam-backend-sg \
    --description "Security group for Lavangam backend services"

# Add inbound rules
aws ec2 authorize-security-group-ingress \
    --group-name lavangam-backend-sg \
    --protocol tcp \
    --port 22 \
    --cidr 0.0.0.0/0

aws ec2 authorize-security-group-ingress \
    --group-name lavangam-backend-sg \
    --protocol tcp \
    --port 80 \
    --cidr 0.0.0.0/0

# Add other ports...
aws ec2 authorize-security-group-ingress \
    --group-name lavangam-backend-sg \
    --protocol tcp \
    --port 8000 \
    --cidr 0.0.0.0/0

# Launch instance
aws ec2 run-instances \
    --image-id ami-0c02fb55956c7d316 \
    --count 1 \
    --instance-type t3.medium \
    --key-name your-key-pair \
    --security-group-ids sg-xxxxxxxxx \
    --tag-specifications 'ResourceType=instance,Tags=[{Key=Name,Value=Lavangam-Backend}]'
```

## 🔑 Step 2: Connect to EC2 Instance

```bash
# Connect via SSH
ssh -i your-key.pem ubuntu@your-ec2-public-ip

# Update system
sudo apt update && sudo apt upgrade -y
```

## 🐍 Step 3: Install Dependencies

```bash
# Install Python and pip
sudo apt install python3 python3-pip python3-venv -y

# Install system dependencies
sudo apt install nginx mysql-server mysql-client -y

# Install additional dependencies for scraping
sudo apt install chromium-browser chromium-chromedriver -y

# Install Node.js (if needed)
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt-get install -y nodejs
```

## 🗄️ Step 4: Setup MySQL Database

```bash
# Secure MySQL installation
sudo mysql_secure_installation

# Create database and user
sudo mysql -u root -p
```

```sql
CREATE DATABASE toolinformation;
CREATE USER 'lavangam'@'localhost' IDENTIFIED BY 'your_secure_password';
GRANT ALL PRIVILEGES ON toolinformation.* TO 'lavangam'@'localhost';
FLUSH PRIVILEGES;
EXIT;
```

## 📁 Step 5: Deploy Application

```bash
# Create application directory
sudo mkdir -p /opt/lavangam
sudo chown ubuntu:ubuntu /opt/lavangam
cd /opt/lavangam

# Clone or upload your code
# Option 1: Clone from Git
git clone https://github.com/your-repo/lavangam.git .

# Option 2: Upload via SCP
# scp -r backend/ ubuntu@your-ec2-ip:/opt/lavangam/

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install Python dependencies
pip install -r requirements.txt

# Install additional dependencies
pip install gunicorn supervisor
```

## ⚙️ Step 6: Configure Services

### Create Systemd Service Files

```bash
# Create service directory
sudo mkdir -p /etc/systemd/system/lavangam
```

**Main API Service** (`/etc/systemd/system/lavangam/main-api.service`):
```ini
[Unit]
Description=Lavangam Main API
After=network.target

[Service]
Type=simple
User=ubuntu
WorkingDirectory=/opt/lavangam
Environment=PATH=/opt/lavangam/venv/bin
ExecStart=/opt/lavangam/venv/bin/gunicorn main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

**Scrapers API Service** (`/etc/systemd/system/lavangam/scrapers-api.service`):
```ini
[Unit]
Description=Lavangam Scrapers API
After=network.target

[Service]
Type=simple
User=ubuntu
WorkingDirectory=/opt/lavangam
Environment=PATH=/opt/lavangam/venv/bin
ExecStart=/opt/lavangam/venv/bin/gunicorn scrapers.api:app -w 2 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:5022
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

**Dashboard API Service** (`/etc/systemd/system/lavangam/dashboard-api.service`):
```ini
[Unit]
Description=Lavangam Dashboard API
After=network.target

[Service]
Type=simple
User=ubuntu
WorkingDirectory=/opt/lavangam
Environment=PATH=/opt/lavangam/venv/bin
ExecStart=/opt/lavangam/venv/bin/gunicorn dashboard_api:app -w 2 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8004
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

**File Manager Service** (`/etc/systemd/system/lavangam/file-manager.service`):
```ini
[Unit]
Description=Lavangam File Manager
After=network.target

[Service]
Type=simple
User=ubuntu
WorkingDirectory=/opt/lavangam
Environment=PATH=/opt/lavangam/venv/bin
ExecStart=/opt/lavangam/venv/bin/python file_manager.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

**E-Procurement Service** (`/etc/systemd/system/lavangam/eproc-server.service`):
```ini
[Unit]
Description=Lavangam E-Procurement Server
After=network.target

[Service]
Type=simple
User=ubuntu
WorkingDirectory=/opt/lavangam
Environment=PATH=/opt/lavangam/venv/bin
ExecStart=/opt/lavangam/venv/bin/python eproc_server_fixed.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

### Enable and Start Services

```bash
# Reload systemd
sudo systemctl daemon-reload

# Enable services
sudo systemctl enable lavangam-main-api
sudo systemctl enable lavangam-scrapers-api
sudo systemctl enable lavangam-dashboard-api
sudo systemctl enable lavangam-file-manager
sudo systemctl enable lavangam-eproc-server

# Start services
sudo systemctl start lavangam-main-api
sudo systemctl start lavangam-scrapers-api
sudo systemctl start lavangam-dashboard-api
sudo systemctl start lavangam-file-manager
sudo systemctl start lavangam-eproc-server

# Check status
sudo systemctl status lavangam-*
```

## 🌐 Step 7: Configure Nginx (Reverse Proxy)

```bash
# Create Nginx configuration
sudo nano /etc/nginx/sites-available/lavangam
```

**Nginx Configuration:**
```nginx
server {
    listen 80;
    server_name your-domain.com;  # Replace with your domain

    # Main API
    location /api/ {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # Scrapers API
    location /scrapers/ {
        proxy_pass http://127.0.0.1:5022/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # Dashboard API
    location /dashboard/ {
        proxy_pass http://127.0.0.1:8004/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # File Manager
    location /files/ {
        proxy_pass http://127.0.0.1:5000/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # E-Procurement
    location /eproc/ {
        proxy_pass http://127.0.0.1:5002/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # WebSocket support
    location /ws/ {
        proxy_pass http://127.0.0.1:5001/;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

```bash
# Enable site
sudo ln -s /etc/nginx/sites-available/lavangam /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

## 🔒 Step 8: SSL Certificate (Optional)

```bash
# Install Certbot
sudo apt install certbot python3-certbot-nginx -y

# Get SSL certificate
sudo certbot --nginx -d your-domain.com

# Auto-renewal
sudo crontab -e
# Add: 0 12 * * * /usr/bin/certbot renew --quiet
```

## 📊 Step 9: Monitoring and Logs

```bash
# View service logs
sudo journalctl -u lavangam-main-api -f
sudo journalctl -u lavangam-scrapers-api -f
sudo journalctl -u lavangam-dashboard-api -f

# Check service status
sudo systemctl status lavangam-*

# Monitor system resources
htop
df -h
free -h
```

## 🚀 Step 10: Environment Configuration

Create environment file:
```bash
sudo nano /opt/lavangam/.env
```

```env
# Database Configuration
DB_HOST=localhost
DB_PORT=3307
DB_USER=lavangam
DB_PASSWORD=your_secure_password
DB_NAME=toolinformation

# AWS Configuration
AWS_ACCESS_KEY_ID=your_access_key
AWS_SECRET_ACCESS_KEY=your_secret_key
AWS_REGION=us-west-2

# Application Configuration
ENVIRONMENT=production
DEBUG=False
LOG_LEVEL=INFO
```

## 🔄 Step 11: Deployment Scripts

### Automated Deployment Script

Create `deploy_to_aws.sh`:
```bash
#!/bin/bash

echo "🚀 Deploying Lavangam Backend to AWS EC2..."

# Update system
sudo apt update && sudo apt upgrade -y

# Install dependencies
sudo apt install python3 python3-pip python3-venv nginx mysql-server -y

# Setup application
cd /opt/lavangam
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
pip install gunicorn

# Setup services
sudo systemctl daemon-reload
sudo systemctl enable lavangam-*
sudo systemctl start lavangam-*

# Setup Nginx
sudo nginx -t
sudo systemctl restart nginx

echo "✅ Deployment completed!"
```

### Update Script

Create `update_deployment.sh`:
```bash
#!/bin/bash

echo "🔄 Updating Lavangam Backend..."

cd /opt/lavangam

# Pull latest code
git pull origin main

# Update dependencies
source venv/bin/activate
pip install -r requirements.txt

# Restart services
sudo systemctl restart lavangam-*

echo "✅ Update completed!"
```

## 🚨 Troubleshooting

### Common Issues

1. **Service Won't Start**
   ```bash
   # Check logs
   sudo journalctl -u lavangam-main-api -f
   
   # Check permissions
   sudo chown -R ubuntu:ubuntu /opt/lavangam
   ```

2. **Database Connection Failed**
   ```bash
   # Check MySQL status
   sudo systemctl status mysql
   
   # Test connection
   mysql -u lavangam -p toolinformation
   ```

3. **Port Already in Use**
   ```bash
   # Check what's using the port
   sudo netstat -tlnp | grep :8000
   
   # Kill process if needed
   sudo kill -9 <PID>
   ```

4. **Nginx Configuration Error**
   ```bash
   # Test configuration
   sudo nginx -t
   
   # Check Nginx logs
   sudo tail -f /var/log/nginx/error.log
   ```

## 📈 Performance Optimization

1. **Enable Gzip Compression**
   ```nginx
   gzip on;
   gzip_types text/plain text/css application/json application/javascript;
   ```

2. **Add Caching Headers**
   ```nginx
   location ~* \.(js|css|png|jpg|jpeg|gif|ico)$ {
       expires 1y;
       add_header Cache-Control "public, immutable";
   }
   ```

3. **Database Optimization**
   ```sql
   -- Add indexes for better performance
   CREATE INDEX idx_jobs_status ON jobs(status);
   CREATE INDEX idx_jobs_created_at ON jobs(created_at);
   ```

## 🔐 Security Best Practices

1. **Firewall Configuration**
   ```bash
   # Install UFW
   sudo apt install ufw
   sudo ufw enable
   sudo ufw allow ssh
   sudo ufw allow 80
   sudo ufw allow 443
   ```

2. **Regular Updates**
   ```bash
   # Create update script
   sudo crontab -e
   # Add: 0 2 * * 0 /usr/bin/apt update && /usr/bin/apt upgrade -y
   ```

3. **Backup Strategy**
   ```bash
   # Database backup
   mysqldump -u lavangam -p toolinformation > backup_$(date +%Y%m%d).sql
   
   # Application backup
   tar -czf lavangam_backup_$(date +%Y%m%d).tar.gz /opt/lavangam
   ```

## 📞 Support

For deployment issues:
1. Check service logs: `sudo journalctl -u lavangam-* -f`
2. Verify network connectivity: `curl http://localhost:8000/health`
3. Check system resources: `htop`, `df -h`
4. Review security group settings in AWS Console 
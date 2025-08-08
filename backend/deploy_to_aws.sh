#!/bin/bash

# Lavangam Backend AWS EC2 Deployment Script
# This script automates the deployment of all Lavangam backend services to AWS EC2

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Logging function
log() {
    echo -e "${GREEN}[$(date +'%Y-%m-%d %H:%M:%S')]${NC} $1"
}

warn() {
    echo -e "${YELLOW}[$(date +'%Y-%m-%d %H:%M:%S')] WARNING:${NC} $1"
}

error() {
    echo -e "${RED}[$(date +'%Y-%m-%d %H:%M:%S')] ERROR:${NC} $1"
    exit 1
}

# Check if running as root
if [[ $EUID -eq 0 ]]; then
   error "This script should not be run as root. Please run as ubuntu user."
fi

log "🚀 Starting Lavangam Backend AWS EC2 Deployment..."

# Step 1: Update system
log "📦 Updating system packages..."
sudo apt update && sudo apt upgrade -y

# Step 2: Install system dependencies
log "🔧 Installing system dependencies..."
sudo apt install -y \
    python3 \
    python3-pip \
    python3-venv \
    nginx \
    mysql-server \
    mysql-client \
    chromium-browser \
    chromium-chromedriver \
    curl \
    wget \
    git \
    unzip \
    htop \
    ufw

# Step 3: Install Node.js
log "📦 Installing Node.js..."
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt-get install -y nodejs

# Step 4: Setup MySQL
log "🗄️ Setting up MySQL database..."
sudo systemctl start mysql
sudo systemctl enable mysql

# Secure MySQL installation (non-interactive)
log "🔒 Securing MySQL installation..."
sudo mysql -e "ALTER USER 'root'@'localhost' IDENTIFIED WITH mysql_native_password BY 'Lavangam@2024';"
sudo mysql -e "DELETE FROM mysql.user WHERE User='';"
sudo mysql -e "DELETE FROM mysql.user WHERE User='root' AND Host NOT IN ('localhost', '127.0.0.1', '::1');"
sudo mysql -e "DROP DATABASE IF EXISTS test;"
sudo mysql -e "DELETE FROM mysql.db WHERE Db='test' OR Db='test\\_%';"
sudo mysql -e "FLUSH PRIVILEGES;"

# Create database and user
log "📊 Creating database and user..."
sudo mysql -e "CREATE DATABASE IF NOT EXISTS toolinformation;"
sudo mysql -e "CREATE USER IF NOT EXISTS 'lavangam'@'localhost' IDENTIFIED BY 'Lavangam@2024';"
sudo mysql -e "GRANT ALL PRIVILEGES ON toolinformation.* TO 'lavangam'@'localhost';"
sudo mysql -e "FLUSH PRIVILEGES;"

# Step 5: Create application directory
log "📁 Setting up application directory..."
sudo mkdir -p /opt/lavangam
sudo chown ubuntu:ubuntu /opt/lavangam
cd /opt/lavangam

# Step 6: Setup Python virtual environment
log "🐍 Setting up Python virtual environment..."
python3 -m venv venv
source venv/bin/activate

# Step 7: Install Python dependencies
log "📦 Installing Python dependencies..."
pip install --upgrade pip
pip install -r requirements.txt
pip install gunicorn supervisor

# Step 8: Create systemd service files
log "⚙️ Creating systemd service files..."
sudo mkdir -p /etc/systemd/system/lavangam

# Main API Service
sudo tee /etc/systemd/system/lavangam/main-api.service > /dev/null <<EOF
[Unit]
Description=Lavangam Main API
After=network.target mysql.service

[Service]
Type=simple
User=ubuntu
Group=ubuntu
WorkingDirectory=/opt/lavangam
Environment=PATH=/opt/lavangam/venv/bin
Environment=PYTHONPATH=/opt/lavangam
ExecStart=/opt/lavangam/venv/bin/gunicorn main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000 --timeout 120
Restart=always
RestartSec=10
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
EOF

# Scrapers API Service
sudo tee /etc/systemd/system/lavangam/scrapers-api.service > /dev/null <<EOF
[Unit]
Description=Lavangam Scrapers API
After=network.target mysql.service

[Service]
Type=simple
User=ubuntu
Group=ubuntu
WorkingDirectory=/opt/lavangam
Environment=PATH=/opt/lavangam/venv/bin
Environment=PYTHONPATH=/opt/lavangam
ExecStart=/opt/lavangam/venv/bin/gunicorn scrapers.api:app -w 2 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:5022 --timeout 120
Restart=always
RestartSec=10
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
EOF

# System Usage API Service
sudo tee /etc/systemd/system/lavangam/system-usage-api.service > /dev/null <<EOF
[Unit]
Description=Lavangam System Usage API
After=network.target

[Service]
Type=simple
User=ubuntu
Group=ubuntu
WorkingDirectory=/opt/lavangam
Environment=PATH=/opt/lavangam/venv/bin
Environment=PYTHONPATH=/opt/lavangam
ExecStart=/opt/lavangam/venv/bin/gunicorn system_usage_api:app -w 2 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:5024 --timeout 120
Restart=always
RestartSec=10
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
EOF

# Dashboard API Service
sudo tee /etc/systemd/system/lavangam/dashboard-api.service > /dev/null <<EOF
[Unit]
Description=Lavangam Dashboard API
After=network.target mysql.service

[Service]
Type=simple
User=ubuntu
Group=ubuntu
WorkingDirectory=/opt/lavangam
Environment=PATH=/opt/lavangam/venv/bin
Environment=PYTHONPATH=/opt/lavangam
ExecStart=/opt/lavangam/venv/bin/gunicorn dashboard_api:app -w 2 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8004 --timeout 120
Restart=always
RestartSec=10
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
EOF

# Admin Metrics API Service
sudo tee /etc/systemd/system/lavangam/admin-metrics-api.service > /dev/null <<EOF
[Unit]
Description=Lavangam Admin Metrics API
After=network.target mysql.service

[Service]
Type=simple
User=ubuntu
Group=ubuntu
WorkingDirectory=/opt/lavangam
Environment=PATH=/opt/lavangam/venv/bin
Environment=PYTHONPATH=/opt/lavangam
ExecStart=/opt/lavangam/venv/bin/gunicorn admin_metrics_api:app -w 2 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:5025 --timeout 120
Restart=always
RestartSec=10
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
EOF

# File Manager Service
sudo tee /etc/systemd/system/lavangam/file-manager.service > /dev/null <<EOF
[Unit]
Description=Lavangam File Manager
After=network.target

[Service]
Type=simple
User=ubuntu
Group=ubuntu
WorkingDirectory=/opt/lavangam
Environment=PATH=/opt/lavangam/venv/bin
Environment=PYTHONPATH=/opt/lavangam
ExecStart=/opt/lavangam/venv/bin/python file_manager.py
Restart=always
RestartSec=10
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
EOF

# E-Procurement Service
sudo tee /etc/systemd/system/lavangam/eproc-server.service > /dev/null <<EOF
[Unit]
Description=Lavangam E-Procurement Server
After=network.target mysql.service

[Service]
Type=simple
User=ubuntu
Group=ubuntu
WorkingDirectory=/opt/lavangam
Environment=PATH=/opt/lavangam/venv/bin
Environment=PYTHONPATH=/opt/lavangam
ExecStart=/opt/lavangam/venv/bin/python eproc_server_fixed.py
Restart=always
RestartSec=10
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
EOF

# Step 9: Create environment file
log "🔧 Creating environment configuration..."
sudo tee /opt/lavangam/.env > /dev/null <<EOF
# Database Configuration
DB_HOST=localhost
DB_PORT=3306
DB_USER=lavangam
DB_PASSWORD=Lavangam@2024
DB_NAME=toolinformation

# Application Configuration
ENVIRONMENT=production
DEBUG=False
LOG_LEVEL=INFO

# AWS Configuration (update with your values)
AWS_ACCESS_KEY_ID=your_access_key_here
AWS_SECRET_ACCESS_KEY=your_secret_key_here
AWS_REGION=us-west-2

# Supabase Configuration
SUPABASE_URL=https://zjfjaezztfydiryzsyvd.supabase.co
SUPABASE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InpqZmphZXp6dGZ5ZGlyeXpzeXZkIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTEwMjcwMjEsImV4cCI6MjA2NjYwMzAyMX0.6ZVMwXK4aMGmR68GTYo0yt_L7bOg5QWtElTaa8heQos
EOF

# Step 10: Setup Nginx
log "🌐 Setting up Nginx reverse proxy..."
sudo tee /etc/nginx/sites-available/lavangam > /dev/null <<EOF
server {
    listen 80;
    server_name _;  # Replace with your domain

    # Security headers
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header Referrer-Policy "no-referrer-when-downgrade" always;
    add_header Content-Security-Policy "default-src 'self' http: https: data: blob: 'unsafe-inline'" always;

    # Gzip compression
    gzip on;
    gzip_vary on;
    gzip_min_length 1024;
    gzip_proxied expired no-cache no-store private must-revalidate auth;
    gzip_types text/plain text/css text/xml text/javascript application/x-javascript application/xml+rss application/javascript application/json;

    # Main API
    location /api/ {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
    }

    # Scrapers API
    location /scrapers/ {
        proxy_pass http://127.0.0.1:5022/;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
    }

    # System Usage API
    location /system/ {
        proxy_pass http://127.0.0.1:5024/;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }

    # Dashboard API
    location /dashboard/ {
        proxy_pass http://127.0.0.1:8004/;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }

    # Admin Metrics API
    location /admin/ {
        proxy_pass http://127.0.0.1:5025/;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }

    # File Manager
    location /files/ {
        proxy_pass http://127.0.0.1:5000/;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }

    # E-Procurement
    location /eproc/ {
        proxy_pass http://127.0.0.1:5002/;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }

    # WebSocket support
    location /ws/ {
        proxy_pass http://127.0.0.1:5001/;
        proxy_http_version 1.1;
        proxy_set_header Upgrade \$http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
        proxy_read_timeout 86400;
    }

    # Health check endpoint
    location /health {
        access_log off;
        return 200 "healthy\n";
        add_header Content-Type text/plain;
    }

    # Static files caching
    location ~* \.(js|css|png|jpg|jpeg|gif|ico|svg)$ {
        expires 1y;
        add_header Cache-Control "public, immutable";
        access_log off;
    }
}
EOF

# Enable Nginx site
sudo ln -sf /etc/nginx/sites-available/lavangam /etc/nginx/sites-enabled/
sudo rm -f /etc/nginx/sites-enabled/default

# Test Nginx configuration
sudo nginx -t

# Step 11: Setup firewall
log "🔥 Configuring firewall..."
sudo ufw --force enable
sudo ufw allow ssh
sudo ufw allow 80
sudo ufw allow 443
sudo ufw allow 8000
sudo ufw allow 5022
sudo ufw allow 5024
sudo ufw allow 8004
sudo ufw allow 5000
sudo ufw allow 5001
sudo ufw allow 5025
sudo ufw allow 5002
sudo ufw allow 8765

# Step 12: Enable and start services
log "🚀 Enabling and starting services..."
sudo systemctl daemon-reload

# Enable services
sudo systemctl enable lavangam-main-api
sudo systemctl enable lavangam-scrapers-api
sudo systemctl enable lavangam-system-usage-api
sudo systemctl enable lavangam-dashboard-api
sudo systemctl enable lavangam-admin-metrics-api
sudo systemctl enable lavangam-file-manager
sudo systemctl enable lavangam-eproc-server

# Start services
sudo systemctl start lavangam-main-api
sudo systemctl start lavangam-scrapers-api
sudo systemctl start lavangam-system-usage-api
sudo systemctl start lavangam-dashboard-api
sudo systemctl start lavangam-admin-metrics-api
sudo systemctl start lavangam-file-manager
sudo systemctl start lavangam-eproc-server

# Start Nginx
sudo systemctl restart nginx

# Step 13: Create output directories
log "📁 Creating output directories..."
mkdir -p /opt/lavangam/outputs/{ap,eproc,gem,ireps}

# Step 14: Setup log rotation
log "📝 Setting up log rotation..."
sudo tee /etc/logrotate.d/lavangam > /dev/null <<EOF
/opt/lavangam/outputs/*.log {
    daily
    missingok
    rotate 30
    compress
    delaycompress
    notifempty
    create 644 ubuntu ubuntu
}
EOF

# Step 15: Create monitoring script
log "📊 Creating monitoring script..."
sudo tee /opt/lavangam/monitor_services.sh > /dev/null <<EOF
#!/bin/bash

echo "=== Lavangam Services Status ==="
echo "Date: \$(date)"
echo ""

services=(
    "lavangam-main-api"
    "lavangam-scrapers-api"
    "lavangam-system-usage-api"
    "lavangam-dashboard-api"
    "lavangam-admin-metrics-api"
    "lavangam-file-manager"
    "lavangam-eproc-server"
    "nginx"
    "mysql"
)

for service in "\${services[@]}"; do
    if systemctl is-active --quiet \$service; then
        echo "✅ \$service: RUNNING"
    else
        echo "❌ \$service: STOPPED"
    fi
done

echo ""
echo "=== System Resources ==="
echo "CPU Usage: \$(top -bn1 | grep "Cpu(s)" | awk '{print \$2}' | cut -d'%' -f1)%"
echo "Memory Usage: \$(free | grep Mem | awk '{printf("%.2f%%", \$3/\$2 * 100.0)}')"
echo "Disk Usage: \$(df / | tail -1 | awk '{print \$5}')"
EOF

sudo chmod +x /opt/lavangam/monitor_services.sh

# Step 16: Create backup script
log "💾 Creating backup script..."
sudo tee /opt/lavangam/backup.sh > /dev/null <<EOF
#!/bin/bash

BACKUP_DIR="/opt/backups"
DATE=\$(date +%Y%m%d_%H%M%S)

mkdir -p \$BACKUP_DIR

# Database backup
mysqldump -u lavangam -pLavangam@2024 toolinformation > \$BACKUP_DIR/db_backup_\$DATE.sql

# Application backup
tar -czf \$BACKUP_DIR/app_backup_\$DATE.tar.gz /opt/lavangam

# Keep only last 7 days of backups
find \$BACKUP_DIR -name "*.sql" -mtime +7 -delete
find \$BACKUP_DIR -name "*.tar.gz" -mtime +7 -delete

echo "Backup completed: \$DATE"
EOF

sudo chmod +x /opt/lavangam/backup.sh

# Step 17: Setup cron jobs
log "⏰ Setting up cron jobs..."
(crontab -l 2>/dev/null; echo "0 2 * * * /opt/lavangam/backup.sh") | crontab -
(crontab -l 2>/dev/null; echo "0 3 * * 0 /usr/bin/apt update && /usr/bin/apt upgrade -y") | crontab -

# Step 18: Final checks
log "🔍 Performing final checks..."

# Check if services are running
sleep 10
for service in lavangam-main-api lavangam-scrapers-api lavangam-system-usage-api lavangam-dashboard-api lavangam-admin-metrics-api lavangam-file-manager lavangam-eproc-server; do
    if systemctl is-active --quiet $service; then
        log "✅ $service is running"
    else
        warn "$service is not running"
        sudo journalctl -u $service --no-pager -n 10
    fi
done

# Check Nginx
if systemctl is-active --quiet nginx; then
    log "✅ Nginx is running"
else
    warn "Nginx is not running"
fi

# Check MySQL
if systemctl is-active --quiet mysql; then
    log "✅ MySQL is running"
else
    warn "MySQL is not running"
fi

# Test endpoints
log "🌐 Testing endpoints..."
curl -s http://localhost:8000/docs > /dev/null && log "✅ Main API is accessible" || warn "Main API is not accessible"
curl -s http://localhost:5022/docs > /dev/null && log "✅ Scrapers API is accessible" || warn "Scrapers API is not accessible"
curl -s http://localhost:5024/api/system-usage > /dev/null && log "✅ System Usage API is accessible" || warn "System Usage API is not accessible"

log "🎉 Deployment completed successfully!"
log ""
log "📋 Service URLs:"
log "  Main API: http://$(curl -s http://169.254.169.254/latest/meta-data/public-ipv4)/api/"
log "  Scrapers API: http://$(curl -s http://169.254.169.254/latest/meta-data/public-ipv4)/scrapers/"
log "  Dashboard API: http://$(curl -s http://169.254.169.254/latest/meta-data/public-ipv4)/dashboard/"
log "  Admin Metrics: http://$(curl -s http://169.254.169.254/latest/meta-data/public-ipv4)/admin/"
log "  File Manager: http://$(curl -s http://169.254.169.254/latest/meta-data/public-ipv4)/files/"
log "  E-Procurement: http://$(curl -s http://169.254.169.254/latest/meta-data/public-ipv4)/eproc/"
log ""
log "🔧 Useful commands:"
log "  Check service status: sudo systemctl status lavangam-*"
log "  View logs: sudo journalctl -u lavangam-main-api -f"
log "  Monitor services: /opt/lavangam/monitor_services.sh"
log "  Create backup: /opt/lavangam/backup.sh"
log ""
log "⚠️  IMPORTANT: Update the .env file with your actual AWS credentials and other sensitive information!" 
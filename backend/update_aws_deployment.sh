#!/bin/bash

# Lavangam Backend AWS EC2 Update Script
# This script updates an existing Lavangam backend deployment on AWS EC2

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

log "🔄 Starting Lavangam Backend AWS EC2 Update..."

# Check if application directory exists
if [ ! -d "/opt/lavangam" ]; then
    error "Lavangam application directory not found. Please run the full deployment script first."
fi

# Step 1: Backup current deployment
log "💾 Creating backup of current deployment..."
BACKUP_DIR="/opt/backups"
DATE=$(date +%Y%m%d_%H%M%S)
mkdir -p $BACKUP_DIR

# Backup application
tar -czf $BACKUP_DIR/app_backup_$DATE.tar.gz /opt/lavangam

# Backup database
mysqldump -u lavangam -pLavangam@2024 toolinformation > $BACKUP_DIR/db_backup_$DATE.sql

log "✅ Backup completed: $BACKUP_DIR/app_backup_$DATE.tar.gz"

# Step 2: Stop services
log "⏹️ Stopping services..."
sudo systemctl stop lavangam-main-api
sudo systemctl stop lavangam-scrapers-api
sudo systemctl stop lavangam-system-usage-api
sudo systemctl stop lavangam-dashboard-api
sudo systemctl stop lavangam-admin-metrics-api
sudo systemctl stop lavangam-file-manager
sudo systemctl stop lavangam-eproc-server

# Step 3: Update system packages
log "📦 Updating system packages..."
sudo apt update && sudo apt upgrade -y

# Step 4: Navigate to application directory
cd /opt/lavangam

# Step 5: Backup current code (if using git)
if [ -d ".git" ]; then
    log "📝 Backing up current code..."
    git stash
    git pull origin main
    git stash pop
else
    warn "No git repository found. Please update code manually."
fi

# Step 6: Update Python dependencies
log "🐍 Updating Python dependencies..."
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt

# Step 7: Update environment file if needed
log "🔧 Checking environment configuration..."
if [ ! -f ".env" ]; then
    warn ".env file not found. Creating default configuration..."
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
fi

# Step 8: Update systemd service files if needed
log "⚙️ Updating systemd service files..."
sudo systemctl daemon-reload

# Step 9: Start services
log "🚀 Starting services..."
sudo systemctl start lavangam-main-api
sudo systemctl start lavangam-scrapers-api
sudo systemctl start lavangam-system-usage-api
sudo systemctl start lavangam-dashboard-api
sudo systemctl start lavangam-admin-metrics-api
sudo systemctl start lavangam-file-manager
sudo systemctl start lavangam-eproc-server

# Step 10: Restart Nginx
log "🌐 Restarting Nginx..."
sudo systemctl restart nginx

# Step 11: Create output directories if they don't exist
log "📁 Ensuring output directories exist..."
mkdir -p outputs/{ap,eproc,gem,ireps}

# Step 12: Final checks
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

# Test endpoints
log "🌐 Testing endpoints..."
curl -s http://localhost:8000/docs > /dev/null && log "✅ Main API is accessible" || warn "Main API is not accessible"
curl -s http://localhost:5022/docs > /dev/null && log "✅ Scrapers API is accessible" || warn "Scrapers API is not accessible"
curl -s http://localhost:5024/api/system-usage > /dev/null && log "✅ System Usage API is accessible" || warn "System Usage API is not accessible"

# Clean up old backups (keep last 7 days)
log "🧹 Cleaning up old backups..."
find $BACKUP_DIR -name "*.sql" -mtime +7 -delete
find $BACKUP_DIR -name "*.tar.gz" -mtime +7 -delete

log "🎉 Update completed successfully!"
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
log "📦 Backup created: $BACKUP_DIR/app_backup_$DATE.tar.gz" 
# 🚀 Quick AWS EC2 Deployment Guide

This is a quick guide to deploy your Lavangam backend to AWS EC2 in under 30 minutes.

## 📋 Prerequisites

- AWS Account
- AWS CLI configured
- SSH Key Pair created in AWS
- Domain name (optional)

## ⚡ Quick Start (3 Methods)

### Method 1: CloudFormation (Recommended - 5 minutes)

1. **Deploy Infrastructure:**
   ```bash
   aws cloudformation create-stack \
     --stack-name lavangam-backend \
     --template-body file://aws_cloudformation_template.yaml \
     --parameters ParameterKey=KeyPairName,ParameterValue=your-key-pair-name \
     --capabilities CAPABILITY_IAM
   ```

2. **Wait for completion:**
   ```bash
   aws cloudformation wait stack-create-complete --stack-name lavangam-backend
   ```

3. **Get your URLs:**
   ```bash
   aws cloudformation describe-stacks --stack-name lavangam-backend --query 'Stacks[0].Outputs'
   ```

### Method 2: Manual EC2 + Automated Script (15 minutes)

1. **Launch EC2 Instance:**
   - AMI: Ubuntu 22.04 LTS
   - Type: t3.medium
   - Storage: 50 GB
   - Security Group: Allow ports 22, 80, 443, 8000, 5022, 5024, 8004, 5000, 5001, 5025, 5002, 8765

2. **Connect and Deploy:**
   ```bash
   ssh -i your-key.pem ubuntu@your-ec2-ip
   cd /opt
   sudo mkdir lavangam
   sudo chown ubuntu:ubuntu lavangam
   cd lavangam
   
   # Upload your backend files or clone from git
   git clone https://github.com/your-repo/lavangam.git .
   
   # Run deployment script
   chmod +x deploy_to_aws.sh
   ./deploy_to_aws.sh
   ```

### Method 3: Manual Step-by-Step (30 minutes)

Follow the detailed guide in `aws_deployment_guide.md`

## 🔧 Post-Deployment Setup

### 1. Update Environment Variables

```bash
sudo nano /opt/lavangam/.env
```

Update with your actual values:
```env
# AWS Configuration
AWS_ACCESS_KEY_ID=your_actual_access_key
AWS_SECRET_ACCESS_KEY=your_actual_secret_key
AWS_REGION=us-west-2

# Database Configuration (if using external database)
DB_HOST=your-db-host
DB_PASSWORD=your_secure_password
```

### 2. Configure Domain (Optional)

```bash
# Install Certbot
sudo apt install certbot python3-certbot-nginx -y

# Get SSL certificate
sudo certbot --nginx -d your-domain.com
```

### 3. Test Your Deployment

```bash
# Check service status
sudo systemctl status lavangam-*

# Test endpoints
curl http://your-ec2-ip/api/
curl http://your-ec2-ip/scrapers/
curl http://your-ec2-ip/dashboard/
```

## 📊 Service URLs

After deployment, your services will be available at:

| Service | URL Pattern |
|---------|-------------|
| Main API | `http://your-ec2-ip/api/` |
| Scrapers API | `http://your-ec2-ip/scrapers/` |
| System Usage API | `http://your-ec2-ip/system/` |
| Dashboard API | `http://your-ec2-ip/dashboard/` |
| Admin Metrics API | `http://your-ec2-ip/admin/` |
| File Manager | `http://your-ec2-ip/files/` |
| E-Procurement | `http://your-ec2-ip/eproc/` |

## 🔄 Updates and Maintenance

### Update Your Application

```bash
# SSH to your instance
ssh -i your-key.pem ubuntu@your-ec2-ip

# Run update script
cd /opt/lavangam
chmod +x update_aws_deployment.sh
./update_aws_deployment.sh
```

### Monitor Services

```bash
# Check service status
sudo systemctl status lavangam-*

# View logs
sudo journalctl -u lavangam-main-api -f

# Monitor system resources
htop
df -h
free -h

# Run health check
/opt/lavangam/monitor_services.sh
```

### Backup and Restore

```bash
# Create backup
/opt/lavangam/backup.sh

# Restore from backup (if needed)
cd /opt
sudo tar -xzf /opt/backups/app_backup_YYYYMMDD_HHMMSS.tar.gz
```

## 🚨 Troubleshooting

### Common Issues

1. **Services not starting:**
   ```bash
   sudo journalctl -u lavangam-main-api -f
   sudo systemctl restart lavangam-main-api
   ```

2. **Database connection failed:**
   ```bash
   sudo systemctl status mysql
   mysql -u lavangam -p toolinformation
   ```

3. **Port already in use:**
   ```bash
   sudo netstat -tlnp | grep :8000
   sudo kill -9 <PID>
   ```

4. **Nginx configuration error:**
   ```bash
   sudo nginx -t
   sudo systemctl restart nginx
   ```

### Emergency Commands

```bash
# Restart all services
sudo systemctl restart lavangam-*

# Restart everything
sudo reboot

# Check disk space
df -h

# Check memory usage
free -h

# Check running processes
ps aux | grep lavangam
```

## 💰 Cost Optimization

### Instance Sizing

| Workload | Instance Type | Monthly Cost* |
|----------|---------------|---------------|
| Development | t3.small | ~$15 |
| Production (Light) | t3.medium | ~$30 |
| Production (Heavy) | t3.large | ~$60 |
| High Performance | m5.large | ~$85 |

*Estimated costs for us-west-2 region

### Cost Saving Tips

1. **Use Spot Instances** for development/testing
2. **Reserved Instances** for production (1-3 year commitment)
3. **Auto Scaling** based on CPU/memory usage
4. **S3 for file storage** instead of EBS
5. **RDS for database** instead of local MySQL

## 🔐 Security Checklist

- [ ] Update default passwords in `.env`
- [ ] Configure firewall (UFW)
- [ ] Enable SSL/TLS with Let's Encrypt
- [ ] Regular security updates
- [ ] Database backups enabled
- [ ] Monitor access logs
- [ ] Use IAM roles instead of access keys

## 📞 Support

### Useful Commands

```bash
# Service management
sudo systemctl start/stop/restart/status lavangam-*

# Log viewing
sudo journalctl -u lavangam-main-api -f
sudo tail -f /var/log/nginx/access.log

# Health checks
curl http://localhost:8000/health
curl http://localhost:5024/api/system-usage

# Performance monitoring
htop
iotop
nethogs
```

### Getting Help

1. Check service logs: `sudo journalctl -u lavangam-* -f`
2. Verify network connectivity: `curl http://localhost:8000/health`
3. Check system resources: `htop`, `df -h`
4. Review security group settings in AWS Console
5. Check CloudWatch logs (if enabled)

## 🎯 Next Steps

1. **Set up monitoring** with CloudWatch
2. **Configure auto-scaling** for high availability
3. **Set up CI/CD** pipeline
4. **Implement backup strategy** with S3
5. **Add SSL certificate** with Let's Encrypt
6. **Configure domain** and DNS
7. **Set up monitoring** and alerting

---

**Need help?** Check the detailed guide in `aws_deployment_guide.md` or the troubleshooting section above. 
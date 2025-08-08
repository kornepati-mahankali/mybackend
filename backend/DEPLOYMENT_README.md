# AWS Elastic Beanstalk Deployment Guide

## 🚀 Quick Deployment

### Option 1: Using Windows Batch Script (Recommended)
```bash
# Run the deployment script
deploy.bat
```

### Option 2: Manual Deployment
1. Create a ZIP file containing all backend files
2. Upload to AWS Elastic Beanstalk Console
3. Deploy to your environment

## 📁 File Structure
```
backend/
├── .ebextensions/
│   ├── packages.config          # System packages (Python, GCC, etc.)
│   ├── mysql.config             # MySQL development headers
│   ├── database.config          # Database environment variables
│   ├── mariadb_setup.config     # MariaDB installation & configuration
│   ├── environment.config       # Elastic Beanstalk settings
│   └── 01_install_dependencies.config  # Python dependencies
├── requirements.txt             # Python packages
├── app.py                       # Main FastAPI application
├── deploy.bat                   # Windows deployment script
└── test_db_connection.py        # Database connection test
```

## 🔧 Configuration Files Explained

### 1. packages.config
Installs system-level dependencies:
- `python3-devel`: Python development headers
- `gcc`, `gcc-c++`: C/C++ compilers
- `libffi-devel`: Foreign function interface
- `openssl-devel`: OpenSSL development headers

### 2. mysql.config
Installs MySQL development headers:
- Enables MySQL 8.0 repository
- Installs `mysql-community-devel`
- Installs `mariadb-devel` as backup
- Installs `mysql-connector-python` via pip

### 3. database.config
Sets environment variables:
- `DB_HOST`: 127.0.0.1
- `DB_PORT`: 3307
- `DB_NAME`: toolinformation
- `DB_USER`: root
- `DB_PASSWORD`: thanuja

### 4. mariadb_setup.config
Installs and configures MariaDB:
- Installs MariaDB server
- Secures installation with password
- Creates database and user
- Configures port 3307

## 🗄️ Database Setup

### Local Database (for development)
- Host: 127.0.0.1
- Port: 3307
- Database: toolinformation
- User: root
- Password: thanuja

### AWS EC2 Database
MariaDB will be automatically installed and configured on the EC2 instance with the same settings.

## 🔍 Troubleshooting

### Common Issues

#### 1. "mysql-devel not available" Error
**Solution**: The `mysql.config` file now properly installs MySQL development headers.

#### 2. Database Connection Failed
**Check**:
- MariaDB service status: `sudo systemctl status mariadb`
- Database exists: `mysql -u root -p -e "SHOW DATABASES;"`
- Port configuration: `sudo netstat -tlnp | grep 3307`

#### 3. Application Won't Start
**Check logs**:
```bash
# On EC2 instance
sudo tail -f /var/log/eb-engine.log
sudo tail -f /var/log/cfn-init.log
sudo tail -f /var/log/web.stdout.log
```

### Manual Database Setup (if needed)
```bash
# Connect to MariaDB
sudo mysql -u root

# Create database
CREATE DATABASE toolinformation;

# Create user
CREATE USER 'root'@'localhost' IDENTIFIED BY 'thanuja';
GRANT ALL PRIVILEGES ON toolinformation.* TO 'root'@'localhost';
FLUSH PRIVILEGES;

# Configure port 3307
sudo sed -i 's/port=3306/port=3307/' /etc/my.cnf.d/server.cnf
sudo systemctl restart mariadb
```

## 📊 Monitoring

### Health Checks
- Check Elastic Beanstalk environment health
- Monitor application logs
- Test database connectivity

### Log Locations
- `/var/log/eb-engine.log`: Elastic Beanstalk engine logs
- `/var/log/cfn-init.log`: Configuration logs
- `/var/log/web.stdout.log`: Application stdout
- `/var/log/web.error.log`: Application errors

## 🔄 Redeployment

### After Code Changes
1. Update your code
2. Run `deploy.bat` to create new package
3. Upload to Elastic Beanstalk
4. Monitor deployment

### After Configuration Changes
1. Update `.ebextensions/*.config` files
2. Deploy to trigger configuration changes
3. Check logs for any errors

## 📞 Support

If you encounter issues:
1. Check the logs mentioned above
2. Verify database connectivity
3. Ensure all configuration files are correct
4. Test locally before deploying

## ✅ Success Indicators

Your deployment is successful when:
- ✅ Elastic Beanstalk environment shows "Healthy"
- ✅ Application responds to HTTP requests
- ✅ Database connection test passes
- ✅ No errors in `/var/log/eb-engine.log` 
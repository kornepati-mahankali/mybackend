# E-Procurement MySQL Database Integration

This document explains how to set up and use the MySQL database for storing e-procurement data when users click the "Merge All" button.

## 🎯 **Problem Solved**

You were seeing an empty `tender` table in phpMyAdmin because:
1. The original solution was designed for **PostgreSQL**
2. You're using **MySQL** (as shown in your phpMyAdmin screenshot)
3. The table structure didn't match your database system

## 📋 **Database Schema**

### Table: `eprocurement_tenders`

The main table that stores all merged e-procurement data in MySQL:

```sql
CREATE TABLE eprocurement_tenders (
    id VARCHAR(36) PRIMARY KEY,
    bid_user VARCHAR(100),
    tender_id VARCHAR(100),
    name_of_work TEXT,
    tender_category VARCHAR(50),
    department VARCHAR(100),
    quantity VARCHAR(50),
    emd DECIMAL(15, 2),
    exemption VARCHAR(50),
    ecv DECIMAL(20, 2),
    state_name VARCHAR(100),
    location VARCHAR(100),
    apply_mode VARCHAR(50),
    website VARCHAR(100),
    document_link TEXT,
    closing_date DATE,
    pincode VARCHAR(10),
    attachments TEXT,
    source_session_id VARCHAR(100),
    source_file VARCHAR(255),
    merge_session_id VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_tender_id (tender_id),
    INDEX idx_merge_session (merge_session_id),
    INDEX idx_created_at (created_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
```

## 🚀 **Quick Setup (3 Steps)**

### Step 1: Install Dependencies

```bash
cd backend
pip install -r requirements-db.txt
npm install mysql2 dotenv
```

### Step 2: Set Up Database

```bash
# Option A: Using the setup script (Recommended)
node setup-mysql.js

# Option B: Manual SQL execution
mysql -u root -p toolinformation < create_eprocurement_table_mysql.sql
```

### Step 3: Configure Environment

Create/update `.env` file in the backend directory:

```env
# MySQL Database Configuration
DB_HOST=localhost
DB_PORT=3307
DB_USER=root
DB_PASSWORD=your_password_here
DB_NAME=toolinformation

# Server Configuration
BACKEND_URL=http://127.0.0.1:5023
```

## 🔧 **Detailed Setup Instructions**

### 1. **Install Python Dependencies**

```bash
cd backend
pip install mysql-connector-python==8.2.0 pandas==2.1.4 python-dotenv==1.0.0
```

### 2. **Install Node.js Dependencies**

```bash
npm install mysql2 dotenv
```

### 3. **Database Setup**

#### **Option A: Automated Setup (Recommended)**

```bash
node setup-mysql.js
```

This script will:
- ✅ Connect to your MySQL database
- ✅ Create the `eprocurement_tenders` table
- ✅ Add proper indexes
- ✅ Verify the setup
- ✅ Create a `.env` file if it doesn't exist

#### **Option B: Manual Setup**

1. **Open phpMyAdmin** (as you did before)
2. **Select the `toolinformation` database**
3. **Go to SQL tab**
4. **Run the SQL script**:

```sql
USE toolinformation;

CREATE TABLE IF NOT EXISTS eprocurement_tenders (
    id VARCHAR(36) PRIMARY KEY,
    bid_user VARCHAR(100),
    tender_id VARCHAR(100),
    name_of_work TEXT,
    tender_category VARCHAR(50),
    department VARCHAR(100),
    quantity VARCHAR(50),
    emd DECIMAL(15, 2),
    exemption VARCHAR(50),
    ecv DECIMAL(20, 2),
    state_name VARCHAR(100),
    location VARCHAR(100),
    apply_mode VARCHAR(50),
    website VARCHAR(100),
    document_link TEXT,
    closing_date DATE,
    pincode VARCHAR(10),
    attachments TEXT,
    source_session_id VARCHAR(100),
    source_file VARCHAR(255),
    merge_session_id VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_tender_id (tender_id),
    INDEX idx_merge_session (merge_session_id),
    INDEX idx_created_at (created_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
```

### 4. **Start the MySQL-Compatible Server**

```bash
python eproc_server_mysql.py
```

## 🔍 **Verification Steps**

### 1. **Check Table Creation**

In phpMyAdmin:
1. Go to `toolinformation` database
2. Look for `eprocurement_tenders` table
3. Click on "Browse" to see the table structure

### 2. **Test Database Connection**

```bash
# Test the connection
python -c "
from database_operations_mysql import EProcurementDBMySQL
db = EProcurementDBMySQL()
db.create_table_if_not_exists()
print('✅ Database connection successful!')
"
```

### 3. **Check Server Health**

```bash
curl http://127.0.0.1:5023/api/health
```

Should return:
```json
{
  "status": "healthy",
  "server": "eproc_server_mysql.py"
}
```

## 📊 **How It Works**

### When User Clicks "Merge All" Button:

1. **Frontend** → Calls `handleEprocGlobalMerge()`
2. **API** → `POST /api/merge-global`
3. **Backend** → Merges Excel files into DataFrame
4. **MySQL Database** → Stores each tender record in `eprocurement_tenders` table
5. **Response** → Returns success with record counts

### Data Flow:

```
Excel Files → Pandas DataFrame → MySQL Database Table
     ↓              ↓                    ↓
  Scraped    →   Merged      →   Stored in
  Data       →   Data        →   MySQL (toolinformation)
```

## 🗄️ **Database Operations**

### **Store Data**
- **Method**: `store_merged_data()`
- **Function**: Stores DataFrame data in MySQL
- **Duplicate Handling**: Updates existing records based on `tender_id`

### **Retrieve Data**
- **Method**: `get_merged_data()`
- **Function**: Retrieves data with pagination and filtering
- **API**: `GET /api/eprocurement-data`

### **Delete Data**
- **Method**: `delete_merged_data()`
- **Function**: Deletes records by merge session
- **API**: `DELETE /api/eprocurement-data/<session_id>`

## 📈 **API Endpoints**

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/merge-global` | POST | Store merged data (triggered by Merge All button) |
| `/api/eprocurement-data` | GET | Retrieve stored data with pagination |
| `/api/eprocurement-data/<id>` | DELETE | Delete data by merge session |
| `/api/merge-history` | GET | Get merge operation history |

## 🔧 **Troubleshooting**

### **Common Issues:**

#### 1. **"Table not showing" in phpMyAdmin**
- ✅ Run `node setup-mysql.js` to create the table
- ✅ Check if you're in the correct database (`toolinformation`)
- ✅ Refresh phpMyAdmin after table creation

#### 2. **Database Connection Failed**
```bash
# Check your .env file
cat .env

# Test connection manually
mysql -u root -p -h localhost -P 3307 toolinformation
```

#### 3. **"Module not found" errors**
```bash
# Install missing dependencies
pip install mysql-connector-python pandas python-dotenv
npm install mysql2 dotenv
```

#### 4. **Port 3307 not accessible**
- Check if MySQL is running on port 3307
- Update `.env` file with correct port
- Try default port 3306 if needed

### **Debug Commands:**

```bash
# Check table exists
mysql -u root -p toolinformation -e "SHOW TABLES LIKE 'eprocurement_tenders';"

# Check table structure
mysql -u root -p toolinformation -e "DESCRIBE eprocurement_tenders;"

# Check for data
mysql -u root -p toolinformation -e "SELECT COUNT(*) FROM eprocurement_tenders;"
```

## 🎉 **Success Indicators**

After setup, you should see:

1. ✅ **phpMyAdmin**: `eprocurement_tenders` table visible
2. ✅ **Server**: `python eproc_server_mysql.py` runs without errors
3. ✅ **Health Check**: `http://127.0.0.1:5023/api/health` returns success
4. ✅ **Merge All Button**: Stores data in MySQL when clicked

## 📝 **Next Steps**

1. **Test the Merge All button** in your e-procurement tool
2. **Check phpMyAdmin** to see data being stored
3. **Use the API endpoints** to retrieve and manage data
4. **Monitor logs** for any database operations

## 🆘 **Need Help?**

If you encounter issues:

1. **Check the logs** in the terminal running the server
2. **Verify database connection** using the debug commands
3. **Ensure all dependencies** are installed correctly
4. **Check the `.env` file** has correct MySQL credentials

The MySQL solution is now ready to store your e-procurement data when users click the "Merge All" button! 🚀 
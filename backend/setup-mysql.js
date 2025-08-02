const mysql = require('mysql2/promise');
require('dotenv').config();

async function setupMySQLDatabase() {
  let connection;
  
  try {
    console.log('Setting up MySQL database for E-Procurement...');

    // Create connection
    connection = await mysql.createConnection({
      host: process.env.DB_HOST || 'localhost',
      port: process.env.DB_PORT || 3307,
      user: process.env.DB_USER || 'root',
      password: process.env.DB_PASSWORD || '',
      database: process.env.DB_NAME || 'toolinformation'
    });

    console.log('✅ Connected to MySQL database');

    // Create eprocurement_tenders table
    const createTableSQL = `
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
      ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
    `;

    await connection.execute(createTableSQL);
    console.log('✅ eprocurement_tenders table created successfully');

    // Add table comment
    await connection.execute(`
      ALTER TABLE eprocurement_tenders 
      COMMENT = 'Stores merged e-procurement tender data from the scraper'
    `);

    // Verify table exists
    const [rows] = await connection.execute(`
      SELECT COUNT(*) as count 
      FROM information_schema.tables 
      WHERE table_schema = ? AND table_name = 'eprocurement_tenders'
    `, [process.env.DB_NAME || 'toolinformation']);

    if (rows[0].count > 0) {
      console.log('✅ Table verification successful');
    } else {
      console.log('❌ Table verification failed');
    }

    // Show table structure
    const [columns] = await connection.execute(`
      DESCRIBE eprocurement_tenders
    `);

    console.log('\n📋 Table Structure:');
    console.table(columns);

    console.log('\n🎉 MySQL database setup completed successfully!');
    console.log('\n📝 Next steps:');
    console.log('1. Install Python dependencies: pip install -r requirements-db.txt');
    console.log('2. Set up environment variables in .env file');
    console.log('3. Run the MySQL-compatible server: python eproc_server_mysql.py');

  } catch (error) {
    console.error('❌ Database setup error:', error.message);
    
    if (error.code === 'ER_ACCESS_DENIED_ERROR') {
      console.log('\n💡 Troubleshooting:');
      console.log('- Check your MySQL credentials in .env file');
      console.log('- Ensure MySQL server is running on port 3307');
      console.log('- Verify database "toolinformation" exists');
    }
    
    if (error.code === 'ECONNREFUSED') {
      console.log('\n💡 Troubleshooting:');
      console.log('- Make sure MySQL server is running');
      console.log('- Check if port 3307 is correct');
      console.log('- Verify host address');
    }
    
  } finally {
    if (connection) {
      await connection.end();
      console.log('🔌 Database connection closed');
    }
  }
}

// Create .env file if it doesn't exist
const fs = require('fs');
const path = require('path');

const envPath = path.join(__dirname, '.env');
if (!fs.existsSync(envPath)) {
  const envContent = `# MySQL Database Configuration
DB_HOST=localhost
DB_PORT=3307
DB_USER=root
DB_PASSWORD=
DB_NAME=toolinformation

# Server Configuration
BACKEND_URL=http://127.0.0.1:5023
`;

  fs.writeFileSync(envPath, envContent);
  console.log('📄 Created .env file with default configuration');
  console.log('⚠️  Please update the .env file with your actual MySQL credentials');
}

setupMySQLDatabase(); 
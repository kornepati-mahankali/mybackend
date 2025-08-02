const { Pool } = require('pg');
require('dotenv').config();

const pool = new Pool({
  connectionString: process.env.DATABASE_URL || 'postgresql://username:password@localhost:5432/scraper_db',
});

async function setupDatabase() {
  try {
    console.log('Setting up Super Scraper database...');

    // Create users table
    await pool.query(`
      CREATE TABLE IF NOT EXISTS users (
        id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
        email VARCHAR(255) UNIQUE NOT NULL,
        username VARCHAR(100) NOT NULL,
        password_hash VARCHAR(255) NOT NULL,
        role VARCHAR(20) DEFAULT 'user',
        created_at TIMESTAMP DEFAULT NOW(),
        updated_at TIMESTAMP DEFAULT NOW(),
        last_login TIMESTAMP,
        is_active BOOLEAN DEFAULT true
      );
    `);

    // Create tools table
    await pool.query(`
      CREATE TABLE IF NOT EXISTS tools (
        id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
        name VARCHAR(255) NOT NULL,
        category VARCHAR(50) NOT NULL,
        description TEXT,
        states JSONB,
        icon VARCHAR(50),
        is_active BOOLEAN DEFAULT true,
        created_by UUID REFERENCES users(id),
        created_at TIMESTAMP DEFAULT NOW(),
        updated_at TIMESTAMP DEFAULT NOW()
      );
    `);

    // Create tools_1 table (for job tracking)
    await pool.query(`
      CREATE TABLE IF NOT EXISTS tools_1 (
        id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
        user_id UUID REFERENCES users(id),
        tool_id UUID REFERENCES tools(id),
        state VARCHAR(100),
        username VARCHAR(255),
        starting_name VARCHAR(255),
        status VARCHAR(20) DEFAULT 'pending',
        progress INTEGER DEFAULT 0,
        start_time TIMESTAMP,
        end_time TIMESTAMP,
        output_files JSONB,
        logs JSONB,
        created_at TIMESTAMP DEFAULT NOW()
      );
    `);

    // Create eprocurement_tenders table (for storing merged e-procurement data)
    await pool.query(`
      CREATE TABLE IF NOT EXISTS eprocurement_tenders (
        id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
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
        created_at TIMESTAMP DEFAULT NOW(),
        updated_at TIMESTAMP DEFAULT NOW()
      );
    `);

    // Create index on tender_id for faster lookups
    await pool.query(`
      CREATE INDEX IF NOT EXISTS idx_eprocurement_tenders_tender_id 
      ON eprocurement_tenders(tender_id);
    `);

    // Create index on merge_session_id for filtering by merge session
    await pool.query(`
      CREATE INDEX IF NOT EXISTS idx_eprocurement_tenders_merge_session 
      ON eprocurement_tenders(merge_session_id);
    `);

    // Insert default super admin user
    const bcrypt = require('bcryptjs');
    const hashedPassword = await bcrypt.hash('SuperScraper2024!', 10);
    
    await pool.query(`
      INSERT INTO users (email, username, password_hash, role) 
      VALUES ($1, $2, $3, $4) 
      ON CONFLICT (email) DO NOTHING
    `, ['super@scraper.com', 'Super Admin', hashedPassword, 'super_admin']);

    // Insert default admin user
    const adminPassword = await bcrypt.hash('admin123', 10);
    await pool.query(`
      INSERT INTO users (email, username, password_hash, role) 
      VALUES ($1, $2, $3, $4) 
      ON CONFLICT (email) DO NOTHING
    `, ['admin@scraper.com', 'Admin', adminPassword, 'admin']);

    // Insert default tools
    const tools = [
      {
        name: 'Gem Portal Scraper',
        category: 'gem',
        description: 'Extract tender data from Government e-Marketplace portal',
        states: ['Delhi', 'Mumbai', 'Chennai', 'Kolkata', 'Bangalore', 'Hyderabad', 'Pune', 'Ahmedabad'],
        icon: 'gem'
      },
      {
        name: 'Global Trade Monitor',
        category: 'global',
        description: 'Monitor international trade opportunities',
        states: ['USA', 'UK', 'Germany', 'France', 'Japan', 'Singapore', 'Australia', 'Canada'],
        icon: 'globe'
      },
      {
        name: 'E-Procurement Monitor',
        category: 'eprocurement',
        description: 'Monitor e-procurement platforms for new opportunities',
        states: ['Central Govt', 'State Govt', 'PSU', 'Private', 'International'],
        icon: 'shopping-cart'
      }
    ];

    for (const tool of tools) {
      await pool.query(`
        INSERT INTO tools (name, category, description, states, icon) 
        VALUES ($1, $2, $3, $4, $5) 
        ON CONFLICT DO NOTHING
      `, [tool.name, tool.category, tool.description, JSON.stringify(tool.states), tool.icon]);
    }

    console.log('Database setup completed successfully!');
    console.log('Default accounts created:');
    console.log('Super Admin: super@scraper.com / SuperScraper2024!');
    console.log('Admin: admin@scraper.com / admin123');
    
  } catch (error) {
    console.error('Database setup error:', error);
  } finally {
    await pool.end();
  }
}

setupDatabase();
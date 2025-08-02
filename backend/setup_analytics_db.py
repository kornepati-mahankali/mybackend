#!/usr/bin/env python3
"""
Database setup script for Analytics API
Creates the necessary tables if they don't exist
"""

import pymysql
import os
from datetime import datetime

# Database configuration
DB_CONFIG = {
    'host': '127.0.0.1',
    'port': 3307,
    'user': 'root',
    'password': 'thanuja',
    'db': 'toolinformation',
    'charset': 'utf8mb4',
    'cursorclass': pymysql.cursors.DictCursor
}

def create_tables():
    """Create the necessary tables for analytics"""
    try:
        connection = pymysql.connect(**DB_CONFIG)
        
        with connection:
            with connection.cursor() as cursor:
                print("Setting up analytics database tables...")
                
                # Create jobs table if it doesn't exist
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS jobs (
                        id VARCHAR(36) PRIMARY KEY,
                        user_id VARCHAR(36),
                        tool_id VARCHAR(36),
                        state VARCHAR(100),
                        username VARCHAR(255),
                        starting_name VARCHAR(255),
                        status ENUM('pending', 'running', 'completed', 'failed', 'stopped') DEFAULT 'pending',
                        progress INT DEFAULT 0,
                        start_time TIMESTAMP NULL,
                        end_time TIMESTAMP NULL,
                        data_volume DECIMAL(10,2) DEFAULT 0,
                        output_files JSON,
                        logs JSON,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                        INDEX idx_user_id (user_id),
                        INDEX idx_status (status),
                        INDEX idx_created_at (created_at),
                        INDEX idx_tool_id (tool_id)
                    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
                """)
                
                # Create tools table if it doesn't exist
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS tools (
                        id VARCHAR(36) PRIMARY KEY,
                        name VARCHAR(255) NOT NULL,
                        category VARCHAR(50) NOT NULL,
                        description TEXT,
                        states JSON,
                        icon VARCHAR(50),
                        is_active BOOLEAN DEFAULT true,
                        created_by VARCHAR(36),
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                        INDEX idx_category (category),
                        INDEX idx_is_active (is_active)
                    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
                """)
                
                # Create users table if it doesn't exist
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS users (
                        id VARCHAR(36) PRIMARY KEY,
                        email VARCHAR(255) UNIQUE NOT NULL,
                        username VARCHAR(100) NOT NULL,
                        password_hash VARCHAR(255) NOT NULL,
                        role ENUM('user', 'admin', 'super_admin') DEFAULT 'user',
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                        last_login TIMESTAMP NULL,
                        is_active BOOLEAN DEFAULT true,
                        INDEX idx_email (email),
                        INDEX idx_role (role),
                        INDEX idx_is_active (is_active)
                    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
                """)
                
                # Insert some sample tools if they don't exist
                sample_tools = [
                    {
                        'id': 'gem-portal-001',
                        'name': 'Gem Portal',
                        'category': 'Government',
                        'description': 'Scrape data from Gem Portal',
                        'icon': 'gem',
                        'states': '["Maharashtra", "Delhi", "Karnataka", "Tamil Nadu"]'
                    },
                    {
                        'id': 'global-trade-001',
                        'name': 'Global Trade',
                        'category': 'International',
                        'description': 'Monitor global trade data',
                        'icon': 'globe',
                        'states': '["USA", "Europe", "Asia", "Africa"]'
                    },
                    {
                        'id': 'eprocurement-001',
                        'name': 'E-Procurement',
                        'category': 'Government',
                        'description': 'E-Procurement tender monitoring',
                        'icon': 'file-text',
                        'states': '["Central Govt", "State Govt", "Municipal"]'
                    },
                    {
                        'id': 'universal-extractor-001',
                        'name': 'Universal Extractor',
                        'category': 'General',
                        'description': 'Universal web data extraction tool',
                        'icon': 'download',
                        'states': '["Web Scraping", "Data Mining", "Content Extraction"]'
                    },
                    {
                        'id': 'market-intelligence-001',
                        'name': 'Market Intelligence',
                        'category': 'Business',
                        'description': 'Market intelligence and analysis',
                        'icon': 'trending-up',
                        'states': '["Market Analysis", "Competitor Research", "Industry Trends"]'
                    }
                ]
                
                for tool in sample_tools:
                    cursor.execute("""
                        INSERT IGNORE INTO tools (id, name, category, description, icon, states)
                        VALUES (%s, %s, %s, %s, %s, %s)
                    """, (tool['id'], tool['name'], tool['category'], tool['description'], tool['icon'], tool['states']))
                
                # Insert sample user if it doesn't exist
                cursor.execute("""
                    INSERT IGNORE INTO users (id, email, username, password_hash, role)
                    VALUES ('admin-001', 'admin@example.com', 'admin', 'hashed_password_here', 'admin')
                """)
                
                # Insert some sample jobs for testing
                sample_jobs = [
                    {
                        'id': 'job-001',
                        'user_id': 'admin-001',
                        'tool_id': 'gem-portal-001',
                        'state': 'Maharashtra',
                        'status': 'completed',
                        'progress': 100,
                        'start_time': datetime.now().replace(hour=10, minute=30),
                        'end_time': datetime.now().replace(hour=10, minute=34, second=12),
                        'data_volume': 1250.5,
                        'created_at': datetime.now().replace(hour=10, minute=30)
                    },
                    {
                        'id': 'job-002',
                        'user_id': 'admin-001',
                        'tool_id': 'eprocurement-001',
                        'state': 'Central Govt',
                        'status': 'completed',
                        'progress': 100,
                        'start_time': datetime.now().replace(hour=8, minute=15),
                        'end_time': datetime.now().replace(hour=8, minute=20, second=30),
                        'data_volume': 890.2,
                        'created_at': datetime.now().replace(hour=8, minute=15)
                    },
                    {
                        'id': 'job-003',
                        'user_id': 'admin-001',
                        'tool_id': 'global-trade-001',
                        'state': 'USA',
                        'status': 'failed',
                        'progress': 45,
                        'start_time': datetime.now().replace(hour=6, minute=0),
                        'end_time': datetime.now().replace(hour=6, minute=2, second=15),
                        'data_volume': 0,
                        'created_at': datetime.now().replace(hour=6, minute=0)
                    },
                    {
                        'id': 'job-004',
                        'user_id': 'admin-001',
                        'tool_id': 'universal-extractor-001',
                        'state': 'Web Scraping',
                        'status': 'completed',
                        'progress': 100,
                        'start_time': datetime.now().replace(hour=4, minute=30),
                        'end_time': datetime.now().replace(hour=4, minute=35, second=45),
                        'data_volume': 2100.8,
                        'created_at': datetime.now().replace(hour=4, minute=30)
                    }
                ]
                
                for job in sample_jobs:
                    cursor.execute("""
                        INSERT IGNORE INTO jobs (id, user_id, tool_id, state, status, progress, start_time, end_time, data_volume, created_at)
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    """, (job['id'], job['user_id'], job['tool_id'], job['state'], job['status'], 
                          job['progress'], job['start_time'], job['end_time'], job['data_volume'], job['created_at']))
                
                connection.commit()
                print("✅ Analytics database tables created successfully!")
                print("📊 Sample data inserted for testing")
                
    except Exception as e:
        print(f"❌ Error setting up database: {e}")
        raise

if __name__ == "__main__":
    create_tables() 
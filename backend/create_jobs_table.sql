-- Create jobs table for Admin Metrics API
-- Run this script in your MySQL database to enable real job tracking

USE toolinformation;

-- Drop existing table if it exists
DROP TABLE IF EXISTS jobs;

-- Create jobs table with updated schema
CREATE TABLE IF NOT EXISTS jobs (
    id INT AUTO_INCREMENT PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    description TEXT,
    status ENUM('queued', 'running', 'completed', 'failed') DEFAULT 'queued',
    priority INT DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    started_at TIMESTAMP NULL,
    completed_at TIMESTAMP NULL,
    progress INT DEFAULT 0 COMMENT 'Progress percentage (0-100)',
    user_id VARCHAR(100),
    metadata JSON COMMENT 'Additional job metadata including downloads count'
);

-- Create indexes for better performance
CREATE INDEX idx_jobs_status ON jobs(status);
CREATE INDEX idx_jobs_created_at ON jobs(created_at);
CREATE INDEX idx_jobs_completed_at ON jobs(completed_at);
CREATE INDEX idx_jobs_user_id ON jobs(user_id);

-- Insert sample data with realistic metadata
INSERT INTO jobs (title, description, status, priority, progress, user_id, metadata, created_at, updated_at, started_at, completed_at) VALUES
('Gem Portal Scraper', 'Scraping GEM portal data for government tenders', 'completed', 1, 100, 'user1', '{"downloads": 1247, "records_extracted": 1247, "portal": "gem"}', NOW() - INTERVAL 2 MINUTE, NOW() - INTERVAL 2 MINUTE, NOW() - INTERVAL 5 MINUTE, NOW() - INTERVAL 2 MINUTE),
('Global Trade Monitor', 'Processing USA market data for trade opportunities', 'running', 2, 65, 'user2', '{"downloads": 856, "records_extracted": 856, "market": "usa"}', NOW() - INTERVAL 5 MINUTE, NOW() - INTERVAL 5 MINUTE, NOW() - INTERVAL 5 MINUTE, NULL),
('E-Procurement Scan', 'Scanning e-procurement portals for new tenders', 'failed', 1, 30, 'user1', '{"downloads": 0, "error": "Connection timeout", "retry_count": 3}', NOW() - INTERVAL 12 MINUTE, NOW() - INTERVAL 12 MINUTE, NOW() - INTERVAL 15 MINUTE, NULL),
('Market Intelligence', 'Analyzing market trends and opportunities', 'completed', 3, 100, 'user3', '{"downloads": 856, "opportunities_found": 856, "analysis_type": "trend"}', NOW() - INTERVAL 18 MINUTE, NOW() - INTERVAL 18 MINUTE, NOW() - INTERVAL 25 MINUTE, NOW() - INTERVAL 18 MINUTE),
('AP Portal Scraper', 'Scraping Andhra Pradesh government portal', 'queued', 2, 0, 'user1', '{"downloads": 0, "portal": "ap"}', NOW() - INTERVAL 1 HOUR, NOW() - INTERVAL 1 HOUR, NULL, NULL),
('IREPS Data Collection', 'Collecting IREPS portal data', 'queued', 1, 0, 'user2', '{"downloads": 0, "portal": "ireps"}', NOW() - INTERVAL 2 HOUR, NOW() - INTERVAL 2 HOUR, NULL, NULL),
('Tender Analysis', 'Analyzing tender patterns and statistics', 'running', 3, 45, 'user3', '{"downloads": 234, "analysis_progress": 45}', NOW() - INTERVAL 30 MINUTE, NOW() - INTERVAL 30 MINUTE, NOW() - INTERVAL 30 MINUTE, NULL),
('Contract Monitoring', 'Monitoring contract awards and updates', 'completed', 2, 100, 'user1', '{"downloads": 567, "contracts_found": 567}', NOW() - INTERVAL 1 DAY, NOW() - INTERVAL 1 DAY, NOW() - INTERVAL 1 DAY + INTERVAL 10 MINUTE, NOW() - INTERVAL 1 DAY - INTERVAL 5 MINUTE),
('Vendor Database Update', 'Updating vendor information database', 'completed', 1, 100, 'user2', '{"downloads": 1234, "vendors_updated": 1234}', NOW() - INTERVAL 2 DAY, NOW() - INTERVAL 2 DAY, NOW() - INTERVAL 2 DAY + INTERVAL 15 MINUTE, NOW() - INTERVAL 2 DAY - INTERVAL 10 MINUTE),
('Category Analysis', 'Analyzing tender categories and trends', 'failed', 2, 75, 'user3', '{"downloads": 890, "error": "Database connection lost", "records_processed": 890}', NOW() - INTERVAL 3 DAY, NOW() - INTERVAL 3 DAY, NOW() - INTERVAL 3 DAY + INTERVAL 5 MINUTE, NULL),
('Location Data Scraper', 'Scraping location-based tender data', 'completed', 1, 100, 'user1', '{"downloads": 432, "locations_processed": 432}', NOW() - INTERVAL 4 DAY, NOW() - INTERVAL 4 DAY, NOW() - INTERVAL 4 DAY + INTERVAL 20 MINUTE, NOW() - INTERVAL 4 DAY - INTERVAL 15 MINUTE),
('Historical Data Analysis', 'Analyzing historical tender patterns', 'running', 3, 80, 'user2', '{"downloads": 1567, "analysis_progress": 80}', NOW() - INTERVAL 6 HOUR, NOW() - INTERVAL 6 HOUR, NOW() - INTERVAL 6 HOUR, NULL);

-- Show table structure
DESCRIBE jobs;

-- Show sample data
SELECT id, title, status, priority, progress, created_at, JSON_EXTRACT(metadata, '$.downloads') as downloads FROM jobs LIMIT 5; 
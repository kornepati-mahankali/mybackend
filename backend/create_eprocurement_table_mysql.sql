-- Create eprocurement_tenders table for storing merged e-procurement data
-- Run this script in your MySQL database (toolinformation)

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

-- Add comments for documentation
ALTER TABLE eprocurement_tenders 
COMMENT = 'Stores merged e-procurement tender data from the scraper';

-- Verify table creation
SELECT 'eprocurement_tenders table created successfully' as status; 
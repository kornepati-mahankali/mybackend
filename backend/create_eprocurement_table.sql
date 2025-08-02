-- Create eprocurement_tenders table for storing merged e-procurement data
-- Run this script in your PostgreSQL database

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

-- Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_eprocurement_tenders_tender_id 
ON eprocurement_tenders(tender_id);

CREATE INDEX IF NOT EXISTS idx_eprocurement_tenders_merge_session 
ON eprocurement_tenders(merge_session_id);

CREATE INDEX IF NOT EXISTS idx_eprocurement_tenders_created_at 
ON eprocurement_tenders(created_at);

-- Add comments for documentation
COMMENT ON TABLE eprocurement_tenders IS 'Stores merged e-procurement tender data from the scraper';
COMMENT ON COLUMN eprocurement_tenders.tender_id IS 'Unique identifier for the tender';
COMMENT ON COLUMN eprocurement_tenders.merge_session_id IS 'Identifier for the merge operation that created this record';
COMMENT ON COLUMN eprocurement_tenders.source_session_id IS 'Original scraping session ID';
COMMENT ON COLUMN eprocurement_tenders.source_file IS 'Original Excel file name';

-- Verify table creation
SELECT 'eprocurement_tenders table created successfully' as status; 
-- Update jobs table with proper data for dashboard
-- First, let's see what we have
SELECT COUNT(*) as total_jobs FROM jobs;

-- Update existing jobs with proper status values and metadata
UPDATE jobs 
SET 
    status = CASE 
        WHEN status = 'pending' THEN 'queued'
        WHEN status = 'running' THEN 'running'
        ELSE status
    END,
    metadata = CASE 
        WHEN id = 1 THEN '{"downloads": 1247, "records_extracted": 1247, "portal": "gem"}'
        WHEN id = 2 THEN '{"downloads": 856, "records_extracted": 856, "market": "usa"}'
        WHEN id = 3 THEN '{"downloads": 0, "error": "Connection timeout", "retry_count": 3}'
        WHEN id = 4 THEN '{"downloads": 567, "opportunities_found": 567, "analysis_type": "trend"}'
        WHEN id = 5 THEN '{"downloads": 234, "analysis_progress": 45}'
        WHEN id = 6 THEN '{"downloads": 1234, "vendors_updated": 1234}'
        WHEN id = 7 THEN '{"downloads": 890, "error": "Database connection lost", "records_processed": 890}'
        WHEN id = 8 THEN '{"downloads": 432, "locations_processed": 432}'
        WHEN id = 9 THEN '{"downloads": 1567, "analysis_progress": 80}'
        WHEN id = 10 THEN '{"downloads": 0, "portal": "ap"}'
        WHEN id = 11 THEN '{"downloads": 0, "portal": "ireps"}'
        WHEN id = 12 THEN '{"downloads": 0, "portal": "eproc"}'
        ELSE '{"downloads": 0, "status": "unknown"}'
    END,
    title = CASE 
        WHEN id = 1 THEN 'Gem Portal Scraper'
        WHEN id = 2 THEN 'Global Trade Monitor'
        WHEN id = 3 THEN 'E-Procurement Scan'
        WHEN id = 4 THEN 'Market Intelligence'
        WHEN id = 5 THEN 'Tender Analysis'
        WHEN id = 6 THEN 'Vendor Database Update'
        WHEN id = 7 THEN 'Category Analysis'
        WHEN id = 8 THEN 'Location Data Scraper'
        WHEN id = 9 THEN 'Historical Data Analysis'
        WHEN id = 10 THEN 'AP Portal Scraper'
        WHEN id = 11 THEN 'IREPS Data Collection'
        WHEN id = 12 THEN 'Contract Monitoring'
        ELSE CONCAT('Data Scraping Job #', id)
    END,
    completed_at = CASE 
        WHEN status = 'completed' THEN NOW() - INTERVAL FLOOR(RAND() * 24) HOUR
        ELSE NULL
    END
WHERE id <= 12;

-- Set some jobs as completed today
UPDATE jobs 
SET 
    status = 'completed',
    completed_at = NOW() - INTERVAL FLOOR(RAND() * 6) HOUR
WHERE id IN (1, 4, 6, 8);

-- Set some jobs as failed
UPDATE jobs 
SET 
    status = 'failed',
    completed_at = NOW() - INTERVAL FLOOR(RAND() * 12) HOUR
WHERE id IN (3, 7);

-- Set some jobs as queued
UPDATE jobs 
SET status = 'queued'
WHERE id IN (10, 11, 12);

-- Show updated data
SELECT 
    id,
    title,
    status,
    JSON_EXTRACT(metadata, '$.downloads') as downloads,
    completed_at
FROM jobs 
ORDER BY updated_at DESC 
LIMIT 10; 
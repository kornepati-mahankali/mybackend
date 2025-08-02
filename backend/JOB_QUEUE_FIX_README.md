# Job Queue Issue Fix

## Problem Description

The admin panel was showing "0 Active Jobs" with "6 queued" jobs, indicating that jobs were getting stuck in the queue instead of being processed. This was caused by several issues:

1. **Database Mismatch**: The admin metrics API was looking for a `jobs` table in MySQL, but the actual job data was stored in the `tools_1` table in PostgreSQL.

2. **Simulated Job Processing**: The `startScrapingJob` function in `server.js` was only simulating job processing instead of actually running the scrapers.

3. **No Real Job Queue**: There was no proper job queue system to process pending jobs.

## Solution Implemented

### 1. Fixed Database Configuration

- Updated `admin_metrics_api.py` to use PostgreSQL instead of MySQL
- Changed table reference from `jobs` to `tools_1`
- Updated database queries to match the actual schema

### 2. Created Real Job Processor

- Created `job_processor.py` - a proper job queue system that:
  - Monitors the `tools_1` table for pending jobs
  - Processes jobs based on their tool category (gem, eprocurement, etc.)
  - Updates job status and progress in real-time
  - Handles job failures and timeouts

### 3. Updated Job Creation

- Modified `server.js` to queue jobs instead of simulating them
- Jobs are now properly marked as 'pending' and picked up by the job processor

### 4. Created Management Tools

- `clear_stuck_jobs.py` - Script to clear stuck jobs and reset the queue
- `start_services.py` - Startup script for all backend services

## How to Fix the Issue

### Step 1: Install Dependencies

```bash
cd backend
pip install psycopg2-binary
```

### Step 2: Clear Stuck Jobs

```bash
python clear_stuck_jobs.py
```

This will:
- Reset any jobs that have been running for more than 1 hour
- Reset any jobs that have been pending for more than 30 minutes
- Show you the current job status

### Step 3: Start the Services

```bash
python start_services.py
```

This will start:
- Admin Metrics API (port 8001)
- Job Processor (background service)

### Step 4: Verify the Fix

1. Check the admin panel - you should now see accurate job counts
2. Create a new job - it should be processed automatically
3. Monitor the job status in real-time

## Job Status Flow

1. **pending** - Job is queued and waiting to be processed
2. **running** - Job is currently being processed
3. **completed** - Job finished successfully
4. **failed** - Job failed due to an error
5. **stopped** - Job was manually stopped

## Troubleshooting

### If jobs are still stuck:

1. **Check the job processor logs**:
   ```bash
   # Look for job processor output in the console
   ```

2. **Clear all jobs and restart**:
   ```bash
   python clear_stuck_jobs.py --reset-all
   python start_services.py
   ```

3. **Check database connection**:
   - Ensure PostgreSQL is running
   - Verify database credentials in `admin_metrics_api.py` and `job_processor.py`

### If the admin panel shows incorrect counts:

1. **Restart the admin metrics API**:
   ```bash
   # Stop the current service and restart
   python start_services.py
   ```

2. **Check the database directly**:
   ```sql
   SELECT status, COUNT(*) FROM tools_1 GROUP BY status;
   ```

## File Changes Summary

- `admin_metrics_api.py` - Fixed database configuration and table references
- `job_processor.py` - New job queue system
- `server.js` - Updated job creation to use real queue
- `start_services.py` - New startup script
- `clear_stuck_jobs.py` - Job cleanup utility
- `requirements.txt` - Added psycopg2-binary dependency

## Expected Results

After implementing these fixes:

- ✅ Admin panel shows accurate job counts
- ✅ Jobs are processed automatically when created
- ✅ Real-time job status updates
- ✅ Proper error handling and job recovery
- ✅ No more stuck jobs in the queue

The job queue should now work properly, and you should see jobs moving from "pending" to "running" to "completed" status automatically. 
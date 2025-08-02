# E-Procurement Database Integration

This document explains how the e-procurement "Merge All" button now stores data in a PostgreSQL database.

## Database Schema

### Table: `eprocurement_tenders`

The main table that stores all merged e-procurement data:

```sql
CREATE TABLE eprocurement_tenders (
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
```

### Indexes

- `idx_eprocurement_tenders_tender_id` - For faster tender lookups
- `idx_eprocurement_tenders_merge_session` - For filtering by merge session

## Setup Instructions

### 1. Install Database Dependencies

```bash
cd backend
pip install -r requirements-db.txt
```

### 2. Set Up PostgreSQL Database

1. Install PostgreSQL if not already installed
2. Create a database named `scraper_db`
3. Set up the database schema:

```bash
cd backend
node setup-database.js
```

### 3. Configure Environment Variables

Create a `.env` file in the backend directory:

```env
DATABASE_URL=postgresql://username:password@localhost:5432/scraper_db
```

Replace `username`, `password`, and `localhost` with your actual PostgreSQL credentials.

## How It Works

### When User Clicks "Merge All" Button

1. **Frontend**: User clicks "Merge All" button in e-procurement tool
2. **Backend**: `handleEprocGlobalMerge()` function is called
3. **API Call**: Frontend makes POST request to `/api/merge-global`
4. **Data Processing**: 
   - Reads all Excel files from the session
   - Merges them into a single DataFrame
   - Saves merged file as CSV
5. **Database Storage**: 
   - Creates `EProcurementDB` instance
   - Calls `store_merged_data()` method
   - Stores each tender record in `eprocurement_tenders` table
6. **Response**: Returns success message with record counts

### Data Flow

```
Excel Files → Pandas DataFrame → Database Table
     ↓              ↓                ↓
  Scraped    →   Merged      →   Stored in
  Data       →   Data        →   PostgreSQL
```

## API Endpoints

### 1. Store Merged Data (Automatic)
- **Endpoint**: `POST /api/merge-global`
- **Trigger**: When user clicks "Merge All" button
- **Function**: Stores all merged data in database

### 2. Retrieve Data
- **Endpoint**: `GET /api/eprocurement-data`
- **Parameters**:
  - `merge_session_id` (optional): Filter by merge session
  - `limit` (default: 100): Number of records to return
  - `offset` (default: 0): Number of records to skip
- **Response**: JSON with tender data and metadata

### 3. Delete Data
- **Endpoint**: `DELETE /api/eprocurement-data/<merge_session_id>`
- **Function**: Deletes all records for a specific merge session

### 4. Get Merge History
- **Endpoint**: `GET /api/merge-history`
- **Function**: Returns metadata about all merge operations

## Database Operations Class

### `EProcurementDB` Class

Located in `backend/database_operations.py`

#### Key Methods:

1. **`store_merged_data(df, merge_session_id, source_session_id, source_file)`**
   - Stores DataFrame data in database
   - Handles duplicate detection (updates existing records)
   - Returns operation statistics

2. **`get_merged_data(merge_session_id, limit, offset)`**
   - Retrieves data from database
   - Supports pagination and filtering
   - Returns data with metadata

3. **`delete_merged_data(merge_session_id)`**
   - Deletes all records for a merge session
   - Returns deletion statistics

## Data Mapping

| Excel Column | Database Column | Type | Description |
|--------------|----------------|------|-------------|
| Bid User | bid_user | VARCHAR(100) | User who placed the bid |
| Tender ID | tender_id | VARCHAR(100) | Unique tender identifier |
| Name of Work | name_of_work | TEXT | Description of the work |
| Tender Category | tender_category | VARCHAR(50) | Category of tender |
| Department | department | VARCHAR(100) | Government department |
| Quantity | quantity | VARCHAR(50) | Quantity required |
| EMD | emd | DECIMAL(15,2) | Earnest Money Deposit |
| Exemption | exemption | VARCHAR(50) | EMD exemption status |
| ECV | ecv | DECIMAL(20,2) | Estimated Contract Value |
| State Name | state_name | VARCHAR(100) | State where tender is located |
| Location | location | VARCHAR(100) | Specific location |
| Apply Mode | apply_mode | VARCHAR(50) | Application method |
| Website | website | VARCHAR(100) | Source website |
| Document Link | document_link | TEXT | Link to tender documents |
| Closing Date | closing_date | DATE | Tender closing date |
| Pincode | pincode | VARCHAR(10) | Postal code |
| Attachments | attachments | TEXT | Document attachments |

## Error Handling

The system includes comprehensive error handling:

1. **Database Connection Errors**: Logged and reported to frontend
2. **Data Parsing Errors**: Individual record errors don't stop the process
3. **Duplicate Records**: Automatically updated instead of creating duplicates
4. **Invalid Data**: Skipped with logging

## Monitoring and Logging

- All database operations are logged
- Success/failure messages sent to frontend via WebSocket
- Record counts reported after each operation
- Error details logged for debugging

## Benefits

1. **Persistent Storage**: Data survives server restarts
2. **Query Capability**: Can search and filter data
3. **Data Integrity**: Prevents duplicate records
4. **Scalability**: Can handle large datasets
5. **Backup**: Database can be backed up easily
6. **Analytics**: Can run complex queries for insights

## Troubleshooting

### Common Issues:

1. **Database Connection Failed**
   - Check DATABASE_URL in .env file
   - Ensure PostgreSQL is running
   - Verify database credentials

2. **Table Not Found**
   - Run `node setup-database.js` to create tables
   - Check database permissions

3. **Data Not Stored**
   - Check logs for error messages
   - Verify DataFrame structure matches expected columns
   - Ensure tender_id is not empty

### Debug Commands:

```bash
# Check database connection
psql $DATABASE_URL -c "SELECT COUNT(*) FROM eprocurement_tenders;"

# View recent merge operations
psql $DATABASE_URL -c "SELECT * FROM eprocurement_tenders ORDER BY created_at DESC LIMIT 5;"

# Check for duplicates
psql $DATABASE_URL -c "SELECT tender_id, COUNT(*) FROM eprocurement_tenders GROUP BY tender_id HAVING COUNT(*) > 1;"
``` 
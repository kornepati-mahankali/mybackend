# Export Data Feature

## Overview
The Export Data feature allows users to download all their scraping data and job history from the Super Scraper Pro Dashboard. This feature is accessible from the Settings page under the "Data Management" section.

## Features

### 1. Export All Data (JSON)
- **Location**: Settings → Data Management → Export Data
- **Button**: "Export All Data" (Blue button)
- **Output**: JSON file containing:
  - User profile information
  - All scraping jobs and their status
  - Available tools
  - Summary statistics
  - List of available output files
  - Export timestamp

### 2. Export Output Files (ZIP)
- **Location**: Settings → Data Management → Export Data
- **Button**: "Export Output Files" (Green button)
- **Output**: ZIP file containing:
  - All output files from GEM, IREPS, E-Procurement, and AP scrapers
  - Organized by tool type and session
  - Excel and CSV files from scraping sessions

## Backend Implementation

### New API Endpoints

#### 1. `/api/export-data` (GET)
- **Authentication**: Required (Bearer token)
- **Response**: JSON file download
- **Data Included**:
  - User profile from database
  - Scraping jobs from `tools_1` table
  - Available tools from `tools` table
  - Output file information from filesystem
  - Summary statistics

#### 2. `/api/export-files` (GET)
- **Authentication**: Required (Bearer token)
- **Response**: ZIP file download
- **Contents**:
  - All files from `backend/outputs/` directory
  - Organized by tool type (gem, ireps, eproc, ap)
  - Includes session directories and their files

### Database Queries
The export functionality queries the following tables:
- `users` - User profile information
- `tools_1` - Scraping job history
- `tools` - Available tools

### File System Access
The export scans the following directories:
- `backend/outputs/gem/`
- `backend/outputs/ireps/`
- `backend/outputs/eproc/`
- `backend/outputs/ap/`

## Frontend Implementation

### Settings Component Updates
- Added export state management
- Added export functions with error handling
- Updated UI with two export buttons
- Added loading states and success messages

### API Service Updates
- Added `exportUserData()` method
- Added `exportOutputFiles()` method
- Proper error handling and authentication

## Installation

### Backend Dependencies
Add the archiver package to `backend/package.json`:
```json
{
  "dependencies": {
    "archiver": "^6.0.1"
  }
}
```

Install dependencies:
```bash
cd backend
npm install
```

## Usage

1. Navigate to Settings page
2. Click on "Data Management" in the left sidebar
3. Choose export option:
   - **Export All Data**: Downloads JSON with all user data
   - **Export Output Files**: Downloads ZIP with all output files

## Error Handling

### Backend Errors
- Database connection errors
- File system access errors
- Archive creation errors
- Authentication errors

### Frontend Errors
- Network errors
- Authentication token errors
- File download errors

## Security Considerations

- All endpoints require authentication
- Users can only export their own data
- File paths are validated to prevent directory traversal
- ZIP files are created securely with proper error handling

## File Naming Convention

### JSON Export
- Format: `user_data_{userId}_{timestamp}.json`
- Example: `user_data_123e4567-e89b-12d3-a456-426614174000_1703123456789.json`

### ZIP Export
- Format: `output_files_{userId}_{timestamp}.zip`
- Example: `output_files_123e4567-e89b-12d3-a456-426614174000_1703123456789.zip`

## Future Enhancements

1. **Selective Export**: Allow users to choose specific data types
2. **Scheduled Exports**: Automatic periodic data exports
3. **Export History**: Track and display previous exports
4. **Data Format Options**: CSV, XML, or other formats
5. **Cloud Storage**: Direct upload to cloud storage services
6. **Email Export**: Send exports via email
7. **Compression Options**: Different compression levels for ZIP files 
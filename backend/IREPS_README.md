# IREPS Server Setup

## Quick Start

To start the IREPS backend server:

1. **Navigate to the backend directory:**
   ```bash
   cd backend
   ```

2. **Start the server using the batch file:**
   ```bash
   start_ireps_server.bat
   ```
   
   Or manually:
   ```bash
   python start_ireps_server.py
   ```

3. **The server will start on:** http://localhost:5022

## Troubleshooting

### If Chrome doesn't open:
1. Make sure the IREPS server is running on port 5022
2. Check that `chromedriver.exe` exists in `backend/scrapers/edgedriver_win64/`
3. Check the console logs for any error messages
4. Make sure you have Chrome browser installed

### If you get dependency errors:
1. Install the requirements:
   ```bash
   pip install -r requirements.txt
   ```

### If the server won't start:
1. Make sure no other service is using port 5022
2. Check that Python 3.8+ is installed
3. Try running with administrator privileges

## API Endpoints

- `POST /ireps/open-edge` - Opens Chrome and navigates to IREPS
- `POST /ireps/start-scraping` - Starts the scraping process
- `GET /ireps/files` - Lists output files
- `POST /ireps/merge-files` - Merges all files and downloads
- `GET /ireps/download/{session_id}/{filename}` - Downloads a specific file
- `POST /ireps/delete-file` - Deletes a specific file
- `POST /ireps/stop-session` - Stops the current session
- `WebSocket /ws/logs` - Real-time log streaming 
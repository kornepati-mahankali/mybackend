# E-Procurement Backend

This is the backend server for the E-Procurement scraping tool. It provides a REST API and WebSocket interface for scraping tender data from E-Procurement websites.

## Features

- 🚀 **Web Scraping**: Automated scraping of tender data using Selenium and Edge WebDriver
- 📊 **Excel Export**: Generates Excel files for each scraped page
- 🔄 **Real-time Updates**: WebSocket communication for live scraping progress
- 📁 **File Management**: Session-based file organization and management
- 🔗 **REST API**: Complete REST API for all operations
- 🎯 **Captcha Handling**: Manual captcha input support
- 📈 **Data Merging**: Merge multiple Excel files into one

## Prerequisites

- Python 3.8 or higher
- Microsoft Edge browser installed
- Edge WebDriver (included in the project)

## Installation

1. **Clone the repository** (if not already done):
   ```bash
   git clone <repository-url>
   cd lavangam/backend
   ```

2. **Install Python dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Verify Edge WebDriver**:
   The Edge WebDriver should be located at:
   ```
   backend/scrapers/edgedriver_win64/msedgedriver.exe
   ```

## Quick Start

### Option 1: Using the startup script (Recommended)
```bash
python start_eproc_server.py
```

### Option 2: Direct server start
```bash
python eproc_server.py
```

The server will start on `http://localhost:5020`

## API Endpoints

### Health Check
- **GET** `/api/health` - Check server health

### Browser Control
- **POST** `/api/open-edge` - Open Edge browser with URL
  ```json
  {
    "url": "https://eprocurement.example.com"
  }
  ```

### Scraping Operations
- **POST** `/api/start-eproc-scraping` - Start scraping
  ```json
  {
    "base_url": "https://eprocurement.example.com",
    "tender_type": "O",
    "days_interval": 7,
    "start_page": 1,
    "captcha": "ABC123"
  }
  ```
- **POST** `/api/stop-scraping` - Stop current scraping

### Status & Monitoring
- **GET** `/api/status` - Get current scraping status
- **GET** `/api/sessions` - List all scraping sessions

### File Management
- **GET** `/api/files/<session_id>` - Get files for a session
- **GET** `/api/download/<session_id>/<filename>` - Download a file
- **POST** `/api/merge/<session_id>` - Merge session files

## WebSocket Events

The server provides real-time updates via WebSocket:

### Client → Server
- `connect` - Connect to server
- `disconnect` - Disconnect from server

### Server → Client
- `scraping_log` - Real-time scraping logs
- `scraping_started` - Scraping session started
- `scraping_complete` - Scraping completed
- `scraping_error` - Scraping error occurred
- `status_update` - Status update

## Usage Examples

### 1. Start Scraping Session

```javascript
// Frontend JavaScript example
const response = await fetch('http://localhost:5020/api/start-eproc-scraping', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({
    base_url: 'https://eprocurement.example.com',
    tender_type: 'O',  // O for Open, L for Limited
    days_interval: 7,
    start_page: 1,
    captcha: 'ABC123'
  })
});

const result = await response.json();
console.log('Session ID:', result.session_id);
```

### 2. WebSocket Connection

```javascript
// Frontend JavaScript example
import io from 'socket.io-client';

const socket = io('http://localhost:5020');

socket.on('connect', () => {
  console.log('Connected to server');
});

socket.on('scraping_log', (data) => {
  console.log('Log:', data.message);
});

socket.on('scraping_complete', (data) => {
  console.log('Scraping completed:', data.message);
  console.log('Session ID:', data.session_id);
});
```

### 3. Download Files

```javascript
// Download a specific file
const downloadUrl = `http://localhost:5020/api/download/${sessionId}/${filename}`;
window.open(downloadUrl, '_blank');

// Get list of files
const filesResponse = await fetch(`http://localhost:5020/api/files/${sessionId}`);
const files = await filesResponse.json();
console.log('Available files:', files.files);
```

## Configuration

### Environment Variables (Optional)
Create a `.env` file in the backend directory:

```env
FLASK_ENV=development
FLASK_DEBUG=True
PORT=5020
HOST=0.0.0.0
```

### Output Directory Structure
```
backend/
├── outputs/
│   └── eproc/
│       ├── 1752640923114/  # Session ID
│       │   ├── open-tenders_output_page-1.xlsx
│       │   ├── open-tenders_output_page-2.xlsx
│       │   └── merged_data_1752640923114.xlsx
│       └── 1752643029670/  # Another session
│           └── ...
```

## Troubleshooting

### Common Issues

1. **Edge Driver Not Found**
   - Ensure `msedgedriver.exe` is in `backend/scrapers/edgedriver_win64/`
   - Download the correct version for your Edge browser

2. **Port Already in Use**
   - Change the port in `eproc_server.py`
   - Or kill the process using the port

3. **Dependencies Missing**
   - Run `pip install -r requirements.txt`
   - Check Python version (3.8+ required)

4. **Scraping Fails**
   - Check if the website is accessible
   - Verify captcha input
   - Check browser automation settings

### Debug Mode

Run with debug mode for detailed logs:
```bash
python eproc_server.py
```

## Development

### Adding New Features

1. **New API Endpoint**:
   ```python
   @app.route('/api/new-endpoint', methods=['GET'])
   def new_endpoint():
       return jsonify({'message': 'New endpoint'})
   ```

2. **New WebSocket Event**:
   ```python
   @socketio.on('new_event')
   def handle_new_event(data):
       emit('response_event', {'data': 'response'})
   ```

### Testing

Test the API endpoints using curl or Postman:

```bash
# Health check
curl http://localhost:5020/api/health

# Start scraping
curl -X POST http://localhost:5020/api/start-eproc-scraping \
  -H "Content-Type: application/json" \
  -d '{"base_url":"https://example.com","tender_type":"O","days_interval":1,"start_page":1,"captcha":"ABC123"}'
```

## License

This project is part of the Lavangam E-Procurement system.

## Support

For issues and questions:
1. Check the troubleshooting section
2. Review the logs in the console
3. Check the WebSocket events for real-time updates
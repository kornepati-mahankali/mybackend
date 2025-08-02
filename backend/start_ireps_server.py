import uvicorn
import sys
import os

# Add the current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import the FastAPI app from scrapers/api.py
from scrapers.api import app

if __name__ == "__main__":
    print("Starting IREPS API server on port 5022...")
    print("Server will be available at: http://localhost:5022")
    print("Press Ctrl+C to stop the server")
    print("=" * 50)
    
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=5022,
        reload=True,
        log_level="info"
    ) 
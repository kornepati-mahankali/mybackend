"""
Configuration file for E-Procurement Backend
"""

import os
from pathlib import Path

# Base directory
BASE_DIR = Path(__file__).parent.absolute()

# Server configuration
SERVER_HOST = os.getenv('HOST', '0.0.0.0')
SERVER_PORT = int(os.getenv('PORT', 5021))
DEBUG = os.getenv('FLASK_DEBUG', 'True').lower() == 'true'

# Output directories
OUTPUT_BASE_DIR = BASE_DIR / 'outputs' / 'eproc'
SCRAPER_OUTPUT_DIR = BASE_DIR / 'scrapers' / 'OUTPUT'
DOWNLOAD_DIR = SCRAPER_OUTPUT_DIR / 'Downloaded_Documents'

# Edge driver configuration
EDGE_DRIVER_PATH = BASE_DIR / 'scrapers' / 'edgedriver_win64' / 'msedgedriver.exe'

# Scraping configuration
TIMEOUT = 6
DEFAULT_DAYS_INTERVAL = 1
DEFAULT_START_PAGE = 1

# File configuration
ALLOWED_EXTENSIONS = {'.xlsx', '.xls'}
MAX_FILE_SIZE = 100 * 1024 * 1024  # 100MB

# WebSocket configuration
SOCKETIO_CORS_ALLOWED_ORIGINS = "*"
SOCKETIO_ASYNC_MODE = 'eventlet'

# Logging configuration
LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'

# Security configuration
CORS_ORIGINS = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    "*"  # Allow all origins in development
]

# API configuration
API_PREFIX = '/api'
API_VERSION = 'v1'

# Session configuration
SESSION_TIMEOUT = 3600  # 1 hour in seconds
MAX_CONCURRENT_SESSIONS = 5

# Scraping limits
MAX_PAGES_PER_SESSION = 100
MAX_TENDERS_PER_PAGE = 50

# Error messages
ERROR_MESSAGES = {
    'missing_fields': 'Missing required fields',
    'invalid_url': 'Invalid URL provided',
    'scraping_in_progress': 'Scraping is already in progress',
    'session_not_found': 'Session not found',
    'file_not_found': 'File not found',
    'invalid_tender_type': 'Invalid tender type. Use "O" for Open or "L" for Limited',
    'invalid_days_interval': 'Days interval must be a positive integer',
    'invalid_start_page': 'Start page must be a positive integer',
    'edge_driver_not_found': 'Edge driver not found',
    'browser_error': 'Failed to start browser',
    'captcha_required': 'Captcha is required',
    'scraping_failed': 'Scraping failed',
    'merge_failed': 'Failed to merge files',
    'download_failed': 'Failed to download file'
}

# Success messages
SUCCESS_MESSAGES = {
    'edge_opened': 'Edge browser opened successfully',
    'scraping_started': 'Scraping started successfully',
    'scraping_completed': 'Scraping completed successfully',
    'scraping_stopped': 'Scraping stopped successfully',
    'files_merged': 'Files merged successfully',
    'file_downloaded': 'File downloaded successfully'
}

# File naming patterns
FILE_PATTERNS = {
    'open_tender': 'open-tenders_output_page-{}.xlsx',
    'limited_tender': 'limited-tenders_output_page-{}.xlsx',
    'merged': 'merged_data_{}.xlsx'
}

# Browser configuration
BROWSER_OPTIONS = {
    'disable_gpu': True,
    'no_sandbox': True,
    'disable_dev_shm_usage': True,
    'disable_blink_features': 'AutomationControlled',
    'disable_extensions': True,
    'disable_plugins': True,
    'disable_images': True,
    'exclude_switches': ['enable-automation'],
    'use_automation_extension': False,
    'download_restrictions': 3
}

# Database configuration (if needed in future)
DATABASE_CONFIG = {
    'host': os.getenv('DB_HOST', 'localhost'),
    'port': int(os.getenv('DB_PORT', 5432)),
    'database': os.getenv('DB_NAME', 'eproc_db'),
    'user': os.getenv('DB_USER', 'postgres'),
    'password': os.getenv('DB_PASSWORD', ''),
}

# Email configuration (if needed in future)
EMAIL_CONFIG = {
    'smtp_server': os.getenv('SMTP_SERVER', 'smtp.gmail.com'),
    'smtp_port': int(os.getenv('SMTP_PORT', 587)),
    'smtp_user': os.getenv('SMTP_USER', ''),
    'smtp_password': os.getenv('SMTP_PASSWORD', ''),
    'from_email': os.getenv('FROM_EMAIL', 'noreply@eproc.com'),
}

# Monitoring configuration
MONITORING_CONFIG = {
    'enable_metrics': os.getenv('ENABLE_METRICS', 'False').lower() == 'true',
    'metrics_port': int(os.getenv('METRICS_PORT', 9090)),
    'health_check_interval': int(os.getenv('HEALTH_CHECK_INTERVAL', 30)),
}

def create_directories():
    """Create necessary directories if they don't exist"""
    directories = [
        OUTPUT_BASE_DIR,
        SCRAPER_OUTPUT_DIR,
        DOWNLOAD_DIR
    ]
    
    for directory in directories:
        directory.mkdir(parents=True, exist_ok=True)

def validate_config():
    """Validate configuration settings"""
    errors = []
    
    # Check if Edge driver exists
    if not EDGE_DRIVER_PATH.exists():
        errors.append(f"Edge driver not found at: {EDGE_DRIVER_PATH}")
    
    # Validate port range
    if not (1024 <= SERVER_PORT <= 65535):
        errors.append(f"Invalid port number: {SERVER_PORT}")
    
    # Validate timeout
    if TIMEOUT <= 0:
        errors.append(f"Invalid timeout value: {TIMEOUT}")
    
    return errors

# Create directories on import
create_directories() 
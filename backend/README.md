# Super Scraper Backend

Complete backend API for the Super Scraper Dashboard with role-based authentication and real-time job monitoring.

## Features

- **Multi-level Authentication**: User, Admin, Super Admin roles
- **Real-time Job Monitoring**: WebSocket connections for live updates
- **File Management**: Upload/download scraping results
- **System Monitoring**: Performance metrics and system control
- **Database Integration**: PostgreSQL with proper schema
- **Security**: JWT tokens, password hashing, role-based access

## Quick Start

### 1. Install Dependencies
```bash
cd backend
npm install
```

### 2. Setup Environment
```bash
cp .env.example .env
# Edit .env with your database credentials
```

### 3. Setup Database
```bash
# Create PostgreSQL database first
createdb scraper_db

# Run database setup
npm run setup-db
```

### 4. Start Server
```bash
# Development mode
npm run dev

# Production mode
npm start
```

## Default Accounts

After running the database setup, these accounts will be available:

- **Super Admin**: `super@scraper.com` / `SuperScraper2024!`
- **Admin**: `admin@scraper.com` / `admin123`

## API Endpoints

### Authentication
- `POST /api/auth/register` - User registration
- `POST /api/auth/login` - User login
- `POST /api/auth/logout` - User logout

### User Management (Admin/Super Admin)
- `GET /api/admin/users` - Get all users
- `PUT /api/admin/users/:id/role` - Update user role (Super Admin only)
- `DELETE /api/admin/users/:id` - Delete user (Super Admin only)

### Tools Management
- `GET /api/tools` - Get all tools
- `POST /api/tools` - Create tool (Admin only)
- `PUT /api/tools/:id` - Update tool (Admin only)
- `DELETE /api/tools/:id` - Delete tool (Admin only)

### Scraping Jobs
- `POST /api/jobs` - Create scraping job
- `GET /api/jobs` - Get jobs (filtered by user role)
- `GET /api/jobs/:id/status` - Get job status
- `POST /api/jobs/:id/stop` - Stop job

### System Monitoring (Super Admin)
- `GET /api/admin/system-metrics` - Get system metrics

### WebSocket
- `ws://localhost:3001` - Real-time job updates

## Database Schema

The system uses PostgreSQL with the following main tables:

- **users**: User accounts with role-based access
- **tools**: Scraping tools configuration
- **scraping_jobs**: Job execution tracking

## Security Features

- JWT token authentication
- Password hashing with bcrypt
- Role-based access control
- Input validation and sanitization
- CORS protection

## File Storage

Uploaded files are stored in the `uploads/` directory with proper access control.

## Development

The backend is built with:
- Node.js + Express
- PostgreSQL database
- WebSocket for real-time updates
- JWT for authentication
- Multer for file uploads

## Production Deployment

1. Set up PostgreSQL database
2. Configure environment variables
3. Run database setup
4. Start the server with PM2 or similar process manager
5. Set up reverse proxy (nginx) for production

## Support

For issues or questions, please check the documentation or contact the development team.
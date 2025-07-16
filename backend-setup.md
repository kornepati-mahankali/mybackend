# Backend Setup Guide

## Required Backend Endpoints

### Authentication
- `POST /api/auth/login` - User login
- `POST /api/auth/register` - User registration  
- `POST /api/auth/logout` - User logout
- `GET /api/auth/me` - Get current user

### User Management (Admin only)
- `GET /api/admin/users` - Get all users
- `PUT /api/admin/users/:id/role` - Update user role
- `DELETE /api/admin/users/:id` - Delete user

### Tools Management
- `GET /api/tools` - Get all tools
- `POST /api/tools` - Create new tool (Admin only)
- `PUT /api/tools/:id` - Update tool (Admin only)
- `DELETE /api/tools/:id` - Delete tool (Admin only)

### Scraping Jobs
- `POST /api/jobs` - Create scraping job
- `GET /api/jobs` - Get user's jobs (or all for admin)
- `GET /api/jobs/:id/status` - Get job status
- `POST /api/jobs/:id/stop` - Stop running job
- `GET /api/jobs/:id/download/:filename` - Download output file
- `WebSocket /api/jobs/:id/stream` - Real-time job updates

### Analytics
- `GET /api/analytics/performance` - Get performance data
- `GET /api/admin/system-metrics` - Get system metrics (Admin only)

## Database Schema

### Users Table
```sql
CREATE TABLE users (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  email VARCHAR(255) UNIQUE NOT NULL,
  username VARCHAR(100) NOT NULL,
  password_hash VARCHAR(255) NOT NULL,
  role VARCHAR(20) DEFAULT 'user',
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW()
);
```

### Tools Table
```sql
CREATE TABLE tools (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  name VARCHAR(255) NOT NULL,
  category VARCHAR(50) NOT NULL,
  description TEXT,
  states JSONB,
  icon VARCHAR(50),
  is_active BOOLEAN DEFAULT true,
  created_at TIMESTAMP DEFAULT NOW()
);
```

### Scraping Jobs Table
```sql
CREATE TABLE scraping_jobs (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID REFERENCES users(id),
  tool_id UUID REFERENCES tools(id),
  state VARCHAR(100),
  username VARCHAR(255),
  starting_name VARCHAR(255),
  status VARCHAR(20) DEFAULT 'pending',
  progress INTEGER DEFAULT 0,
  start_time TIMESTAMP,
  end_time TIMESTAMP,
  output_files JSONB,
  logs JSONB,
  created_at TIMESTAMP DEFAULT NOW()
);
```

## Tech Stack Recommendations

### Backend Framework Options:
1. **Node.js + Express + TypeScript**
2. **Python + FastAPI**
3. **Go + Gin**
4. **Java + Spring Boot**

### Database:
- **PostgreSQL** (recommended for complex queries)
- **MongoDB** (for flexible document storage)

### Queue System:
- **Redis + Bull Queue** (Node.js)
- **Celery** (Python)
- **Background jobs** (Go)

### File Storage:
- **Local filesystem** (development)
- **AWS S3** (production)
- **Google Cloud Storage**

## Environment Setup

1. Copy `.env.example` to `.env`
2. Update the API base URL to match your backend
3. Configure your backend with the required endpoints
4. Set up database with the provided schema
5. Implement authentication middleware
6. Add file upload/download handling
7. Set up WebSocket for real-time updates
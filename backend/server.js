const express = require('express');
const cors = require('cors');
const bcrypt = require('bcryptjs');
const jwt = require('jsonwebtoken');
const { Pool } = require('pg');
const multer = require('multer');
const path = require('path');
const fs = require('fs');
const WebSocket = require('ws');
const http = require('http');
require('dotenv').config();

const app = express();
const server = http.createServer(app);
const wss = new WebSocket.Server({ server });

// Database connection
const pool = new Pool({
  connectionString: process.env.DATABASE_URL || 'postgresql://username:password@localhost:5432/scraper_db',
});

// Middleware
app.use(cors());
app.use(express.json());
app.use('/uploads', express.static('uploads'));

// File upload configuration
const storage = multer.diskStorage({
  destination: (req, file, cb) => {
    const uploadPath = 'uploads/';
    if (!fs.existsSync(uploadPath)) {
      fs.mkdirSync(uploadPath, { recursive: true });
    }
    cb(null, uploadPath);
  },
  filename: (req, file, cb) => {
    cb(null, Date.now() + '-' + file.originalname);
  }
});

const upload = multer({ 
  storage,
  limits: { fileSize: 100 * 1024 * 1024 } // 100MB limit
});

// JWT middleware
const authenticateToken = (req, res, next) => {
  const authHeader = req.headers['authorization'];
  const token = authHeader && authHeader.split(' ')[1];

  if (!token) {
    return res.status(401).json({ error: 'Access token required' });
  }

  jwt.verify(token, process.env.JWT_SECRET || 'your-secret-key', (err, user) => {
    if (err) {
      return res.status(403).json({ error: 'Invalid token' });
    }
    req.user = user;
    next();
  });
};

// Admin middleware
const requireAdmin = (req, res, next) => {
  if (req.user.role !== 'admin' && req.user.role !== 'super_admin') {
    return res.status(403).json({ error: 'Admin access required' });
  }
  next();
};

// Super Admin middleware
const requireSuperAdmin = (req, res, next) => {
  if (req.user.role !== 'super_admin') {
    return res.status(403).json({ error: 'Super Admin access required' });
  }
  next();
};

// Authentication Routes
app.post('/api/auth/register', async (req, res) => {
  try {
    const { email, username, password } = req.body;

    // Check if user exists
    const existingUser = await pool.query('SELECT id FROM users WHERE email = $1', [email]);
    if (existingUser.rows.length > 0) {
      return res.status(400).json({ error: 'User already exists' });
    }

    // Hash password
    const hashedPassword = await bcrypt.hash(password, 10);

    // Create user
    const result = await pool.query(
      'INSERT INTO users (email, username, password_hash, role) VALUES ($1, $2, $3, $4) RETURNING id, email, username, role, created_at',
      [email, username, hashedPassword, 'user']
    );

    const user = result.rows[0];
    const token = jwt.sign(
      { id: user.id, email: user.email, role: user.role },
      process.env.JWT_SECRET || 'your-secret-key',
      { expiresIn: '24h' }
    );

    res.json({ user, token });
  } catch (error) {
    console.error('Registration error:', error);
    res.status(500).json({ error: 'Registration failed' });
  }
});

app.post('/api/auth/login', async (req, res) => {
  try {
    const { email, password } = req.body;

    // Find user
    const result = await pool.query('SELECT * FROM users WHERE email = $1', [email]);
    if (result.rows.length === 0) {
      return res.status(401).json({ error: 'Invalid credentials' });
    }

    const user = result.rows[0];

    // Check password
    const validPassword = await bcrypt.compare(password, user.password_hash);
    if (!validPassword) {
      return res.status(401).json({ error: 'Invalid credentials' });
    }

    // Update last login
    await pool.query('UPDATE users SET last_login = NOW() WHERE id = $1', [user.id]);

    const token = jwt.sign(
      { id: user.id, email: user.email, role: user.role },
      process.env.JWT_SECRET || 'your-secret-key',
      { expiresIn: '24h' }
    );

    const { password_hash, ...userWithoutPassword } = user;
    res.json({ user: userWithoutPassword, token });
  } catch (error) {
    console.error('Login error:', error);
    res.status(500).json({ error: 'Login failed' });
  }
});

app.post('/api/auth/logout', authenticateToken, (req, res) => {
  res.json({ message: 'Logged out successfully' });
});

// User Management Routes (Admin/Super Admin)
app.get('/api/admin/users', authenticateToken, requireAdmin, async (req, res) => {
  try {
    const result = await pool.query(
      'SELECT id, email, username, role, created_at, last_login, is_active FROM users ORDER BY created_at DESC'
    );
    res.json(result.rows);
  } catch (error) {
    console.error('Get users error:', error);
    res.status(500).json({ error: 'Failed to fetch users' });
  }
});

app.put('/api/admin/users/:id/role', authenticateToken, requireSuperAdmin, async (req, res) => {
  try {
    const { id } = req.params;
    const { role } = req.body;

    await pool.query('UPDATE users SET role = $1 WHERE id = $2', [role, id]);
    res.json({ message: 'User role updated successfully' });
  } catch (error) {
    console.error('Update user role error:', error);
    res.status(500).json({ error: 'Failed to update user role' });
  }
});

app.delete('/api/admin/users/:id', authenticateToken, requireSuperAdmin, async (req, res) => {
  try {
    const { id } = req.params;
    await pool.query('DELETE FROM users WHERE id = $1', [id]);
    res.json({ message: 'User deleted successfully' });
  } catch (error) {
    console.error('Delete user error:', error);
    res.status(500).json({ error: 'Failed to delete user' });
  }
});

// Tools Management Routes
app.get('/api/tools', authenticateToken, async (req, res) => {
  try {
    const result = await pool.query('SELECT * FROM tools WHERE is_active = true ORDER BY name');
    res.json(result.rows);
  } catch (error) {
    console.error('Get tools error:', error);
    res.status(500).json({ error: 'Failed to fetch tools' });
  }
});

app.post('/api/tools', authenticateToken, requireAdmin, async (req, res) => {
  try {
    const { name, category, description, states, icon } = req.body;
    
    const result = await pool.query(
      'INSERT INTO tools (name, category, description, states, icon, created_by) VALUES ($1, $2, $3, $4, $5, $6) RETURNING *',
      [name, category, description, JSON.stringify(states), icon, req.user.id]
    );

    res.json(result.rows[0]);
  } catch (error) {
    console.error('Create tool error:', error);
    res.status(500).json({ error: 'Failed to create tool' });
  }
});

// Scraping Jobs Routes
app.post('/api/jobs', authenticateToken, async (req, res) => {
  try {
    const { toolId, state, username, startingName } = req.body;
    
    const result = await pool.query(
      'INSERT INTO tools_1 (user_id, tool_id, state, username, starting_name, status) VALUES ($1, $2, $3, $4, $5, $6) RETURNING *',
      [req.user.id, toolId, state, username, startingName, 'pending']
    );

    const job = result.rows[0];
    
    // Start scraping process (simulate)
    setTimeout(() => {
      startScrapingJob(job.id);
    }, 1000);

    res.json(job);
  } catch (error) {
    console.error('Create job error:', error);
    res.status(500).json({ error: 'Failed to create job' });
  }
});

app.get('/api/jobs', authenticateToken, async (req, res) => {
  try {
    const { userId } = req.query;
    let query = 'SELECT j.*, t.name as tool_name FROM tools_1 j JOIN tools t ON j.tool_id = t.id';
    let params = [];

    if (req.user.role === 'user') {
      query += ' WHERE j.user_id = $1';
      params = [req.user.id];
    } else if (userId) {
      query += ' WHERE j.user_id = $1';
      params = [userId];
    }

    query += ' ORDER BY j.created_at DESC';

    const result = await pool.query(query, params);
    res.json(result.rows);
  } catch (error) {
    console.error('Get jobs error:', error);
    res.status(500).json({ error: 'Failed to fetch jobs' });
  }
});

// System Metrics (Super Admin)
app.get('/api/admin/system-metrics', authenticateToken, requireSuperAdmin, async (req, res) => {
  try {
    const totalUsers = await pool.query('SELECT COUNT(*) FROM users');
    const activeUsers = await pool.query('SELECT COUNT(*) FROM users WHERE last_login > NOW() - INTERVAL \'24 hours\'');
    const totalJobs = await pool.query('SELECT COUNT(*) FROM tools_1');
    const runningJobs = await pool.query('SELECT COUNT(*) FROM tools_1 WHERE status = \'running\'');

    res.json({
      totalUsers: parseInt(totalUsers.rows[0].count),
      activeUsers: parseInt(activeUsers.rows[0].count),
      totalJobs: parseInt(totalJobs.rows[0].count),
      runningJobs: parseInt(runningJobs.rows[0].count),
      systemLoad: Math.random() * 100,
      memoryUsage: Math.random() * 100,
      diskUsage: Math.random() * 100,
      uptime: process.uptime()
    });
  } catch (error) {
    console.error('Get system metrics error:', error);
    res.status(500).json({ error: 'Failed to fetch system metrics' });
  }
});

// Simulate scraping job
async function startScrapingJob(jobId) {
  try {
    await pool.query('UPDATE tools_1 SET status = $1, start_time = NOW() WHERE id = $2', ['running', jobId]);
    
    // Simulate progress updates
    for (let progress = 0; progress <= 100; progress += 10) {
      await new Promise(resolve => setTimeout(resolve, 1000));
      
      await pool.query('UPDATE tools_1 SET progress = $1 WHERE id = $2', [progress, jobId]);
      
      // Broadcast progress to WebSocket clients
      wss.clients.forEach(client => {
        if (client.readyState === WebSocket.OPEN) {
          client.send(JSON.stringify({
            type: 'progress',
            jobId,
            progress,
            message: `Processing... ${progress}%`
          }));
        }
      });
    }

    // Complete job
    const outputFiles = [
      `job_${jobId}_output.csv`,
      `job_${jobId}_output.json`,
      `job_${jobId}_output.xlsx`
    ];

    await pool.query(
      'UPDATE tools_1 SET status = $1, progress = $2, end_time = NOW(), output_files = $3 WHERE id = $4',
      ['completed', 100, JSON.stringify(outputFiles), jobId]
    );

    wss.clients.forEach(client => {
      if (client.readyState === WebSocket.OPEN) {
        client.send(JSON.stringify({
          type: 'completed',
          jobId,
          outputFiles,
          message: 'Job completed successfully!'
        }));
      }
    });

  } catch (error) {
    console.error('Job execution error:', error);
    await pool.query('UPDATE tools_1 SET status = $1 WHERE id = $2', ['failed', jobId]);
  }
}

// WebSocket connection handling
wss.on('connection', (ws, req) => {
  console.log('WebSocket client connected');
  
  ws.on('message', (message) => {
    try {
      const data = JSON.parse(message);
      console.log('Received:', data);
    } catch (error) {
      console.error('WebSocket message error:', error);
    }
  });

  ws.on('close', () => {
    console.log('WebSocket client disconnected');
  });
});

const PORT = process.env.PORT || 3001;
server.listen(PORT, () => {
  console.log(`Super Scraper Backend running on port ${PORT}`);
});
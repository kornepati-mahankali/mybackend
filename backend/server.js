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
const archiver = require('archiver');
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

// Test endpoint
app.get('/api/test', (req, res) => {
  res.json({ message: 'Server is running correctly!', timestamp: new Date().toISOString() });
});

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

// Change Password Endpoint
app.post('/api/auth/change-password', authenticateToken, async (req, res) => {
  try {
    const userId = req.user.id;
    const { currentPassword, newPassword, confirmNewPassword } = req.body;

    if (!currentPassword || !newPassword || !confirmNewPassword) {
      return res.status(400).json({ error: 'All fields are required.' });
    }
    if (newPassword !== confirmNewPassword) {
      return res.status(400).json({ error: 'New passwords do not match.' });
    }
    // Get user from DB
    const result = await pool.query('SELECT password_hash FROM users WHERE id = $1', [userId]);
    if (result.rows.length === 0) {
      return res.status(404).json({ error: 'User not found.' });
    }
    const user = result.rows[0];
    // Check current password
    const validPassword = await bcrypt.compare(currentPassword, user.password_hash);
    if (!validPassword) {
      return res.status(401).json({ error: 'Current password is incorrect.' });
    }
    // Hash new password
    const hashedPassword = await bcrypt.hash(newPassword, 10);
    // Update password in DB
    await pool.query('UPDATE users SET password_hash = $1, updated_at = NOW() WHERE id = $2', [hashedPassword, userId]);
    res.json({ message: 'Password updated successfully.' });
  } catch (error) {
    console.error('Change password error:', error);
    res.status(500).json({ error: 'Failed to change password.' });
  }
});

// Delete Account Endpoint
app.delete('/api/auth/delete-account', authenticateToken, async (req, res) => {
  try {
    const userId = req.user.id;
    const { password } = req.body;

    if (!password) {
      return res.status(400).json({ error: 'Password is required for account deletion.' });
    }

    // Get user from DB
    const result = await pool.query('SELECT password_hash FROM users WHERE id = $1', [userId]);
    if (result.rows.length === 0) {
      return res.status(404).json({ error: 'User not found.' });
    }
    const user = result.rows[0];

    // Verify password
    const validPassword = await bcrypt.compare(password, user.password_hash);
    if (!validPassword) {
      return res.status(401).json({ error: 'Incorrect password.' });
    }

    // Delete user from DB
    await pool.query('DELETE FROM users WHERE id = $1', [userId]);
    res.json({ message: 'Account deleted successfully.' });
  } catch (error) {
    console.error('Delete account error:', error);
    res.status(500).json({ error: 'Failed to delete account.' });
  }
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

// Export all user data
app.get('/api/export-data', authenticateToken, async (req, res) => {
  try {
    const userId = req.user.id;
    
    // Get user profile data
    const userResult = await pool.query(
      'SELECT id, email, username, role, created_at, updated_at, last_login FROM users WHERE id = $1',
      [userId]
    );
    
    // Get user's scraping jobs
    const jobsResult = await pool.query(
      'SELECT j.*, t.name as tool_name FROM tools_1 j JOIN tools t ON j.tool_id = t.id WHERE j.user_id = $1 ORDER BY j.created_at DESC',
      [userId]
    );
    
    // Get user's tools (if any are assigned to them)
    const toolsResult = await pool.query(
      'SELECT * FROM tools WHERE created_by = $1 OR is_active = true ORDER BY created_at DESC',
      [userId]
    );
    
    // Get available output files information
    const outputDirs = ['gem', 'ireps', 'eproc', 'ap'];
    const availableFiles = [];
    
    for (const dir of outputDirs) {
      const outputPath = path.join(__dirname, 'outputs', dir);
      if (fs.existsSync(outputPath)) {
        const files = fs.readdirSync(outputPath, { withFileTypes: true });
        for (const file of files) {
          if (file.isDirectory()) {
            const subDirPath = path.join(outputPath, file.name);
            const subFiles = fs.readdirSync(subDirPath);
            availableFiles.push({
              tool: dir.toUpperCase(),
              sessionId: file.name,
              files: subFiles.filter(f => f.endsWith('.xlsx') || f.endsWith('.csv')),
              path: path.join('outputs', dir, file.name)
            });
          }
        }
      }
    }
    
    // Prepare export data
    const exportData = {
      exportDate: new Date().toISOString(),
      user: userResult.rows[0] || null,
      scrapingJobs: jobsResult.rows || [],
      tools: toolsResult.rows || [],
      availableFiles: availableFiles,
      summary: {
        totalJobs: jobsResult.rows.length,
        completedJobs: jobsResult.rows.filter(job => job.status === 'completed').length,
        failedJobs: jobsResult.rows.filter(job => job.status === 'failed').length,
        runningJobs: jobsResult.rows.filter(job => job.status === 'running').length,
        totalTools: toolsResult.rows.length,
        totalOutputFiles: availableFiles.reduce((sum, dir) => sum + dir.files.length, 0),
        availableSessions: availableFiles.length
      }
    };
    
    // Set headers for file download
    res.setHeader('Content-Type', 'application/json');
    res.setHeader('Content-Disposition', `attachment; filename="user_data_${userId}_${Date.now()}.json"`);
    
    res.json(exportData);
    
  } catch (error) {
    console.error('Export data error:', error);
    res.status(500).json({ error: 'Failed to export data' });
  }
});

// Download all output files as zip
app.get('/api/export-files', authenticateToken, async (req, res) => {
  try {
    const userId = req.user.id;
    
    // Create a zip archive
    const archive = archiver('zip', {
      zlib: { level: 9 } // Sets the compression level
    });
    
    // Handle archive errors
    archive.on('error', (err) => {
      console.error('Archive error:', err);
      res.status(500).json({ error: 'Failed to create archive' });
    });
    
    // Set headers for file download
    res.setHeader('Content-Type', 'application/zip');
    res.setHeader('Content-Disposition', `attachment; filename="output_files_${userId}_${Date.now()}.zip"`);
    
    // Pipe archive data to the response
    archive.pipe(res);
    
    // Add output directories to the zip
    const outputDirs = ['gem', 'ireps', 'eproc', 'ap'];
    let hasFiles = false;
    
    for (const dir of outputDirs) {
      const outputPath = path.join(__dirname, 'outputs', dir);
      if (fs.existsSync(outputPath)) {
        const files = fs.readdirSync(outputPath);
        if (files.length > 0) {
          // Add the entire directory to the zip
          archive.directory(outputPath, `outputs/${dir}`);
          hasFiles = true;
        }
      }
    }
    
    if (!hasFiles) {
      // If no files found, create an empty zip with a readme
      archive.append('No output files found at the time of export.', { name: 'README.txt' });
    }
    
    // Finalize the archive
    await archive.finalize();
    
  } catch (error) {
    console.error('Export files error:', error);
    res.status(500).json({ error: 'Failed to export files' });
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

// Job processing - now handled by the job_processor.py
// The job processor will automatically pick up pending jobs and process them
async function startScrapingJob(jobId) {
  try {
    // Just update the job status to pending - the job processor will handle the rest
    await pool.query('UPDATE tools_1 SET status = $1 WHERE id = $2', ['pending', jobId]);
    
    console.log(`Job ${jobId} queued for processing`);
    
    // Broadcast job queued to WebSocket clients
    wss.clients.forEach(client => {
      if (client.readyState === WebSocket.OPEN) {
        client.send(JSON.stringify({
          type: 'queued',
          jobId,
          message: 'Job queued for processing'
        }));
      }
    });

  } catch (error) {
    console.error('Job queuing error:', error);
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
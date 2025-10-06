const express = require('express');
const bcrypt = require('bcryptjs');
const jwt = require('jsonwebtoken');
const { body, validationResult } = require('express-validator');
const { query } = require('../database/connection');
const logger = require('../utils/logger');

const router = express.Router();

// Register endpoint
router.post('/register', [
  body('email').isEmail().normalizeEmail(),
  body('password').isLength({ min: 8 }).withMessage('Password must be at least 8 characters'),
  body('firstName').trim().isLength({ min: 1 }).withMessage('First name is required'),
  body('lastName').trim().isLength({ min: 1 }).withMessage('Last name is required'),
  body('company').optional().trim()
], async (req, res, next) => {
  try {
    const errors = validationResult(req);
    if (!errors.isEmpty()) {
      return res.status(400).json({
        error: 'Validation failed',
        details: errors.array()
      });
    }

    const { email, password, firstName, lastName, company } = req.body;

    // Check if user already exists
    const existingUser = await query(
      'SELECT id FROM users WHERE email = $1',
      [email]
    );

    if (existingUser.rows.length > 0) {
      return res.status(400).json({
        error: 'User already exists with this email'
      });
    }

    // Hash password
    const saltRounds = 12;
    const passwordHash = await bcrypt.hash(password, saltRounds);

    // Create user
    const result = await query(`
      INSERT INTO users (email, password_hash, first_name, last_name, company)
      VALUES ($1, $2, $3, $4, $5)
      RETURNING id, email, first_name, last_name, company, role, subscription_tier, created_at
    `, [email, passwordHash, firstName, lastName, company || null]);

    const user = result.rows[0];

    // Generate JWT token
    const token = jwt.sign(
      { userId: user.id, email: user.email },
      process.env.JWT_SECRET,
      { expiresIn: process.env.JWT_EXPIRES_IN || '7d' }
    );

    logger.info(`New user registered: ${email}`);

    res.status(201).json({
      message: 'User registered successfully',
      user: {
        id: user.id,
        email: user.email,
        firstName: user.first_name,
        lastName: user.last_name,
        company: user.company,
        role: user.role,
        subscriptionTier: user.subscription_tier,
        createdAt: user.created_at
      },
      token
    });

  } catch (error) {
    next(error);
  }
});

// Login endpoint
router.post('/login', [
  body('email').isEmail().normalizeEmail(),
  body('password').exists().withMessage('Password is required')
], async (req, res, next) => {
  try {
    const errors = validationResult(req);
    if (!errors.isEmpty()) {
      return res.status(400).json({
        error: 'Validation failed',
        details: errors.array()
      });
    }

    const { email, password } = req.body;

    // Find user
    const result = await query(`
      SELECT id, email, password_hash, first_name, last_name, company, role, 
             subscription_tier, is_verified, is_active, created_at
      FROM users 
      WHERE email = $1 AND is_active = true
    `, [email]);

    if (result.rows.length === 0) {
      return res.status(401).json({
        error: 'Invalid email or password'
      });
    }

    const user = result.rows[0];

    // Verify password
    const isValidPassword = await bcrypt.compare(password, user.password_hash);
    if (!isValidPassword) {
      return res.status(401).json({
        error: 'Invalid email or password'
      });
    }

    // Update last login
    await query(
      'UPDATE users SET last_login = CURRENT_TIMESTAMP WHERE id = $1',
      [user.id]
    );

    // Generate JWT token
    const token = jwt.sign(
      { userId: user.id, email: user.email },
      process.env.JWT_SECRET,
      { expiresIn: process.env.JWT_EXPIRES_IN || '7d' }
    );

    logger.info(`User logged in: ${email}`);

    res.json({
      message: 'Login successful',
      user: {
        id: user.id,
        email: user.email,
        firstName: user.first_name,
        lastName: user.last_name,
        company: user.company,
        role: user.role,
        subscriptionTier: user.subscription_tier,
        isVerified: user.is_verified,
        createdAt: user.created_at
      },
      token
    });

  } catch (error) {
    next(error);
  }
});

// Token verification endpoint
router.get('/verify', async (req, res, next) => {
  try {
    const token = req.headers.authorization?.split(' ')[1];
    
    if (!token) {
      return res.status(401).json({
        error: 'No token provided'
      });
    }

    const decoded = jwt.verify(token, process.env.JWT_SECRET);
    
    // Get current user data
    const result = await query(`
      SELECT id, email, first_name, last_name, company, role, 
             subscription_tier, is_verified, is_active, created_at
      FROM users 
      WHERE id = $1 AND is_active = true
    `, [decoded.userId]);

    if (result.rows.length === 0) {
      return res.status(401).json({
        error: 'Invalid token - user not found'
      });
    }

    const user = result.rows[0];

    res.json({
      valid: true,
      user: {
        id: user.id,
        email: user.email,
        firstName: user.first_name,
        lastName: user.last_name,
        company: user.company,
        role: user.role,
        subscriptionTier: user.subscription_tier,
        isVerified: user.is_verified,
        createdAt: user.created_at
      }
    });

  } catch (error) {
    if (error.name === 'JsonWebTokenError' || error.name === 'TokenExpiredError') {
      return res.status(401).json({
        error: 'Invalid or expired token'
      });
    }
    next(error);
  }
});

// Logout endpoint (optional - mainly for logging)
router.post('/logout', (req, res) => {
  // Since JWTs are stateless, logout is handled client-side
  // This endpoint is mainly for logging purposes
  logger.info('User logged out');
  res.json({
    message: 'Logged out successfully'
  });
});

module.exports = router;
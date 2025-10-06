const express = require('express');
const bcrypt = require('bcryptjs');
const jwt = require('jsonwebtoken');
const { body, validationResult } = require('express-validator');
const logger = require('../utils/logger');

const router = express.Router();

// In-memory user store for development
const users = new Map();
let nextUserId = 1;

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
    const existingUser = Array.from(users.values()).find(u => u.email === email);
    if (existingUser) {
      return res.status(400).json({
        error: 'User already exists with this email'
      });
    }

    // Hash password
    const saltRounds = 12;
    const passwordHash = await bcrypt.hash(password, saltRounds);

    // Create user
    const user = {
      id: nextUserId++,
      email,
      passwordHash,
      firstName,
      lastName,
      company: company || null,
      role: 'user',
      subscriptionTier: 'free',
      isVerified: false,
      createdAt: new Date().toISOString()
    };

    users.set(user.id, user);

    // Generate JWT token
    const token = jwt.sign(
      { userId: user.id, email: user.email },
      process.env.JWT_SECRET || 'dev-secret',
      { expiresIn: process.env.JWT_EXPIRES_IN || '7d' }
    );

    logger.info(`New user registered: ${email}`);

    res.status(201).json({
      message: 'User registered successfully',
      user: {
        id: user.id,
        email: user.email,
        firstName: user.firstName,
        lastName: user.lastName,
        company: user.company,
        role: user.role,
        subscriptionTier: user.subscriptionTier,
        isVerified: user.isVerified,
        createdAt: user.createdAt
      },
      token
    });

  } catch (error) {
    logger.error('Registration error:', error);
    next(error);
  }
});

// Login endpoint
router.post('/login', [
  body('email').isEmail().normalizeEmail(),
  body('password').notEmpty()
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
    const user = Array.from(users.values()).find(u => u.email === email);
    if (!user) {
      return res.status(401).json({
        error: 'Invalid credentials'
      });
    }

    // Check password
    const isValidPassword = await bcrypt.compare(password, user.passwordHash);
    if (!isValidPassword) {
      return res.status(401).json({
        error: 'Invalid credentials'
      });
    }

    // Generate JWT token
    const token = jwt.sign(
      { userId: user.id, email: user.email },
      process.env.JWT_SECRET || 'dev-secret',
      { expiresIn: process.env.JWT_EXPIRES_IN || '7d' }
    );

    logger.info(`User logged in: ${email}`);

    res.json({
      message: 'Login successful',
      user: {
        id: user.id,
        email: user.email,
        firstName: user.firstName,
        lastName: user.lastName,
        company: user.company,
        role: user.role,
        subscriptionTier: user.subscriptionTier,
        isVerified: user.isVerified,
        createdAt: user.createdAt
      },
      token
    });

  } catch (error) {
    logger.error('Login error:', error);
    next(error);
  }
});

// Verify token endpoint
router.get('/verify', async (req, res, next) => {
  try {
    const token = req.headers.authorization?.replace('Bearer ', '');
    
    if (!token) {
      return res.status(401).json({
        error: 'No token provided'
      });
    }

    const decoded = jwt.verify(token, process.env.JWT_SECRET || 'dev-secret');
    const user = users.get(decoded.userId);

    if (!user) {
      return res.status(401).json({
        error: 'Invalid token'
      });
    }

    res.json({
      valid: true,
      user: {
        id: user.id,
        email: user.email,
        firstName: user.firstName,
        lastName: user.lastName,
        company: user.company,
        role: user.role,
        subscriptionTier: user.subscriptionTier,
        isVerified: user.isVerified,
        createdAt: user.createdAt
      }
    });

  } catch (error) {
    logger.error('Token verification error:', error);
    res.status(401).json({
      error: 'Invalid token'
    });
  }
});

// Logout endpoint
router.post('/logout', (req, res) => {
  // In a real implementation, you might invalidate the token
  // For now, we just send a success response
  res.json({ message: 'Logout successful' });
});

module.exports = router;
const { Pool } = require('pg');
const logger = require('../utils/logger');

let pool;

const connectDB = async () => {
  try {
    // For development without database, return a mock connection
    if (process.env.NODE_ENV === 'development' && !process.env.DB_HOST) {
      logger.info('⚠️  Running in mock database mode for development');
      return null;
    }

    pool = new Pool({
      host: process.env.DB_HOST || 'localhost',
      port: process.env.DB_PORT || 5432,
      database: process.env.DB_NAME || 'ensimuspace_dev',
      user: process.env.DB_USER || 'postgres',
      password: process.env.DB_PASSWORD || 'password',
      max: 20,
      idleTimeoutMillis: 30000,
      connectionTimeoutMillis: 2000,
    });

    // Test the connection
    const client = await pool.connect();
    await client.query('SELECT NOW()');
    client.release();

    logger.info('✅ Database connection established successfully');
    return pool;
  } catch (error) {
    logger.error('❌ Database connection failed:', error.message);
    logger.warn('⚠️  Running without database connection');
    return null;
  }
};

const query = async (text, params) => {
  if (!pool) {
    throw new Error('Database not available');
  }
  
  const start = Date.now();
  try {
    const res = await pool.query(text, params);
    const duration = Date.now() - start;
    logger.debug(`Query executed in ${duration}ms: ${text}`);
    return res;
  } catch (error) {
    logger.error('Database query error:', error.message);
    logger.error('Query:', text);
    logger.error('Params:', params);
    throw error;
  }
};

const getClient = async () => {
  return await pool.connect();
};

const closeDB = async () => {
  if (pool) {
    await pool.end();
    logger.info('Database connection closed');
  }
};

module.exports = {
  connectDB,
  query,
  getClient,
  closeDB,
  pool: () => pool
};
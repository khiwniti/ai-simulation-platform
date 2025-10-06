const { connectDB, query, closeDB } = require('./connection');
const logger = require('../utils/logger');

async function clearDatabase() {
  try {
    await connectDB();
    logger.info('🧹 Starting database cleanup...');

    // Clear all data but preserve schema
    const tables = [
      'usage_analytics',
      'notifications', 
      'api_keys',
      'simulation_versions',
      'project_collaborators',
      'simulation_files',
      'simulations',
      'projects',
      'users'
    ];

    for (const table of tables) {
      try {
        await query(`DELETE FROM ${table}`);
        logger.info(`✅ Cleared table: ${table}`);
      } catch (error) {
        logger.warn(`⚠️  Could not clear table ${table}: ${error.message}`);
      }
    }

    // Reset sequences if needed
    try {
      await query(`
        DO $$ 
        DECLARE 
          r RECORD;
        BEGIN
          FOR r IN (SELECT tablename FROM pg_tables WHERE schemaname = 'public') 
          LOOP
            EXECUTE 'ALTER SEQUENCE IF EXISTS ' || quote_ident(r.tablename) || '_id_seq RESTART WITH 1';
          END LOOP;
        END $$;
      `);
      logger.info('✅ Reset sequences');
    } catch (error) {
      logger.warn(`⚠️  Could not reset sequences: ${error.message}`);
    }

    logger.info('🎉 Database cleanup completed successfully!');
    logger.info('📝 All mock data has been removed - ready for production data');

  } catch (error) {
    logger.error('❌ Database cleanup failed:', error);
    throw error;
  } finally {
    await closeDB();
  }
}

// Run if called directly
if (require.main === module) {
  clearDatabase()
    .then(() => process.exit(0))
    .catch((error) => {
      console.error('Cleanup failed:', error);
      process.exit(1);
    });
}

module.exports = { clearDatabase };
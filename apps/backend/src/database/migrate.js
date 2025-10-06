const { connectDB, query, closeDB } = require('./connection');
const fs = require('fs');
const path = require('path');
const logger = require('../utils/logger');

async function setupDatabase() {
  try {
    await connectDB();
    logger.info('📋 Setting up EnsimuSpace database schema...');

    // Read the schema file
    const schemaPath = path.join(__dirname, '../../../database/schema.sql');
    
    if (!fs.existsSync(schemaPath)) {
      throw new Error('Schema file not found at: ' + schemaPath);
    }

    const schema = fs.readFileSync(schemaPath, 'utf8');
    
    // Execute the schema
    await query(schema);
    logger.info('✅ Database schema created successfully');

    // Insert initial simulation types
    await query(`
      INSERT INTO simulation_types (name, description, category, icon, is_ai_assisted, parameters) VALUES
      ('CFD Analysis', 'Computational Fluid Dynamics simulation for fluid flow analysis', 'fluid', 'wind', true, '{"inlet_velocity": {"type": "number", "default": 10}, "viscosity": {"type": "number", "default": 0.001}}'),
      ('Structural Analysis', 'Finite Element Analysis for structural mechanics', 'structural', 'layers', true, '{"material": {"type": "string", "default": "steel"}, "load": {"type": "number", "default": 1000}}'),
      ('Heat Transfer', 'Thermal analysis and heat transfer simulation', 'thermal', 'thermometer', true, '{"temperature": {"type": "number", "default": 300}, "conductivity": {"type": "number", "default": 0.5}}'),
      ('Electromagnetic', 'Electromagnetic field simulation and analysis', 'electromagnetic', 'zap', false, '{"frequency": {"type": "number", "default": 1000}, "amplitude": {"type": "number", "default": 1}}'),
      ('Multiphysics', 'Combined physics simulation for complex interactions', 'multiphysics', 'layers-3', true, '{"coupling": {"type": "array", "default": ["thermal", "structural"]}}'),
      ('Optimization', 'AI-powered design optimization', 'optimization', 'trending-up', true, '{"objective": {"type": "string", "default": "minimize_weight"}, "constraints": {"type": "array", "default": []}}')
      ON CONFLICT (name) DO NOTHING;
    `);
    logger.info('✅ Simulation types initialized');

    // Insert AI models
    await query(`
      INSERT INTO ai_models (name, description, model_type, version, parameters, is_active) VALUES
      ('FlowNet', 'Neural network for fluid flow prediction', 'prediction', '2.1.0', '{"layers": 5, "neurons": 128}', true),
      ('StructOpt', 'AI optimizer for structural design', 'optimization', '1.5.2', '{"algorithm": "genetic", "population": 100}', true),
      ('ThermalPredict', 'Thermal behavior prediction model', 'prediction', '1.8.1', '{"accuracy": 0.95, "speed": "fast"}', true)
      ON CONFLICT (name) DO NOTHING;
    `);
    logger.info('✅ AI models initialized');

    logger.info('🎉 Database setup completed successfully!');
    logger.info('🚀 EnsimuSpace backend is ready to serve');

  } catch (error) {
    logger.error('❌ Database setup failed:', error);
    throw error;
  } finally {
    await closeDB();
  }
}

// Run if called directly
if (require.main === module) {
  setupDatabase()
    .then(() => process.exit(0))
    .catch((error) => {
      console.error('Setup failed:', error);
      process.exit(1);
    });
}

module.exports = { setupDatabase };
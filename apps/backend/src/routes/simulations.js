/**
 * Physics Simulation API Routes
 * Advanced engineering simulation endpoints
 */

const express = require('express');
const PhysicsEngine = require('../services/physicsEngine');
const router = express.Router();

const physicsEngine = new PhysicsEngine();

/**
 * GET /api/simulations/types
 * Get available simulation types
 */
router.get('/types', (req, res) => {
  try {
    const types = physicsEngine.getSimulationTypes();
    res.json({
      success: true,
      simulationTypes: types,
      count: Object.keys(types).length
    });
  } catch (error) {
    res.status(500).json({
      success: false,
      error: error.message
    });
  }
});

/**
 * GET /api/simulations/materials
 * Get available materials with properties
 */
router.get('/materials', (req, res) => {
  try {
    const materials = physicsEngine.getMaterials();
    res.json({
      success: true,
      materials: materials,
      count: Object.keys(materials).length
    });
  } catch (error) {
    res.status(500).json({
      success: false,
      error: error.message
    });
  }
});

/**
 * POST /api/simulations/run
 * Execute physics simulation
 */
router.post('/run', async (req, res) => {
  try {
    const { type, config } = req.body;
    
    if (!type) {
      return res.status(400).json({
        success: false,
        error: 'Simulation type is required'
      });
    }

    if (!config) {
      return res.status(400).json({
        success: false,
        error: 'Simulation configuration is required'
      });
    }

    console.log(`🚀 Running ${type} simulation with config:`, JSON.stringify(config, null, 2));
    
    const startTime = Date.now();
    const results = await physicsEngine.runSimulation(type, config);
    const executionTime = Date.now() - startTime;

    console.log(`✅ ${type} simulation completed in ${executionTime}ms`);

    res.json({
      success: true,
      simulationType: type,
      results: results,
      executionTime: `${executionTime}ms`,
      timestamp: new Date().toISOString()
    });

  } catch (error) {
    console.error('❌ Simulation error:', error);
    res.status(500).json({
      success: false,
      error: error.message,
      simulationType: req.body.type
    });
  }
});

/**
 * POST /api/simulations/fea
 * Specific FEA simulation endpoint
 */
router.post('/fea', async (req, res) => {
  try {
    const config = req.body;
    
    // Default FEA configuration
    const feaConfig = {
      geometry: {
        length: config.length || 1.0,
        height: config.height || 0.1,
        elements: config.elements || 20
      },
      material: {
        youngs: config.youngs_modulus || 200e9,
        moment_inertia: config.moment_inertia || (config.height || 0.1)**3/12,
        yield_strength: config.yield_strength || 250e6
      },
      loads: {
        force: config.force || -1000
      }
    };

    const results = await physicsEngine.runFEASimulation(feaConfig);
    
    res.json({
      success: true,
      simulationType: 'FEA',
      results: results,
      configuration: feaConfig
    });

  } catch (error) {
    res.status(500).json({
      success: false,
      error: error.message
    });
  }
});

/**
 * POST /api/simulations/cfd
 * Specific CFD simulation endpoint
 */
router.post('/cfd', async (req, res) => {
  try {
    const config = req.body;
    
    // Default CFD configuration
    const cfdConfig = {
      geometry: {
        length: config.length || 1.0,
        height: config.height || 1.0,
        grid_x: config.grid_x || 50,
        grid_y: config.grid_y || 50
      },
      fluid: {
        density: config.density || 1.0,
        viscosity: config.viscosity || 0.001,
        inlet_velocity: config.inlet_velocity || 1.0
      }
    };

    const results = await physicsEngine.runCFDSimulation(cfdConfig);
    
    res.json({
      success: true,
      simulationType: 'CFD',
      results: results,
      configuration: cfdConfig
    });

  } catch (error) {
    res.status(500).json({
      success: false,
      error: error.message
    });
  }
});

/**
 * POST /api/simulations/thermal
 * Specific thermal analysis endpoint
 */
router.post('/thermal', async (req, res) => {
  try {
    const config = req.body;
    
    // Default thermal configuration
    const thermalConfig = {
      geometry: {
        length: config.length || 1.0,
        height: config.height || 1.0,
        grid_x: config.grid_x || 50,
        grid_y: config.grid_y || 50
      },
      material: {
        thermal_conductivity: config.thermal_conductivity || 50,
        density: config.density || 7850,
        specific_heat: config.specific_heat || 460
      },
      boundary_conditions: {
        heat_source: config.heat_source || 1000,
        temp_bottom: config.temp_bottom || 100,
        temp_top: config.temp_top || 20,
        temp_left: config.temp_left || 60,
        temp_right: config.temp_right || 20
      }
    };

    const results = await physicsEngine.runThermalSimulation(thermalConfig);
    
    res.json({
      success: true,
      simulationType: 'THERMAL',
      results: results,
      configuration: thermalConfig
    });

  } catch (error) {
    res.status(500).json({
      success: false,
      error: error.message
    });
  }
});

/**
 * GET /api/simulations/health
 * Check simulation engine health
 */
router.get('/health', (req, res) => {
  res.json({
    success: true,
    message: 'Physics simulation engine is operational',
    engines: ['FEA', 'CFD', 'THERMAL'],
    timestamp: new Date().toISOString()
  });
});

module.exports = router;
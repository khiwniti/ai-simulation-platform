-- AI Simulation Platform Database Schema
-- Created: 2025-09-23
-- Description: Comprehensive schema for AI-powered engineering simulation platform

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Users table for authentication and user management
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    first_name VARCHAR(100) NOT NULL,
    last_name VARCHAR(100) NOT NULL,
    company VARCHAR(255),
    role VARCHAR(50) DEFAULT 'user' CHECK (role IN ('admin', 'user', 'trial')),
    subscription_tier VARCHAR(50) DEFAULT 'free' CHECK (subscription_tier IN ('free', 'pro', 'enterprise')),
    is_verified BOOLEAN DEFAULT FALSE,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    last_login TIMESTAMP WITH TIME ZONE
);

-- Projects table for organizing simulations
CREATE TABLE projects (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(255) NOT NULL,
    description TEXT,
    owner_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    is_public BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Simulation types/templates
CREATE TABLE simulation_types (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(255) NOT NULL UNIQUE,
    description TEXT,
    category VARCHAR(100) NOT NULL, -- 'fluid', 'structural', 'thermal', 'electromagnetic', etc.
    icon VARCHAR(255),
    is_ai_assisted BOOLEAN DEFAULT FALSE,
    parameters JSONB, -- Available parameters for this simulation type
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Individual simulations
CREATE TABLE simulations (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(255) NOT NULL,
    description TEXT,
    project_id UUID NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
    simulation_type_id UUID NOT NULL REFERENCES simulation_types(id),
    status VARCHAR(50) DEFAULT 'draft' CHECK (status IN ('draft', 'queued', 'running', 'completed', 'failed', 'cancelled')),
    parameters JSONB NOT NULL, -- Simulation parameters and configuration
    ai_config JSONB, -- AI-specific configuration if applicable
    mesh_config JSONB, -- Meshing configuration
    solver_config JSONB, -- Solver settings
    results JSONB, -- Simulation results
    progress DECIMAL(5,2) DEFAULT 0.00, -- Progress percentage
    cpu_time DECIMAL(10,3), -- CPU time in seconds
    memory_usage BIGINT, -- Memory usage in bytes
    error_message TEXT,
    started_at TIMESTAMP WITH TIME ZONE,
    completed_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- File storage for simulation assets
CREATE TABLE simulation_files (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    simulation_id UUID NOT NULL REFERENCES simulations(id) ON DELETE CASCADE,
    filename VARCHAR(255) NOT NULL,
    file_type VARCHAR(50) NOT NULL, -- 'geometry', 'mesh', 'result', 'config', etc.
    file_format VARCHAR(20) NOT NULL, -- 'step', 'stl', 'vtk', 'json', etc.
    file_path VARCHAR(500) NOT NULL, -- Storage path/URL
    file_size BIGINT NOT NULL,
    checksum VARCHAR(64),
    is_public BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- AI models and configurations
CREATE TABLE ai_models (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(255) NOT NULL UNIQUE,
    description TEXT,
    model_type VARCHAR(100) NOT NULL, -- 'prediction', 'optimization', 'meshing', etc.
    version VARCHAR(50) NOT NULL,
    file_path VARCHAR(500),
    parameters JSONB,
    accuracy_metrics JSONB,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Collaboration and sharing
CREATE TABLE project_collaborators (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    project_id UUID NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    role VARCHAR(50) DEFAULT 'viewer' CHECK (role IN ('owner', 'editor', 'viewer')),
    invited_by UUID REFERENCES users(id),
    invited_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    accepted_at TIMESTAMP WITH TIME ZONE,
    UNIQUE(project_id, user_id)
);

-- Simulation history and versioning
CREATE TABLE simulation_versions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    simulation_id UUID NOT NULL REFERENCES simulations(id) ON DELETE CASCADE,
    version_number INTEGER NOT NULL,
    parameters JSONB NOT NULL,
    results JSONB,
    created_by UUID NOT NULL REFERENCES users(id),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(simulation_id, version_number)
);

-- Usage analytics and metrics
CREATE TABLE usage_analytics (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES users(id) ON DELETE SET NULL,
    action VARCHAR(100) NOT NULL, -- 'simulation_created', 'simulation_run', 'file_uploaded', etc.
    resource_type VARCHAR(50), -- 'simulation', 'project', 'file', etc.
    resource_id UUID,
    metadata JSONB,
    ip_address INET,
    user_agent TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- System notifications
CREATE TABLE notifications (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    type VARCHAR(50) NOT NULL, -- 'simulation_complete', 'collaboration_invite', 'system_update', etc.
    title VARCHAR(255) NOT NULL,
    message TEXT NOT NULL,
    data JSONB,
    is_read BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- API keys for external integrations
CREATE TABLE api_keys (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    name VARCHAR(255) NOT NULL,
    key_hash VARCHAR(255) NOT NULL UNIQUE,
    permissions JSONB NOT NULL DEFAULT '[]',
    last_used_at TIMESTAMP WITH TIME ZONE,
    expires_at TIMESTAMP WITH TIME ZONE,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Indexes for performance
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_projects_owner_id ON projects(owner_id);
CREATE INDEX idx_simulations_project_id ON simulations(project_id);
CREATE INDEX idx_simulations_status ON simulations(status);
CREATE INDEX idx_simulations_created_at ON simulations(created_at);
CREATE INDEX idx_simulation_files_simulation_id ON simulation_files(simulation_id);
CREATE INDEX idx_project_collaborators_project_id ON project_collaborators(project_id);
CREATE INDEX idx_project_collaborators_user_id ON project_collaborators(user_id);
CREATE INDEX idx_usage_analytics_user_id ON usage_analytics(user_id);
CREATE INDEX idx_usage_analytics_created_at ON usage_analytics(created_at);
CREATE INDEX idx_notifications_user_id ON notifications(user_id);
CREATE INDEX idx_notifications_is_read ON notifications(is_read);

-- Functions for automatic timestamp updates
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Triggers for automatic timestamp updates
CREATE TRIGGER update_users_updated_at BEFORE UPDATE ON users
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_projects_updated_at BEFORE UPDATE ON projects
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_simulations_updated_at BEFORE UPDATE ON simulations
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_ai_models_updated_at BEFORE UPDATE ON ai_models
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Insert default simulation types
INSERT INTO simulation_types (name, description, category, is_ai_assisted, parameters) VALUES
('Fluid Dynamics - Basic', 'Basic computational fluid dynamics simulation', 'fluid', false, '{"viscosity": {"type": "number", "default": 0.001}, "density": {"type": "number", "default": 1000}}'),
('Fluid Dynamics - AI Enhanced', 'AI-assisted fluid dynamics with predictive modeling', 'fluid', true, '{"viscosity": {"type": "number", "default": 0.001}, "density": {"type": "number", "default": 1000}, "ai_prediction": {"type": "boolean", "default": true}}'),
('Structural Analysis', 'Static and dynamic structural analysis', 'structural', false, '{"material_young_modulus": {"type": "number", "default": 200000000000}, "poisson_ratio": {"type": "number", "default": 0.3}}'),
('Thermal Analysis', 'Heat transfer and thermal analysis', 'thermal', false, '{"thermal_conductivity": {"type": "number", "default": 50}, "specific_heat": {"type": "number", "default": 500}}'),
('Electromagnetic', 'Electromagnetic field simulation', 'electromagnetic', false, '{"permittivity": {"type": "number", "default": 8.854e-12}, "permeability": {"type": "number", "default": 1.257e-6}}'),
('Multiphysics - AI Optimized', 'Multi-physics simulation with AI optimization', 'multiphysics', true, '{"coupling_fields": {"type": "array", "default": ["fluid", "thermal"]}, "ai_optimization": {"type": "boolean", "default": true}}');

-- Insert default AI models
INSERT INTO ai_models (name, description, model_type, version, parameters, accuracy_metrics, is_active) VALUES
('FlowPredict-v1', 'AI model for predicting fluid flow patterns', 'prediction', '1.0.0', '{"input_features": ["geometry", "boundary_conditions"], "output": "flow_field"}', '{"accuracy": 0.95, "mse": 0.023}', true),
('MeshOptimizer-v2', 'AI-driven automatic mesh generation and optimization', 'meshing', '2.1.0', '{"mesh_density": "adaptive", "quality_threshold": 0.8}', '{"mesh_quality": 0.92, "generation_speed": "3x"}', true),
('ThermalPredict-v1', 'Thermal analysis prediction model', 'prediction', '1.2.0', '{"input_features": ["geometry", "material_properties", "heat_sources"], "output": "temperature_field"}', '{"accuracy": 0.93, "rmse": 2.1}', true);

COMMENT ON TABLE users IS 'User accounts and authentication information';
COMMENT ON TABLE projects IS 'Project containers for organizing simulations';
COMMENT ON TABLE simulations IS 'Individual simulation runs with parameters and results';
COMMENT ON TABLE simulation_types IS 'Available simulation types and templates';
COMMENT ON TABLE simulation_files IS 'File storage tracking for simulation assets';
COMMENT ON TABLE ai_models IS 'AI/ML models available for enhanced simulations';
COMMENT ON TABLE project_collaborators IS 'Project sharing and collaboration permissions';
COMMENT ON TABLE simulation_versions IS 'Version history for simulations';
COMMENT ON TABLE usage_analytics IS 'Usage tracking and analytics data';
COMMENT ON TABLE notifications IS 'User notifications and alerts';
COMMENT ON TABLE api_keys IS 'API keys for external integrations';
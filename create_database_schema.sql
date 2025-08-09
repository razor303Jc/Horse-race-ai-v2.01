-- 🗄️ Coding Models Database Schema - Phase 1 (Core Foundation)
-- Execute this SQL script to create the initial database structure

-- Enable necessary extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- 1. Projects Table (Core foundation)
CREATE TABLE projects (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL UNIQUE,
    description TEXT,
    language VARCHAR(50),
    framework VARCHAR(100),
    repository_url VARCHAR(500),
    root_path VARCHAR(1000),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 2. Files Table (File system mapping)
CREATE TABLE files (
    id SERIAL PRIMARY KEY,
    project_id INTEGER REFERENCES projects(id) ON DELETE CASCADE,
    file_path VARCHAR(1000) NOT NULL,
    file_name VARCHAR(255) NOT NULL,
    file_type VARCHAR(50),
    size_bytes INTEGER,
    language VARCHAR(50),
    last_modified TIMESTAMP,
    content_hash VARCHAR(64),
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(project_id, file_path)
);

-- 3. Code Elements Table (Functions, classes, methods)
CREATE TABLE code_elements (
    id SERIAL PRIMARY KEY,
    file_id INTEGER REFERENCES files(id) ON DELETE CASCADE,
    name VARCHAR(255) NOT NULL,
    type VARCHAR(50) CHECK (type IN ('function', 'class', 'method', 'variable', 'constant')),
    signature TEXT,
    docstring TEXT,
    start_line INTEGER,
    end_line INTEGER,
    complexity_score INTEGER,
    dependencies JSONB DEFAULT '[]',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 4. AI Interactions Table (Track model usage)
CREATE TABLE ai_interactions (
    id SERIAL PRIMARY KEY,
    project_id INTEGER REFERENCES projects(id) ON DELETE CASCADE,
    model_name VARCHAR(100),
    query TEXT NOT NULL,
    response TEXT NOT NULL,
    context_files JSONB DEFAULT '[]',
    session_id VARCHAR(100),
    rating INTEGER CHECK (rating >= 1 AND rating <= 5),
    execution_time_ms INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 5. Dependencies Table (Project dependencies)
CREATE TABLE dependencies (
    id SERIAL PRIMARY KEY,
    project_id INTEGER REFERENCES projects(id) ON DELETE CASCADE,
    name VARCHAR(255) NOT NULL,
    version VARCHAR(50),
    type VARCHAR(50) CHECK (type IN ('production', 'development', 'system', 'test')),
    source VARCHAR(100), -- 'pip', 'npm', 'apt', etc.
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(project_id, name, version)
);

-- Create essential indexes for performance
CREATE INDEX idx_files_project_id ON files(project_id);
CREATE INDEX idx_files_path ON files(file_path);
CREATE INDEX idx_files_active ON files(is_active) WHERE is_active = true;
CREATE INDEX idx_code_elements_file_id ON code_elements(file_id);
CREATE INDEX idx_code_elements_name ON code_elements(name);
CREATE INDEX idx_code_elements_type ON code_elements(type);
CREATE INDEX idx_ai_interactions_project_id ON ai_interactions(project_id);
CREATE INDEX idx_ai_interactions_model ON ai_interactions(model_name);
CREATE INDEX idx_dependencies_project_id ON dependencies(project_id);

-- Create a function to update the updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Add trigger to projects table
CREATE TRIGGER update_projects_updated_at 
    BEFORE UPDATE ON projects 
    FOR EACH ROW 
    EXECUTE FUNCTION update_updated_at_column();

-- Insert the Horse Racing AI project as the first entry
INSERT INTO projects (name, description, language, framework, root_path) 
VALUES (
    'Horse Racing AI v2.0',
    'Advanced ML system for horse racing predictions with 4-model ensemble, 76.5% AUC performance, and comprehensive betting strategies',
    'Python',
    'Flask/FastAPI + ML (scikit-learn, TensorFlow)',
    '/home/jc/Documents/Horse-race-ai-v2.01'
);

-- Verify the setup
SELECT 'Database schema Phase 1 created successfully!' as status;
SELECT * FROM projects;

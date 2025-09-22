-- Database initialization script for Learning App microservices
-- This script sets up the PostgreSQL database with optimized indexes and constraints

-- Create database (if running manually)
-- CREATE DATABASE learning_app;
-- \c learning_app;

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Create users table
CREATE TABLE IF NOT EXISTS users (
    id VARCHAR PRIMARY KEY DEFAULT uuid_generate_v4()::text,
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(100) UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create user sessions table
CREATE TABLE IF NOT EXISTS user_sessions (
    id VARCHAR PRIMARY KEY DEFAULT uuid_generate_v4()::text,
    user_id VARCHAR NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    session_token VARCHAR(255) UNIQUE NOT NULL,
    ip_address VARCHAR(45),
    user_agent TEXT,
    expires_at TIMESTAMP NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create PDFs table
CREATE TABLE IF NOT EXISTS pdfs (
    id VARCHAR PRIMARY KEY DEFAULT uuid_generate_v4()::text,
    user_id VARCHAR NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    filename VARCHAR(255) NOT NULL,
    original_filename VARCHAR(255) NOT NULL,
    file_path VARCHAR(500) NOT NULL,
    file_size INTEGER NOT NULL,
    content_hash VARCHAR(64) NOT NULL,
    title VARCHAR(500),
    author VARCHAR(255),
    subject VARCHAR(500),
    pages INTEGER,
    is_processed BOOLEAN DEFAULT FALSE,
    processing_error TEXT,
    uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    processed_at TIMESTAMP
);

-- Create PDF extracted text table
CREATE TABLE IF NOT EXISTS pdf_extracted_text (
    id VARCHAR PRIMARY KEY DEFAULT uuid_generate_v4()::text,
    pdf_id VARCHAR NOT NULL REFERENCES pdfs(id) ON DELETE CASCADE UNIQUE,
    extracted_text TEXT NOT NULL,
    text_length INTEGER NOT NULL,
    extraction_method VARCHAR(50) NOT NULL,
    extracted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create questions table
CREATE TABLE IF NOT EXISTS questions (
    id VARCHAR PRIMARY KEY DEFAULT uuid_generate_v4()::text,
    pdf_id VARCHAR NOT NULL REFERENCES pdfs(id) ON DELETE CASCADE,
    question_set_id VARCHAR NOT NULL,
    question_text TEXT NOT NULL,
    question_type VARCHAR(20) NOT NULL CHECK (question_type IN ('mcq', 'open_ended')),
    topic VARCHAR(255),
    difficulty_level VARCHAR(20) CHECK (difficulty_level IN ('easy', 'medium', 'hard')),
    options JSONB,
    correct_answer VARCHAR(10),
    generation_parameters JSONB,
    cache_key VARCHAR(64) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create chat sessions table
CREATE TABLE IF NOT EXISTS chat_sessions (
    id VARCHAR PRIMARY KEY DEFAULT uuid_generate_v4()::text,
    user_id VARCHAR NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    pdf_id VARCHAR NOT NULL REFERENCES pdfs(id) ON DELETE CASCADE,
    session_name VARCHAR(255),
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create chat messages table
CREATE TABLE IF NOT EXISTS chat_messages (
    id VARCHAR PRIMARY KEY DEFAULT uuid_generate_v4()::text,
    session_id VARCHAR NOT NULL REFERENCES chat_sessions(id) ON DELETE CASCADE,
    message_type VARCHAR(20) NOT NULL CHECK (message_type IN ('user', 'assistant')),
    content TEXT NOT NULL,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    ai_model VARCHAR(50),
    response_time FLOAT
);

-- Create evaluations table
CREATE TABLE IF NOT EXISTS evaluations (
    id VARCHAR PRIMARY KEY DEFAULT uuid_generate_v4()::text,
    user_id VARCHAR NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    question_id VARCHAR NOT NULL REFERENCES questions(id) ON DELETE CASCADE,
    user_answer TEXT NOT NULL,
    score INTEGER NOT NULL CHECK (score >= 0 AND score <= 10),
    max_score INTEGER DEFAULT 10,
    feedback TEXT,
    suggestions TEXT,
    correct_answer_hint TEXT,
    evaluation_level VARCHAR(20) NOT NULL CHECK (evaluation_level IN ('easy', 'medium', 'strict')),
    evaluation_time FLOAT,
    ai_model VARCHAR(50),
    cache_hit BOOLEAN DEFAULT FALSE,
    evaluated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create quiz sessions table
CREATE TABLE IF NOT EXISTS quiz_sessions (
    id VARCHAR PRIMARY KEY DEFAULT uuid_generate_v4()::text,
    user_id VARCHAR NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    pdf_id VARCHAR NOT NULL REFERENCES pdfs(id) ON DELETE CASCADE,
    question_set_id VARCHAR NOT NULL,
    topic VARCHAR(255),
    total_questions INTEGER NOT NULL,
    evaluation_level VARCHAR(20) NOT NULL,
    total_score INTEGER NOT NULL,
    max_score INTEGER NOT NULL,
    percentage FLOAT NOT NULL,
    grade VARCHAR(2) NOT NULL,
    overall_feedback TEXT,
    study_suggestions JSONB,
    strengths JSONB,
    areas_for_improvement JSONB,
    started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP
);

-- Create cache entries table
CREATE TABLE IF NOT EXISTS cache_entries (
    id VARCHAR PRIMARY KEY DEFAULT uuid_generate_v4()::text,
    cache_key VARCHAR(255) UNIQUE NOT NULL,
    cache_type VARCHAR(50) NOT NULL,
    data JSONB NOT NULL,
    expires_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    accessed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    access_count INTEGER DEFAULT 1
);

-- Create background jobs table
CREATE TABLE IF NOT EXISTS background_jobs (
    id VARCHAR PRIMARY KEY DEFAULT uuid_generate_v4()::text,
    job_type VARCHAR(50) NOT NULL,
    status VARCHAR(20) NOT NULL CHECK (status IN ('pending', 'running', 'completed', 'failed')),
    user_id VARCHAR NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    parameters JSONB NOT NULL,
    result JSONB,
    error_message TEXT,
    progress_percentage INTEGER DEFAULT 0 CHECK (progress_percentage >= 0 AND progress_percentage <= 100),
    progress_message VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    started_at TIMESTAMP,
    completed_at TIMESTAMP,
    celery_task_id VARCHAR(255)
);

-- Create indexes for performance optimization

-- User sessions indexes
CREATE INDEX IF NOT EXISTS idx_user_sessions_user_id ON user_sessions(user_id);
CREATE INDEX IF NOT EXISTS idx_user_sessions_token ON user_sessions(session_token);
CREATE INDEX IF NOT EXISTS idx_user_sessions_expires ON user_sessions(expires_at);

-- PDFs indexes
CREATE INDEX IF NOT EXISTS idx_pdfs_user_id ON pdfs(user_id);
CREATE INDEX IF NOT EXISTS idx_pdfs_content_hash ON pdfs(content_hash);
CREATE INDEX IF NOT EXISTS idx_pdfs_processed ON pdfs(is_processed);
CREATE INDEX IF NOT EXISTS idx_pdfs_uploaded_at ON pdfs(uploaded_at);

-- PDF extracted text indexes
CREATE INDEX IF NOT EXISTS idx_pdf_text_pdf_id ON pdf_extracted_text(pdf_id);

-- Questions indexes
CREATE INDEX IF NOT EXISTS idx_questions_pdf_id ON questions(pdf_id);
CREATE INDEX IF NOT EXISTS idx_questions_set_id ON questions(question_set_id);
CREATE INDEX IF NOT EXISTS idx_questions_cache_key ON questions(cache_key);
CREATE INDEX IF NOT EXISTS idx_questions_type ON questions(question_type);
CREATE INDEX IF NOT EXISTS idx_questions_topic ON questions(topic);
CREATE INDEX IF NOT EXISTS idx_questions_created_at ON questions(created_at);

-- Chat sessions indexes
CREATE INDEX IF NOT EXISTS idx_chat_sessions_user_id ON chat_sessions(user_id);
CREATE INDEX IF NOT EXISTS idx_chat_sessions_pdf_id ON chat_sessions(pdf_id);
CREATE INDEX IF NOT EXISTS idx_chat_sessions_active ON chat_sessions(is_active);
CREATE INDEX IF NOT EXISTS idx_chat_sessions_updated_at ON chat_sessions(updated_at);

-- Chat messages indexes
CREATE INDEX IF NOT EXISTS idx_chat_messages_session_id ON chat_messages(session_id);
CREATE INDEX IF NOT EXISTS idx_chat_messages_timestamp ON chat_messages(timestamp);
CREATE INDEX IF NOT EXISTS idx_chat_messages_type ON chat_messages(message_type);

-- Evaluations indexes
CREATE INDEX IF NOT EXISTS idx_evaluations_user_id ON evaluations(user_id);
CREATE INDEX IF NOT EXISTS idx_evaluations_question_id ON evaluations(question_id);
CREATE INDEX IF NOT EXISTS idx_evaluations_score ON evaluations(score);
CREATE INDEX IF NOT EXISTS idx_evaluations_level ON evaluations(evaluation_level);
CREATE INDEX IF NOT EXISTS idx_evaluations_evaluated_at ON evaluations(evaluated_at);
CREATE INDEX IF NOT EXISTS idx_evaluations_cache_hit ON evaluations(cache_hit);

-- Quiz sessions indexes
CREATE INDEX IF NOT EXISTS idx_quiz_sessions_user_id ON quiz_sessions(user_id);
CREATE INDEX IF NOT EXISTS idx_quiz_sessions_pdf_id ON quiz_sessions(pdf_id);
CREATE INDEX IF NOT EXISTS idx_quiz_sessions_completed_at ON quiz_sessions(completed_at);
CREATE INDEX IF NOT EXISTS idx_quiz_sessions_grade ON quiz_sessions(grade);

-- Cache entries indexes
CREATE INDEX IF NOT EXISTS idx_cache_entries_key ON cache_entries(cache_key);
CREATE INDEX IF NOT EXISTS idx_cache_entries_type ON cache_entries(cache_type);
CREATE INDEX IF NOT EXISTS idx_cache_entries_expires ON cache_entries(expires_at);
CREATE INDEX IF NOT EXISTS idx_cache_entries_accessed ON cache_entries(accessed_at);

-- Background jobs indexes
CREATE INDEX IF NOT EXISTS idx_background_jobs_type ON background_jobs(job_type);
CREATE INDEX IF NOT EXISTS idx_background_jobs_status ON background_jobs(status);
CREATE INDEX IF NOT EXISTS idx_background_jobs_user_id ON background_jobs(user_id);
CREATE INDEX IF NOT EXISTS idx_background_jobs_created_at ON background_jobs(created_at);
CREATE INDEX IF NOT EXISTS idx_background_jobs_celery_id ON background_jobs(celery_task_id);

-- Create composite indexes for common query patterns
CREATE INDEX IF NOT EXISTS idx_questions_pdf_topic ON questions(pdf_id, topic);
CREATE INDEX IF NOT EXISTS idx_evaluations_user_question ON evaluations(user_id, question_id);
CREATE INDEX IF NOT EXISTS idx_chat_messages_session_time ON chat_messages(session_id, timestamp);
CREATE INDEX IF NOT EXISTS idx_quiz_sessions_user_completed ON quiz_sessions(user_id, completed_at);

-- Create triggers for updated_at timestamps
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Apply triggers to tables with updated_at columns
CREATE TRIGGER update_users_updated_at BEFORE UPDATE ON users
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_chat_sessions_updated_at BEFORE UPDATE ON chat_sessions
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Create function to clean up expired cache entries
CREATE OR REPLACE FUNCTION cleanup_expired_cache()
RETURNS INTEGER AS $$
DECLARE
    deleted_count INTEGER;
BEGIN
    DELETE FROM cache_entries 
    WHERE expires_at IS NOT NULL AND expires_at < CURRENT_TIMESTAMP;
    
    GET DIAGNOSTICS deleted_count = ROW_COUNT;
    RETURN deleted_count;
END;
$$ LANGUAGE plpgsql;

-- Create function to get user statistics
CREATE OR REPLACE FUNCTION get_user_stats(user_uuid VARCHAR)
RETURNS TABLE(
    total_pdfs INTEGER,
    total_questions INTEGER,
    total_evaluations INTEGER,
    total_quiz_sessions INTEGER,
    average_score FLOAT
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        (SELECT COUNT(*)::INTEGER FROM pdfs WHERE user_id = user_uuid),
        (SELECT COUNT(*)::INTEGER FROM questions q 
         JOIN pdfs p ON q.pdf_id = p.id 
         WHERE p.user_id = user_uuid),
        (SELECT COUNT(*)::INTEGER FROM evaluations WHERE user_id = user_uuid),
        (SELECT COUNT(*)::INTEGER FROM quiz_sessions WHERE user_id = user_uuid),
        (SELECT COALESCE(AVG(percentage), 0)::FLOAT FROM quiz_sessions WHERE user_id = user_uuid);
END;
$$ LANGUAGE plpgsql;

-- Create function to get system performance metrics
CREATE OR REPLACE FUNCTION get_performance_metrics()
RETURNS TABLE(
    avg_question_generation_time FLOAT,
    avg_evaluation_time FLOAT,
    cache_hit_rate FLOAT,
    total_active_users INTEGER
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        (SELECT COALESCE(AVG(EXTRACT(EPOCH FROM (completed_at - created_at))), 0)::FLOAT 
         FROM background_jobs 
         WHERE job_type = 'question_generation' 
         AND status = 'completed' 
         AND created_at > CURRENT_TIMESTAMP - INTERVAL '24 hours'),
        (SELECT COALESCE(AVG(evaluation_time), 0)::FLOAT 
         FROM evaluations 
         WHERE evaluated_at > CURRENT_TIMESTAMP - INTERVAL '24 hours'),
        (SELECT CASE 
                    WHEN COUNT(*) > 0 THEN (COUNT(*) FILTER (WHERE cache_hit = true))::FLOAT / COUNT(*) * 100
                    ELSE 0 
                END
         FROM evaluations 
         WHERE evaluated_at > CURRENT_TIMESTAMP - INTERVAL '24 hours'),
        (SELECT COUNT(DISTINCT user_id)::INTEGER 
         FROM user_sessions 
         WHERE expires_at > CURRENT_TIMESTAMP);
END;
$$ LANGUAGE plpgsql;

-- Insert default admin user (password: 'admin123' - change in production!)
INSERT INTO users (username, email, password_hash) 
VALUES ('admin', 'admin@learningapp.com', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPj/RK.PmvlG.') 
ON CONFLICT (username) DO NOTHING;

-- Create indexes for full-text search on questions and PDF content
CREATE INDEX IF NOT EXISTS idx_questions_text_search ON questions USING gin(to_tsvector('english', question_text));
CREATE INDEX IF NOT EXISTS idx_pdf_text_search ON pdf_extracted_text USING gin(to_tsvector('english', extracted_text));

-- Grant permissions (adjust as needed for your setup)
-- GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO learning_app_user;
-- GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO learning_app_user;
-- GRANT ALL PRIVILEGES ON ALL FUNCTIONS IN SCHEMA public TO learning_app_user;

-- Create a view for question statistics
CREATE OR REPLACE VIEW question_stats AS
SELECT 
    pdf_id,
    COUNT(*) as total_questions,
    COUNT(*) FILTER (WHERE question_type = 'mcq') as mcq_questions,
    COUNT(*) FILTER (WHERE question_type = 'open_ended') as open_ended_questions,
    COUNT(DISTINCT topic) as unique_topics,
    MIN(created_at) as first_generated,
    MAX(created_at) as last_generated
FROM questions
GROUP BY pdf_id;

-- Create a view for evaluation statistics
CREATE OR REPLACE VIEW evaluation_stats AS
SELECT 
    user_id,
    COUNT(*) as total_evaluations,
    AVG(score) as average_score,
    COUNT(*) FILTER (WHERE cache_hit = true) as cache_hits,
    COUNT(*) FILTER (WHERE cache_hit = false) as cache_misses,
    AVG(evaluation_time) as avg_evaluation_time
FROM evaluations
GROUP BY user_id;

COMMIT;

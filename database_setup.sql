-- Database Setup Script for Legal Agent Platform
-- Run this as a PostgreSQL superuser (e.g., postgres user)

-- Connect to the database
\c legal_agent_db

-- Grant necessary permissions to legal_agent_user
GRANT ALL PRIVILEGES ON SCHEMA public TO legal_agent_user;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO legal_agent_user;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO legal_agent_user;

-- Grant default privileges for future objects
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL PRIVILEGES ON TABLES TO legal_agent_user;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL PRIVILEGES ON SEQUENCES TO legal_agent_user;

-- Make legal_agent_user the owner of the public schema
ALTER SCHEMA public OWNER TO legal_agent_user;

-- Verify pgvector extension is installed
CREATE EXTENSION IF NOT EXISTS vector;

-- Show current user and privileges
SELECT current_user, current_database();
\dp

-- Success message
\echo 'Database setup completed successfully!'
\echo 'You can now run: python manage.py migrate'


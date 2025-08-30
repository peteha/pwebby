-- Initialize database for Docker PostgreSQL
-- This script runs when the PostgreSQL container first starts

-- Create the images table
CREATE TABLE IF NOT EXISTS images (
    id SERIAL PRIMARY KEY,
    filename VARCHAR(255) NOT NULL,
    data BYTEA NOT NULL,
    description TEXT,
    upload_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_images_filename ON images(filename);
CREATE INDEX IF NOT EXISTS idx_images_upload_date ON images(upload_date);

-- Grant permissions to the application user
GRANT ALL PRIVILEGES ON TABLE images TO gallery_user;
GRANT USAGE, SELECT ON SEQUENCE images_id_seq TO gallery_user;

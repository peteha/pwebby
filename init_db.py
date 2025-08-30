#!/usr/bin/env python3
"""
Database initialization script for Image Gallery
Run this script to set up the database schema
"""

import psycopg2
import sys
from dotenv import load_dotenv

load_dotenv()

# Database configuration
DB_CONFIG = {
    'host': 'pgblin1.pgnet.io',
    'database': 'dbadmin',
    'user': 'dbadmin',
    'password': 'pgdb##123'
}

def init_database():
    """Initialize the database schema"""
    try:
        # Connect to PostgreSQL
        print("Connecting to PostgreSQL database...")
        conn = psycopg2.connect(**DB_CONFIG)
        cur = conn.cursor()
        
        print("Creating images table...")
        # Create images table
        cur.execute('''
            CREATE TABLE IF NOT EXISTS images (
                id SERIAL PRIMARY KEY,
                filename VARCHAR(255) NOT NULL,
                image_data BYTEA NOT NULL,
                content_type VARCHAR(50) NOT NULL,
                upload_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        ''')
        
        print("Creating indexes...")
        # Create index on upload_date for faster queries
        cur.execute('''
            CREATE INDEX IF NOT EXISTS idx_images_upload_date 
            ON images (upload_date DESC);
        ''')
        
        # Commit changes
        conn.commit()
        print("✅ Database schema created successfully!")
        
        # Show table info
        cur.execute('''
            SELECT COUNT(*) FROM images;
        ''')
        count = cur.fetchone()[0]
        print(f"📊 Current images in database: {count}")
        
        cur.close()
        conn.close()
        
    except psycopg2.Error as e:
        print(f"❌ Database error: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    print("🚀 Initializing Image Gallery Database...")
    init_database()
    print("🎉 Database initialization complete!")

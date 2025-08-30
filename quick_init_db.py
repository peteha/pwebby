#!/usr/bin/env python3
"""
Quick Database Setup Script
Simple version for rapid database initialization
"""

import os
import psycopg2
import sqlite3
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def quick_init():
    """Quick database initialization"""
    db_type = os.environ.get('DATABASE_TYPE', 'sqlite').lower()
    
    if db_type == 'postgresql':
        # PostgreSQL setup
        config = {
            'host': os.environ.get('POSTGRES_HOST'),
            'database': os.environ.get('POSTGRES_DATABASE'),
            'user': os.environ.get('POSTGRES_USER'),
            'password': os.environ.get('POSTGRES_PASSWORD'),
            'port': int(os.environ.get('POSTGRES_PORT', 5432)),
        }
        
        print(f"🐘 Setting up PostgreSQL: {config['database']}@{config['host']}")
        
        try:
            # Create database if needed
            temp_config = config.copy()
            temp_config['database'] = 'postgres'
            
            with psycopg2.connect(**temp_config) as conn:
                conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
                with conn.cursor() as cur:
                    cur.execute("SELECT 1 FROM pg_catalog.pg_database WHERE datname = %s", 
                               (config['database'],))
                    if not cur.fetchone():
                        cur.execute(f'CREATE DATABASE "{config["database"]}"')
                        print(f"✅ Created database: {config['database']}")
            
            # Create tables
            with psycopg2.connect(**config) as conn:
                with conn.cursor() as cur:
                    cur.execute('''
                        CREATE TABLE IF NOT EXISTS images (
                            id SERIAL PRIMARY KEY,
                            filename VARCHAR(255) NOT NULL,
                            image_data BYTEA NOT NULL,
                            content_type VARCHAR(50) NOT NULL,
                            description TEXT,
                            upload_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                        );
                        CREATE INDEX IF NOT EXISTS idx_images_upload_date 
                        ON images (upload_date DESC);
                    ''')
                    print("✅ Tables created successfully")
                    
        except Exception as e:
            print(f"❌ Error: {e}")
            return False
            
    else:
        # SQLite setup
        db_path = os.environ.get('SQLITE_DATABASE', 'images.db')
        print(f"🗃️  Setting up SQLite: {db_path}")
        
        try:
            with sqlite3.connect(db_path) as conn:
                cur = conn.cursor()
                cur.execute('''
                    CREATE TABLE IF NOT EXISTS images (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        filename TEXT NOT NULL,
                        image_data BLOB NOT NULL,
                        content_type TEXT NOT NULL,
                        description TEXT,
                        upload_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    );
                ''')
                cur.execute('''
                    CREATE INDEX IF NOT EXISTS idx_images_upload_date 
                    ON images (upload_date DESC);
                ''')
                print("✅ Tables created successfully")
                
        except Exception as e:
            print(f"❌ Error: {e}")
            return False
    
    print("🎉 Database ready!")
    return True

if __name__ == "__main__":
    quick_init()

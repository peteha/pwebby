#!/usr/bin/env python3
"""
Comprehensive Database Initialization Script
Creates database if it doesn't exist and initializes all tables
"""

import os
import sys
import psycopg2
import sqlite3
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def get_postgres_config():
    """Get PostgreSQL configuration from environment variables"""
    return {
        'host': os.environ.get('POSTGRES_HOST', 'localhost'),
        'database': os.environ.get('POSTGRES_DATABASE', 'imagedb'),
        'user': os.environ.get('POSTGRES_USER', 'postgres'),
        'password': os.environ.get('POSTGRES_PASSWORD', ''),
        'port': int(os.environ.get('POSTGRES_PORT', 5432)),
        'sslmode': os.environ.get('POSTGRES_SSLMODE', 'prefer'),
        'connect_timeout': int(os.environ.get('POSTGRES_CONNECT_TIMEOUT', 10))
    }

def create_postgresql_database():
    """Create PostgreSQL database if it doesn't exist"""
    config = get_postgres_config()
    db_name = config['database']
    
    # Connect to PostgreSQL server (not to specific database)
    temp_config = config.copy()
    temp_config['database'] = 'postgres'  # Connect to default database
    
    try:
        print(f"🔗 Connecting to PostgreSQL server at {config['host']}...")
        conn = psycopg2.connect(**temp_config)
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        cur = conn.cursor()
        
        # Check if database exists
        cur.execute("SELECT 1 FROM pg_catalog.pg_database WHERE datname = %s", (db_name,))
        exists = cur.fetchone()
        
        if exists:
            print(f"✅ Database '{db_name}' already exists")
        else:
            print(f"🚀 Creating database '{db_name}'...")
            cur.execute(f'CREATE DATABASE "{db_name}"')
            print(f"✅ Database '{db_name}' created successfully")
        
        cur.close()
        conn.close()
        return True
        
    except psycopg2.Error as e:
        print(f"❌ Error connecting to PostgreSQL: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

def init_postgresql_tables():
    """Initialize PostgreSQL tables"""
    config = get_postgres_config()
    
    try:
        print(f"🔗 Connecting to database '{config['database']}'...")
        conn = psycopg2.connect(**config)
        cur = conn.cursor()
        
        print("🏗️  Creating images table...")
        cur.execute('''
            CREATE TABLE IF NOT EXISTS images (
                id SERIAL PRIMARY KEY,
                filename VARCHAR(255) NOT NULL,
                image_data BYTEA NOT NULL,
                content_type VARCHAR(50) NOT NULL,
                description TEXT,
                upload_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        ''')
        
        # Add description column if it doesn't exist (for existing databases)
        print("🔧 Checking if description column exists...")
        cur.execute('''
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name='images' AND column_name='description';
        ''')
        
        if not cur.fetchone():
            print("➕ Adding description column...")
            cur.execute('ALTER TABLE images ADD COLUMN description TEXT;')
        else:
            print("✅ Description column already exists")
        
        # Create index on upload_date for faster queries
        print("📊 Creating index on upload_date...")
        cur.execute('''
            CREATE INDEX IF NOT EXISTS idx_images_upload_date 
            ON images (upload_date DESC);
        ''')
        
        conn.commit()
        print("✅ PostgreSQL tables initialized successfully")
        
        # Display table info
        cur.execute('''
            SELECT column_name, data_type, is_nullable 
            FROM information_schema.columns 
            WHERE table_name = 'images' 
            ORDER BY ordinal_position;
        ''')
        
        columns = cur.fetchall()
        print("\n📋 Table Structure:")
        for col in columns:
            print(f"   - {col[0]}: {col[1]} ({'nullable' if col[2] == 'YES' else 'not null'})")
        
        cur.close()
        conn.close()
        return True
        
    except psycopg2.Error as e:
        print(f"❌ PostgreSQL error: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

def init_sqlite_tables():
    """Initialize SQLite tables"""
    db_path = os.environ.get('SQLITE_DATABASE', 'images.db')
    
    try:
        print(f"🔗 Connecting to SQLite database: {db_path}")
        conn = sqlite3.connect(db_path)
        cur = conn.cursor()
        
        print("🏗️  Creating images table...")
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
        
        # Add description column if it doesn't exist (for existing databases)
        print("🔧 Checking if description column exists...")
        try:
            cur.execute('ALTER TABLE images ADD COLUMN description TEXT;')
            print("➕ Added description column")
        except sqlite3.OperationalError:
            print("✅ Description column already exists")
        
        # Create index on upload_date for faster queries
        print("📊 Creating index on upload_date...")
        cur.execute('''
            CREATE INDEX IF NOT EXISTS idx_images_upload_date 
            ON images (upload_date DESC);
        ''')
        
        conn.commit()
        print("✅ SQLite tables initialized successfully")
        
        # Display table info
        cur.execute("PRAGMA table_info(images);")
        columns = cur.fetchall()
        print("\n📋 Table Structure:")
        for col in columns:
            nullable = "nullable" if col[3] == 0 else "not null"
            print(f"   - {col[1]}: {col[2]} ({nullable})")
        
        cur.close()
        conn.close()
        return True
        
    except sqlite3.Error as e:
        print(f"❌ SQLite error: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

def main():
    """Main initialization function"""
    print("🚀 Starting Database Initialization...")
    print("=" * 50)
    
    # Get database type from environment
    db_type = os.environ.get('DATABASE_TYPE', 'sqlite').lower()
    print(f"🔧 Database type: {db_type.upper()}")
    
    success = False
    
    if db_type == 'postgresql':
        print("\n🐘 Initializing PostgreSQL Database...")
        print("-" * 40)
        
        # Step 1: Create database if needed
        if create_postgresql_database():
            # Step 2: Initialize tables
            success = init_postgresql_tables()
        
    elif db_type == 'sqlite':
        print("\n🗃️  Initializing SQLite Database...")
        print("-" * 40)
        success = init_sqlite_tables()
        
    else:
        print(f"❌ Unsupported database type: {db_type}")
        print("   Supported types: postgresql, sqlite")
        sys.exit(1)
    
    print("\n" + "=" * 50)
    if success:
        print("🎉 Database initialization completed successfully!")
        print(f"   Database type: {db_type.upper()}")
        if db_type == 'postgresql':
            config = get_postgres_config()
            print(f"   Host: {config['host']}")
            print(f"   Database: {config['database']}")
        else:
            print(f"   Database file: {os.environ.get('SQLITE_DATABASE', 'images.db')}")
    else:
        print("💥 Database initialization failed!")
        sys.exit(1)

if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""
Database Management Utility
Complete database operations for the image gallery
"""

import os
import sys
import argparse
import psycopg2
import sqlite3
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class DatabaseManager:
    def __init__(self):
        self.db_type = os.environ.get('DATABASE_TYPE', 'sqlite').lower()
        self.postgres_config = self._get_postgres_config()
        self.sqlite_db = os.environ.get('SQLITE_DATABASE', 'images.db')
    
    def _get_postgres_config(self):
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
    
    def create_database(self):
        """Create database if it doesn't exist"""
        if self.db_type == 'postgresql':
            return self._create_postgresql_database()
        elif self.db_type == 'sqlite':
            print("📁 SQLite database will be created automatically")
            return True
        else:
            print(f"❌ Unsupported database type: {self.db_type}")
            return False
    
    def _create_postgresql_database(self):
        """Create PostgreSQL database if it doesn't exist"""
        config = self.postgres_config
        db_name = config['database']
        
        temp_config = config.copy()
        temp_config['database'] = 'postgres'
        
        try:
            print(f"🔗 Connecting to PostgreSQL server at {config['host']}...")
            with psycopg2.connect(**temp_config) as conn:
                conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
                with conn.cursor() as cur:
                    cur.execute("SELECT 1 FROM pg_catalog.pg_database WHERE datname = %s", (db_name,))
                    if cur.fetchone():
                        print(f"✅ Database '{db_name}' already exists")
                    else:
                        print(f"🚀 Creating database '{db_name}'...")
                        cur.execute(f'CREATE DATABASE "{db_name}"')
                        print(f"✅ Database '{db_name}' created successfully")
            return True
        except Exception as e:
            print(f"❌ Error: {e}")
            return False
    
    def init_tables(self):
        """Initialize database tables"""
        if self.db_type == 'postgresql':
            return self._init_postgresql_tables()
        elif self.db_type == 'sqlite':
            return self._init_sqlite_tables()
        else:
            print(f"❌ Unsupported database type: {self.db_type}")
            return False
    
    def _init_postgresql_tables(self):
        """Initialize PostgreSQL tables"""
        try:
            with psycopg2.connect(**self.postgres_config) as conn:
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
                    print("✅ PostgreSQL tables initialized")
            return True
        except Exception as e:
            print(f"❌ PostgreSQL error: {e}")
            return False
    
    def _init_sqlite_tables(self):
        """Initialize SQLite tables"""
        try:
            with sqlite3.connect(self.sqlite_db) as conn:
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
                print("✅ SQLite tables initialized")
            return True
        except Exception as e:
            print(f"❌ SQLite error: {e}")
            return False
    
    def show_status(self):
        """Show database status"""
        print(f"🔧 Database type: {self.db_type.upper()}")
        
        if self.db_type == 'postgresql':
            print(f"   Host: {self.postgres_config['host']}")
            print(f"   Database: {self.postgres_config['database']}")
            print(f"   User: {self.postgres_config['user']}")
            try:
                with psycopg2.connect(**self.postgres_config) as conn:
                    with conn.cursor() as cur:
                        cur.execute("SELECT COUNT(*) FROM images")
                        count = cur.fetchone()[0]
                        print(f"   Images: {count}")
                        print("   Status: ✅ Connected")
            except Exception as e:
                print(f"   Status: ❌ Error: {e}")
        else:
            print(f"   Database file: {self.sqlite_db}")
            try:
                with sqlite3.connect(self.sqlite_db) as conn:
                    cur = conn.cursor()
                    cur.execute("SELECT COUNT(*) FROM images")
                    count = cur.fetchone()[0]
                    print(f"   Images: {count}")
                    print("   Status: ✅ Connected")
            except Exception as e:
                print(f"   Status: ❌ Error: {e}")
    
    def reset_database(self):
        """Reset database (drop and recreate tables)"""
        print("⚠️  WARNING: This will delete all images!")
        confirm = input("Type 'yes' to confirm: ")
        if confirm.lower() != 'yes':
            print("❌ Operation cancelled")
            return False
        
        if self.db_type == 'postgresql':
            try:
                with psycopg2.connect(**self.postgres_config) as conn:
                    with conn.cursor() as cur:
                        cur.execute("DROP TABLE IF EXISTS images")
                        print("🗑️  Dropped images table")
                return self._init_postgresql_tables()
            except Exception as e:
                print(f"❌ Error: {e}")
                return False
        else:
            try:
                with sqlite3.connect(self.sqlite_db) as conn:
                    cur = conn.cursor()
                    cur.execute("DROP TABLE IF EXISTS images")
                    print("🗑️  Dropped images table")
                return self._init_sqlite_tables()
            except Exception as e:
                print(f"❌ Error: {e}")
                return False

def main():
    parser = argparse.ArgumentParser(description='Database Management Utility')
    parser.add_argument('action', choices=['init', 'create', 'status', 'reset'], 
                       help='Action to perform')
    parser.add_argument('--force', action='store_true', help='Force operation without confirmation')
    
    args = parser.parse_args()
    
    db_manager = DatabaseManager()
    
    print("🗄️  Database Management Utility")
    print("=" * 40)
    
    if args.action == 'init':
        print("🚀 Initializing database...")
        if db_manager.create_database() and db_manager.init_tables():
            print("🎉 Database initialized successfully!")
        else:
            print("💥 Database initialization failed!")
            sys.exit(1)
    
    elif args.action == 'create':
        print("🚀 Creating database...")
        if db_manager.create_database():
            print("✅ Database created successfully!")
        else:
            print("❌ Database creation failed!")
            sys.exit(1)
    
    elif args.action == 'status':
        print("📊 Database Status:")
        db_manager.show_status()
    
    elif args.action == 'reset':
        if db_manager.reset_database():
            print("✅ Database reset successfully!")
        else:
            print("❌ Database reset failed!")
            sys.exit(1)

if __name__ == "__main__":
    if len(sys.argv) == 1:
        # Default action if no arguments provided
        db_manager = DatabaseManager()
        print("🗄️  Database Management Utility")
        print("=" * 40)
        print("🚀 Running full initialization...")
        if db_manager.create_database() and db_manager.init_tables():
            print("\n📊 Final Status:")
            db_manager.show_status()
            print("\n🎉 Database ready!")
        else:
            print("💥 Initialization failed!")
            sys.exit(1)
    else:
        main()

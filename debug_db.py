#!/usr/bin/env python3

import psycopg2
from psycopg2 import sql
import os
from dotenv import load_dotenv
import base64

# Load environment variables
load_dotenv()

# Database configuration - same as app.py
DB_CONFIG = {
    'host': 'pgdblin1.pgnet.io',
    'database': 'pgimagedb',
    'user': 'dbadmin',
    'password': 'pgdb##123',
    'port': 5432,
    'sslmode': 'prefer',
    'connect_timeout': 10
}

# Connect to database
try:
    conn = psycopg2.connect(**DB_CONFIG)
    print("Connected to PostgreSQL database")
except Exception as e:
    print(f"PostgreSQL connection failed: {e}")
    exit(1)

cur = conn.cursor()

# Check table structure
print("=== DATABASE SCHEMA ===")
cur.execute('SELECT column_name, data_type FROM information_schema.columns WHERE table_name = %s', ('images',))
columns = cur.fetchall()
print('Database schema:')
for col in columns:
    print(f'  {col[0]}: {col[1]}')

# Check actual data
print("\n=== SAMPLE DATA ===")
cur.execute('SELECT id, filename, content_type, LENGTH(image_data) as data_length FROM images LIMIT 3')
images = cur.fetchall()
print('Sample data:')
for img in images:
    print(f'  ID: {img[0]}, filename: {img[1]}, content_type: {img[2]}, data_length: {img[3]}')

# Check if data is already base64 or binary
print("\n=== DATA FORMAT ANALYSIS ===")
if images:
    cur.execute('SELECT image_data FROM images LIMIT 1')
    sample_data = cur.fetchone()[0]
    print(f'Data type: {type(sample_data)}')
    if isinstance(sample_data, str):
        print('Data is stored as string (likely base64)')
        print(f'First 50 chars: {sample_data[:50]}...')
        # Try to decode as base64
        try:
            decoded = base64.b64decode(sample_data)
            print(f'Successfully decoded base64, binary length: {len(decoded)}')
            # Check if it looks like image data
            if decoded.startswith(b'\xff\xd8\xff'):
                print('Data appears to be JPEG')
            elif decoded.startswith(b'\x89PNG'):
                print('Data appears to be PNG')
            else:
                print(f'Unknown image format, starts with: {decoded[:10]}')
        except Exception as e:
            print(f'Failed to decode as base64: {e}')
    else:
        print('Data is stored as binary')
        print(f'Binary length: {len(sample_data)}')
        if sample_data.startswith(b'\xff\xd8\xff'):
            print('Data appears to be JPEG')
        elif sample_data.startswith(b'\x89PNG'):
            print('Data appears to be PNG')
        else:
            print(f'Unknown image format, starts with: {sample_data[:10]}')

cur.close()
conn.close()

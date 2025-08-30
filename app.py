from flask import Flask, render_template, request, jsonify, redirect, url_for, flash
import psycopg2
import psycopg2.extras
import sqlite3
from PIL import Image
import io
import base64
import os
from datetime import datetime
from dotenv import load_dotenv
import requests
import threading
from concurrent.futures import ThreadPoolExecutor
import tempfile
import random
import pandas as pd
import json

# Load environment variables
load_dotenv()

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'fallback-secret-key')

# Database configuration from environment variables
DATABASE_TYPE = os.environ.get('DATABASE_TYPE', 'sqlite').lower()

# PostgreSQL configuration
POSTGRES_CONFIG = {
    'host': os.environ.get('POSTGRES_HOST', 'localhost'),
    'database': os.environ.get('POSTGRES_DATABASE', 'imagedb'),
    'user': os.environ.get('POSTGRES_USER', 'postgres'),
    'password': os.environ.get('POSTGRES_PASSWORD', ''),
    'port': int(os.environ.get('POSTGRES_PORT', 5432)),
    'sslmode': os.environ.get('POSTGRES_SSLMODE', 'prefer'),
    'connect_timeout': int(os.environ.get('POSTGRES_CONNECT_TIMEOUT', 10))
}

# SQLite configuration
SQLITE_DB = os.environ.get('SQLITE_DATABASE', 'images.db')

# Ensure data directory exists for SQLite (especially in Docker)
if DATABASE_TYPE == 'sqlite':
    db_dir = os.path.dirname(SQLITE_DB) if os.path.dirname(SQLITE_DB) else '.'
    if db_dir != '.' and not os.path.exists(db_dir):
        os.makedirs(db_dir, exist_ok=True)

# Application settings
MAX_UPLOAD_SIZE = int(os.environ.get('MAX_UPLOAD_SIZE', 16777216))  # 16MB default
ALLOWED_EXTENSIONS = set(os.environ.get('ALLOWED_EXTENSIONS', 'jpg,jpeg,png,gif').split(','))
DEFAULT_PAGINATION = int(os.environ.get('DEFAULT_PAGINATION', 8))
MAX_WORKERS = int(os.environ.get('MAX_WORKERS', 8))
DOWNLOAD_TIMEOUT = int(os.environ.get('DOWNLOAD_TIMEOUT', 15))
LAION_CSV_FILE = os.environ.get('LAION_CSV_FILE', 'laion_sample.csv')

# Set file upload size limit
app.config['MAX_CONTENT_LENGTH'] = MAX_UPLOAD_SIZE

# Determine which database to use
USE_SQLITE = DATABASE_TYPE == 'sqlite'

def get_db_connection():
    """Create database connection based on environment configuration"""
    global USE_SQLITE
    
    if not USE_SQLITE:
        try:
            print("Attempting to connect to PostgreSQL database...")
            conn = psycopg2.connect(**POSTGRES_CONFIG)
            print("Connected to PostgreSQL database")
            return conn
        except Exception as e:
            print(f"PostgreSQL connection failed: {e}")
            print("Falling back to SQLite database...")
            USE_SQLITE = True
    
    if USE_SQLITE:
        try:
            print(f"Connecting to SQLite database: {SQLITE_DB}")
            conn = sqlite3.connect(SQLITE_DB)
            print("Connected to SQLite database")
            return conn
        except Exception as e:
            print(f"SQLite connection error: {e}")
            return None

def init_db():
    """Initialize database schema"""
    conn = get_db_connection()
    if conn:
        try:
            cur = conn.cursor()
            
            if USE_SQLITE:
                # Create images table for SQLite
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
                try:
                    cur.execute('ALTER TABLE images ADD COLUMN description TEXT;')
                except:
                    pass  # Column already exists
                
                # Create index on upload_date for faster queries
                cur.execute('''
                    CREATE INDEX IF NOT EXISTS idx_images_upload_date 
                    ON images (upload_date DESC);
                ''')
            else:
                # Create images table for PostgreSQL
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
                try:
                    cur.execute('ALTER TABLE images ADD COLUMN description TEXT;')
                except:
                    pass  # Column already exists
                
                # Create index on upload_date for faster queries
                cur.execute('''
                    CREATE INDEX IF NOT EXISTS idx_images_upload_date 
                    ON images (upload_date DESC);
                ''')
            
            conn.commit()
            cur.close()
            conn.close()
            db_type = "SQLite" if USE_SQLITE else "PostgreSQL"
            print(f"Database initialized successfully using {db_type}")
        except Exception as e:
            print(f"Database initialization error: {e}")
            if conn:
                conn.rollback()

def maintain_image_limit():
    """Keep only the latest 100 images"""
    conn = get_db_connection()
    if conn:
        try:
            cur = conn.cursor()
            cur.execute('''
                DELETE FROM images 
                WHERE id NOT IN (
                    SELECT id FROM images 
                    ORDER BY upload_date DESC 
                    LIMIT 100
                );
            ''')
            conn.commit()
            cur.close()
            conn.close()
        except Exception as e:
            print(f"Error maintaining image limit: {e}")

def validate_image(file):
    """Validate uploaded image file using environment configuration"""
    if not file or file.filename == '':
        return False, "No file selected"
    
    file_extension = file.filename.rsplit('.', 1)[1].lower() if '.' in file.filename else ''
    
    if file_extension not in ALLOWED_EXTENSIONS:
        return False, f"Invalid file type. Only {', '.join(ALLOWED_EXTENSIONS).upper()} files are allowed"
    
    try:
        # Check if it's a valid image
        image = Image.open(file.stream)
        image.verify()
        file.stream.seek(0)  # Reset stream position
        return True, "Valid image"
    except Exception as e:
        return False, f"Invalid image file: {str(e)}"

@app.route('/')
@app.route('/page/<int:page>')
def index(page=1):
    """Main page showing images with pagination"""
    per_page = DEFAULT_PAGINATION
    offset = (page - 1) * per_page
    
    conn = get_db_connection()
    images = []
    total_images = 0
    total_pages = 0
    
    if conn:
        try:
            # Get total count of images
            cur = conn.cursor()
            cur.execute('SELECT COUNT(*) FROM images')
            total_images = cur.fetchone()[0]
            total_pages = (total_images + per_page - 1) // per_page
            
            if USE_SQLITE:
                cur.execute('''
                    SELECT id, filename, image_data, content_type, upload_date, description
                    FROM images 
                    ORDER BY upload_date DESC 
                    LIMIT ? OFFSET ?
                ''', (per_page, offset))
                rows = cur.fetchall()
                for row in rows:
                    # Check if image_data is already base64 string or binary
                    if isinstance(row[2], str):
                        # Already base64 string
                        image_base64 = row[2]
                    else:
                        # Binary data (including memoryview), convert to base64
                        if isinstance(row[2], memoryview):
                            # Convert memoryview to bytes first
                            binary_data = bytes(row[2])
                        else:
                            binary_data = row[2]
                        image_base64 = base64.b64encode(binary_data).decode('utf-8')
                    images.append({
                        'id': row[0],
                        'filename': row[1],
                        'data': image_base64,
                        'content_type': row[3],
                        'upload_date': row[4],
                        'description': row[5] if len(row) > 5 else None
                    })
            else:
                cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
                cur.execute('''
                    SELECT id, filename, image_data, content_type, upload_date, description
                    FROM images 
                    ORDER BY upload_date DESC 
                    LIMIT %s OFFSET %s
                ''', (per_page, offset))
                rows = cur.fetchall()
                for row in rows:
                    # Check if image_data is already base64 string or binary
                    if isinstance(row['image_data'], str):
                        # Already base64 string
                        image_base64 = row['image_data']
                    else:
                        # Binary data (including memoryview from PostgreSQL), convert to base64
                        if isinstance(row['image_data'], memoryview):
                            # Convert memoryview to bytes first
                            binary_data = bytes(row['image_data'])
                        else:
                            binary_data = row['image_data']
                        image_base64 = base64.b64encode(binary_data).decode('utf-8')
                    images.append({
                        'id': row['id'],
                        'filename': row['filename'],
                        'data': image_base64,
                        'content_type': row['content_type'],
                        'upload_date': row['upload_date'],
                        'description': row.get('description')
                    })
            
            cur.close()
            conn.close()
        except Exception as e:
            flash(f"Error loading images: {str(e)}", 'error')
    
    return render_template('index.html', 
                         images=images,
                         current_page=page,
                         total_pages=total_pages,
                         total_images=total_images,
                         has_prev=page > 1,
                         has_next=page < total_pages,
                         prev_page=page - 1 if page > 1 else None,
                         next_page=page + 1 if page < total_pages else None)

@app.route('/upload', methods=['GET', 'POST'])
def upload():
    """Upload page"""
    if request.method == 'POST':
        if 'file' not in request.files:
            flash('No file selected', 'error')
            return redirect(request.url)
        
        file = request.files['file']
        is_valid, message = validate_image(file)
        
        if not is_valid:
            flash(message, 'error')
            return redirect(request.url)
        
        # Save image to database
        conn = get_db_connection()
        if conn:
            try:
                cur = conn.cursor()
                image_data = file.read()
                
                cur.execute('''
                    INSERT INTO images (filename, image_data, content_type)
                    VALUES (%s, %s, %s)
                ''', (file.filename, image_data, file.content_type))
                
                conn.commit()
                cur.close()
                conn.close()
                
                # Maintain 100 image limit
                maintain_image_limit()
                
                flash('Image uploaded successfully!', 'success')
                return redirect(url_for('index'))
                
            except Exception as e:
                flash(f'Error uploading image: {str(e)}', 'error')
                if conn:
                    conn.rollback()
        else:
            flash('Database connection error', 'error')
    
    return render_template('upload.html')

@app.route('/delete/<int:image_id>', methods=['POST'])
def delete_image(image_id):
    """Delete a specific image"""
    conn = get_db_connection()
    if conn:
        try:
            cur = conn.cursor()
            cur.execute('DELETE FROM images WHERE id = %s', (image_id,))
            conn.commit()
            cur.close()
            conn.close()
            flash('Image deleted successfully!', 'success')
        except Exception as e:
            flash(f'Error deleting image: {str(e)}', 'error')
    
    return redirect(url_for('index'))

@app.route('/delete_all', methods=['POST'])
def delete_all():
    """Delete all images"""
    conn = get_db_connection()
    if conn:
        try:
            cur = conn.cursor()
            cur.execute('DELETE FROM images')
            conn.commit()
            cur.close()
            conn.close()
            flash('All images deleted successfully!', 'success')
        except Exception as e:
            flash(f'Error deleting images: {str(e)}', 'error')
    
    return redirect(url_for('index'))

@app.route('/api/upload', methods=['POST'])
def api_upload():
    """API endpoint for uploading images"""
    if 'file' not in request.files:
        return jsonify({'error': 'No file provided'}), 400
    
    file = request.files['file']
    is_valid, message = validate_image(file)
    
    if not is_valid:
        return jsonify({'error': message}), 400
    
    conn = get_db_connection()
    if conn:
        try:
            cur = conn.cursor()
            image_data = file.read()
            
            cur.execute('''
                INSERT INTO images (filename, image_data, content_type)
                VALUES (%s, %s, %s)
                RETURNING id
            ''', (file.filename, image_data, file.content_type))
            
            image_id = cur.fetchone()[0]
            conn.commit()
            cur.close()
            conn.close()
            
            # Maintain 100 image limit
            maintain_image_limit()
            
            return jsonify({
                'message': 'Image uploaded successfully',
                'image_id': image_id
            }), 201
            
        except Exception as e:
            return jsonify({'error': f'Database error: {str(e)}'}), 500
    
    return jsonify({'error': 'Database connection failed'}), 500

@app.route('/api/images')
def api_images():
    """API endpoint to get all images metadata"""
    conn = get_db_connection()
    if conn:
        try:
            if USE_SQLITE:
                cur = conn.cursor()
                cur.execute('''
                    SELECT id, filename, content_type, upload_date
                    FROM images 
                    ORDER BY upload_date DESC
                ''')
                rows = cur.fetchall()
                images = []
                for row in rows:
                    images.append({
                        'id': row['id'],
                        'filename': row['filename'],
                        'content_type': row['content_type'],
                        'upload_date': row['upload_date']
                    })
            else:
                cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
                cur.execute('''
                    SELECT id, filename, content_type, upload_date
                    FROM images 
                    ORDER BY upload_date DESC
                ''')
                images = cur.fetchall()
                # Convert datetime objects to strings for PostgreSQL
                for image in images:
                    if hasattr(image['upload_date'], 'isoformat'):
                        image['upload_date'] = image['upload_date'].isoformat()
            
            cur.close()
            conn.close()
            
            return jsonify(images)
            
        except Exception as e:
            return jsonify({'error': f'Database error: {str(e)}'}), 500
    
    return jsonify({'error': 'Database connection failed'}), 500

# Global variable to track populate progress
populate_progress = {'current': 0, 'total': 0, 'status': 'idle', 'message': '', 'uploaded': 0}

@app.route('/api/populate', methods=['POST'])
def start_populate():
    """Start the image population process"""
    import time
    
    data = request.get_json() or {}
    target = data.get('target', 20)  # Default to 20 images
    
    # Reset progress
    populate_progress.update({
        'current': 0,
        'total': target,
        'status': 'running',
        'message': 'Starting image population...',
        'uploaded': 0
    })
    
    def populate_images():
        """Background function to populate images using LAION dataset"""
        print(f"🚀 Starting LAION population process for {target} images...")
        try:
            # Load LAION sample dataset
            laion_file = os.path.join(os.path.dirname(__file__), LAION_CSV_FILE)
            if not os.path.exists(laion_file):
                raise FileNotFoundError(f"LAION sample dataset not found: {LAION_CSV_FILE}")
            
            # Read the LAION CSV
            df = pd.read_csv(laion_file)
            print(f"📊 Loaded LAION dataset with {len(df)} entries")
            
            # Shuffle the dataset for variety
            df = df.sample(frac=1).reset_index(drop=True)
            
            uploaded_count = 0
            attempts = 0
            max_attempts = min(len(df), target * 2)  # Don't exceed available data
            
            while uploaded_count < target and attempts < max_attempts:
                if populate_progress['status'] != 'running':
                    print(f"⏹️ Population stopped at {uploaded_count} images uploaded")
                    break
                
                # Get current row from LAION data
                row = df.iloc[attempts % len(df)]
                attempts += 1
                
                populate_progress['current'] = uploaded_count
                populate_progress['message'] = f'Processing LAION image {attempts} (uploaded: {uploaded_count}/{target})...'
                
                try:
                    url = row['url']
                    caption = row.get('caption', f'LAION Image {attempts}')
                    
                    # Add some randomization to URLs for variety
                    if 'picsum.photos' in url:
                        url = f"https://picsum.photos/800/600?random={random.randint(1, 10000)}"
                    elif 'unsplash.com' in url:
                        # Modify Unsplash URLs to get different images
                        base_url = url.split('?')[0]
                        url = f"{base_url}?w=800&h=600&fit=crop&auto=format&q=80&fm=jpg"
                    
                    print(f"📥 Downloading LAION image {attempts}: {caption[:50]}...")
                    print(f"🔗 URL: {url}")
                    
                    # Download image
                    headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'}
                    response = requests.get(url, headers=headers, timeout=DOWNLOAD_TIMEOUT)
                    print(f"🌐 Response status for LAION image {attempts}: {response.status_code}")
                    
                    if response.status_code == 200:
                        print(f"✅ Successfully downloaded LAION image {attempts}, size: {len(response.content)} bytes")
                        
                        try:
                            print(f"🖼️ Processing LAION image {attempts}...")
                            image = Image.open(io.BytesIO(response.content))
                            if image.mode in ("RGBA", "P"):
                                image = image.convert("RGB")
                            
                            # Resize to standard size
                            image.thumbnail((800, 600), Image.Resampling.LANCZOS)
                            print(f"🔧 Resized LAION image {attempts} to {image.size}")
                            
                            # Convert to base64
                            buffered = io.BytesIO()
                            image.save(buffered, format="JPEG", quality=85)
                            img_base64 = base64.b64encode(buffered.getvalue()).decode('utf-8')
                            print(f"🔄 Converted LAION image {attempts} to base64")
                            
                            # Save to database
                            print(f"💾 Saving LAION image {attempts} to database...")
                            conn = get_db_connection()
                            if conn:
                                uploaded_count += 1
                                filename = f"laion_{uploaded_count:03d}_{row.get('key', str(random.randint(100,999)))}.jpg"
                                
                                populate_progress['message'] = f'Saving LAION image: {caption[:30]}... ({uploaded_count}/{target})'
                                
                                if USE_SQLITE:
                                    cur = conn.cursor()
                                    cur.execute('''
                                        INSERT INTO images (filename, image_data, content_type, description)
                                        VALUES (?, ?, ?, ?)
                                    ''', (filename, img_base64, 'image/jpeg', f"LAION: {caption}"))
                                    print(f"💾 SQLite: Inserted LAION image {attempts} as {filename}")
                                else:
                                    cur = conn.cursor()
                                    img_binary = base64.b64decode(img_base64)
                                    cur.execute('''
                                        INSERT INTO images (filename, image_data, content_type, description)
                                        VALUES (%s, %s, %s, %s)
                                    ''', (filename, img_binary, 'image/jpeg', f"LAION: {caption}"))
                                    print(f"💾 PostgreSQL: Inserted LAION image {attempts} as {filename}")
                                
                                conn.commit()
                                cur.close()
                                conn.close()
                                
                                populate_progress['uploaded'] = uploaded_count
                                populate_progress['current'] = uploaded_count
                                populate_progress['message'] = f'✅ Uploaded LAION: {caption[:30]}... ({uploaded_count}/{target})'
                                print(f"🎉 Successfully saved LAION image {attempts}! Total: {uploaded_count}")
                                
                            else:
                                populate_progress['message'] = f'❌ Database connection failed for LAION image {attempts}'
                                print(f"❌ Database connection failed for LAION image {attempts}")
                                
                        except Exception as e:
                            populate_progress['message'] = f'❌ Failed to process LAION image {attempts}: {str(e)}'
                            print(f"❌ Failed to process LAION image {attempts}: {str(e)}")
                    else:
                        populate_progress['message'] = f'❌ LAION download failed (attempt {attempts}) (HTTP {response.status_code})'
                        print(f"❌ LAION download failed (attempt {attempts}) (HTTP {response.status_code})")
                            
                except Exception as e:
                    populate_progress['message'] = f'❌ Network error for LAION image {attempts}: {str(e)}'
                    print(f"❌ Network error for LAION image {attempts}: {str(e)}")
                
                # Brief delay between requests
                time.sleep(0.5)
            
            populate_progress['status'] = 'completed'
            if uploaded_count >= target:
                populate_progress['message'] = f'🎉 Successfully uploaded {uploaded_count} LAION images in {attempts} attempts!'
                print(f"🏁 LAION population completed! Uploaded {uploaded_count} images in {attempts} attempts")
            else:
                populate_progress['message'] = f'⚠️ Partially completed: {uploaded_count}/{target} LAION images uploaded'
                print(f"⚠️ LAION population stopped: Uploaded {uploaded_count}/{target} images after {attempts} attempts")
            
        except Exception as e:
            populate_progress['status'] = 'error'
            populate_progress['message'] = f'LAION population failed: {str(e)}'
            print(f"💥 LAION population failed with error: {str(e)}")
            
            populate_progress['status'] = 'completed'
            if uploaded_count >= target:
                populate_progress['message'] = f'🎉 Successfully uploaded {uploaded_count} images in {attempts} attempts!'
                print(f"🏁 Population completed successfully! Uploaded {uploaded_count} images in {attempts} attempts")
            else:
                populate_progress['message'] = f'⚠️ Partially completed: {uploaded_count}/{target} images uploaded after {attempts} attempts'
                print(f"⚠️ Population stopped: Uploaded {uploaded_count}/{target} images after {attempts} attempts")
            
        except Exception as e:
            populate_progress['status'] = 'error'
            populate_progress['message'] = f'Population failed: {str(e)}'
            print(f"💥 Population failed with error: {str(e)}")
    
    # Start background thread
    thread = threading.Thread(target=populate_images)
    thread.daemon = True
    thread.start()
    
    return jsonify({'status': 'started', 'target': target})

@app.route('/api/populate/progress')
def get_populate_progress():
    """Get current population progress"""
    return jsonify(populate_progress)

@app.route('/api/populate/stop', methods=['POST'])
def stop_populate():
    """Stop the population process"""
    populate_progress['status'] = 'stopped'
    populate_progress['message'] = 'Population stopped by user'
    return jsonify({'status': 'stopped'})

if __name__ == '__main__':
    # Initialize database
    init_db()
    
    # Get Flask configuration from environment
    debug = os.environ.get('FLASK_DEBUG', 'False').lower() == 'true'
    host = os.environ.get('FLASK_HOST', '0.0.0.0')
    port = int(os.environ.get('FLASK_PORT', 5002))
    
    print(f"🚀 Starting Flask app on {host}:{port} (debug={debug})")
    app.run(debug=debug, host=host, port=port)

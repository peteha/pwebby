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

# Load environment variables
load_dotenv()

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'your-secret-key-here')

# Database configuration - Updated to handle connection issues
DB_CONFIG = {
    'host': 'pgdblin1.pgnet.io',
    'database': 'pgimagedb',
    'user': 'dbadmin',
    'password': 'pgdb##123',
    'port': 5432,
    'sslmode': 'prefer',  # Changed from 'disable' to 'prefer' to allow SSL
    'connect_timeout': 10  # Reduced timeout for faster failure detection
}

# Use SQLite as fallback
USE_SQLITE = False  # Reset to False to try PostgreSQL first
SQLITE_DB = 'images.db'

def get_db_connection():
    """Create database connection with PostgreSQL primary, SQLite fallback"""
    global USE_SQLITE
    
    if not USE_SQLITE:
        try:
            conn = psycopg2.connect(**DB_CONFIG)
            print("Connected to PostgreSQL database")
            return conn
        except Exception as e:
            print(f"PostgreSQL connection failed: {e}")
            print("Falling back to SQLite...")
            USE_SQLITE = True
    
    if USE_SQLITE:
        try:
            conn = sqlite3.connect(SQLITE_DB)
            conn.row_factory = sqlite3.Row  # Enable column access by name
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
                        upload_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    );
                ''')
                
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
                        upload_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    );
                ''')
                
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
    """Validate uploaded image file"""
    if not file or file.filename == '':
        return False, "No file selected"
    
    allowed_extensions = {'jpg', 'jpeg', 'png', 'gif'}
    file_extension = file.filename.rsplit('.', 1)[1].lower() if '.' in file.filename else ''
    
    if file_extension not in allowed_extensions:
        return False, "Invalid file type. Only JPEG, PNG, and GIF files are allowed"
    
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
    """Main page showing images with pagination (8 per page)"""
    per_page = 8
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
                    SELECT id, filename, image_data, content_type, upload_date
                    FROM images 
                    ORDER BY upload_date DESC 
                    LIMIT ? OFFSET ?
                ''', (per_page, offset))
                rows = cur.fetchall()
                for row in rows:
                    # Convert binary data to base64 for display
                    image_base64 = base64.b64encode(row[2]).decode('utf-8')
                    images.append({
                        'id': row[0],
                        'filename': row[1],
                        'data': image_base64,
                        'content_type': row[3],
                        'upload_date': row[4]
                    })
            else:
                cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
                cur.execute('''
                    SELECT id, filename, image_data, content_type, upload_date
                    FROM images 
                    ORDER BY upload_date DESC 
                    LIMIT %s OFFSET %s
                ''', (per_page, offset))
                rows = cur.fetchall()
                for row in rows:
                    # Convert binary data to base64 for display
                    image_base64 = base64.b64encode(row['image_data']).decode('utf-8')
                    images.append({
                        'id': row['id'],
                        'filename': row['filename'],
                        'data': image_base64,
                        'content_type': row['content_type'],
                        'upload_date': row['upload_date']
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

if __name__ == '__main__':
    init_db()
    app.run(debug=True, host='0.0.0.0', port=5001)

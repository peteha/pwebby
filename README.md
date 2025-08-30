# Flask Image Gallery

A modern Flask web application for managing and displaying images with real-time population capabilities.

## Features

✅ **Image Gallery**: Browse images with pagination (8 images per page)  
✅ **Image Upload**: Upload images via web interface  
✅ **Database Storage**: PostgreSQL with SQLite fallback  
✅ **Real-time Population**: Automatically download and upload images from web sources  
✅ **Responsive Design**: Bootstrap-based responsive UI  

## Quick Start

1. **Install Dependencies**
   ```bash
   pip install Flask Pillow python-dotenv psycopg2-binary requests
   ```

2. **Setup Database**
   ```bash
   python setup_database.py
   ```

3. **Run the App**
   ```bash
   python app.py
   ```
   Visit: http://localhost:5001

4. **Populate Gallery** (Optional)
   ```bash
   # Add 100 images from web sources
   python populate_gallery.py --target 100
   
   # Add 50 images with 5 parallel workers
   python populate_gallery.py --target 50 --workers 5
   ```

## Project Structure

```
pwebby/
├── app.py                          # Main Flask application
├── populate_gallery.py             # Live image downloader/uploader
├── requirements.txt                # Python dependencies
├── static/                         # CSS, JS, uploaded images
├── templates/                      # HTML templates
├── .env                           # Environment variables
└── images.db                      # SQLite database (fallback)
```

## Configuration

Create a `.env` file for database configuration:

```env
# PostgreSQL (recommended)
DATABASE_URL=postgresql://username:password@localhost/gallery_db

# SQLite fallback (automatic if PostgreSQL unavailable)
# Uses images.db file
```

## Usage Examples

**Basic gallery population:**
```bash
python populate_gallery.py
```

**Custom target and workers:**
```bash
python populate_gallery.py --target 200 --workers 15
```

**Different Flask URL:**
```bash
python populate_gallery.py --flask-url http://localhost:8000
```

## Image Sources

The gallery populator uses multiple web sources:
- Lorem Picsum (high-quality photos)
- Unsplash Source (professional photos)
- PlaceIMG (categorized images)
- DummyImage (clean placeholders)
- Placeholder.com (colorful placeholders)

## API Endpoints

- `GET /` - Gallery home page
- `GET /page/<int:page>` - Paginated gallery
- `POST /upload` - Upload new image
- `GET /api/images` - JSON API for images
- `DELETE /api/images/<int:image_id>` - Delete image

## Development

The application automatically handles:
- Database connection fallback (PostgreSQL → SQLite)
- Image resizing and optimization
- Error handling and logging
- Responsive pagination
- Real-time image processing

Perfect for portfolios, demos, or any image-centric web application!

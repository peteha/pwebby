# 📸 Image Gallery Web App

A Flask-based web application for managing images stored in a PostgreSQL database. Features a modern Bootstrap UI with Monokai theme, image upload/display functionality, and REST API support.

## ✨ Features

- **Web Interface**: Upload and view images through a responsive web UI
- **Database Storage**: Images stored directly in PostgreSQL database
- **Image Management**: Automatic cleanup (keeps latest 100 images)
- **Multiple Formats**: Supports JPEG, PNG, and GIF images
- **REST API**: Command-line upload support via API
- **Modern UI**: Bootstrap 5 with custom Monokai theme
- **Responsive Design**: Works on desktop and mobile devices

## 🚀 Quick Start

### Prerequisites

- Python 3.9 or higher
- PostgreSQL database access
- Virtual environment (recommended)

### Installation

1. **Clone the repository**
   ```bash
   git clone <your-repo-url>
   cd image-gallery
   ```

2. **Set up virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment**
   ```bash
   # Copy and edit .env file
   cp .env.example .env
   # Edit .env with your database credentials
   ```

5. **Initialize database**
   ```bash
   python init_db.py
   ```

6. **Run the application**
   ```bash
   python app.py
   ```

The application will be available at `http://localhost:5000`

## 🗄️ Database Configuration

The application is pre-configured to connect to:
- **Host**: pgblin1.pgnet.io
- **Database**: dbadmin
- **User**: dbadmin
- **Password**: pgdb##123

To use a different database, update the `DB_CONFIG` in `app.py` or use environment variables.

## 📱 Usage

### Web Interface

1. **Home Page** (`/`): View the latest 5 uploaded images
2. **Upload Page** (`/upload`): Upload new images with drag-and-drop support
3. **Delete Images**: Individual or bulk delete functionality

### API Endpoints

- `GET /`: Main page
- `GET /upload`: Upload page  
- `POST /upload`: Upload via web form
- `POST /api/upload`: Upload via API
- `GET /api/images`: Get images metadata
- `POST /delete/<id>`: Delete specific image
- `POST /delete_all`: Delete all images

### Command Line Upload

Use the included CLI tool to upload images:

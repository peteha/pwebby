# Image Gallery - Deployment Guide

A Flask-based image gallery application with LAION dataset integration and real-time population features.

## Quick Setup

### Option 1: Shell Script (Fastest)
```bash
./setup_host.sh
```
This script will:
- Check system requirements
- Install dependencies
- Set up Python virtual environment
- Create configuration files
- Initialize database
- Create startup scripts

### Option 2: Python Script (More Features)
```bash
python prepare_host.py
```
This provides more detailed setup with better error handling.

### Option 3: Manual Setup
```bash
# 1. Create virtual environment
python3 -m venv .venv
source .venv/bin/activate

# 2. Install requirements
pip install -r requirements.txt

# 3. Copy environment template
cp .env.example .env

# 4. Initialize database
python db_manager.py

# 5. Start application
python app.py
```

## Configuration

Edit `.env` file with your settings:

```bash
# Basic settings
SECRET_KEY=your-secret-key-here
FLASK_PORT=5002
DATABASE_TYPE=sqlite  # or postgresql

# For PostgreSQL
POSTGRES_HOST=localhost
POSTGRES_DATABASE=imagedb
POSTGRES_USER=username
POSTGRES_PASSWORD=password
```

## Running the Application

### Development
```bash
./start-dev.sh
# or
source .venv/bin/activate && python app.py
```

### Production
```bash
./start.sh
# or install as systemd service (Linux)
sudo cp image-gallery.service /etc/systemd/system/
sudo systemctl enable image-gallery
sudo systemctl start image-gallery
```

## Features

- **Image Gallery**: View uploaded images with descriptions
- **Real-time Population**: Populate gallery from LAION dataset with progress bar
- **Upload Interface**: Manual image upload with preview
- **Database Management**: SQLite or PostgreSQL support
- **Responsive Design**: Bootstrap-based UI with dark theme

## API Endpoints

- `GET /` - Main gallery page
- `GET /upload` - Upload page
- `POST /api/populate` - Start gallery population
- `GET /api/populate/progress` - Get population progress
- `POST /api/populate/stop` - Stop population

## Database Scripts

- `db_manager.py` - Full database management
- `init_db.py` - Database initialization
- `quick_init_db.py` - Quick setup

## Requirements

- Python 3.8+
- Flask 2.3+
- PostgreSQL (optional) or SQLite
- System packages for image processing (installed by setup scripts)

## Ports

Default application port: **5002**

Access at: http://localhost:5002

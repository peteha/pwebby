# 🖼️ ### **1. Docker Deployment (Recommended) 🐳**
**Simplest and most reliable deployment method**

```bash
# Quick validation
./validate_docker.sh

# Simple deployment (SQLite)
./docker.sh simple

# Full deployment with internal PostgreSQL + Redis
./docker.sh up

# External PostgreSQL deployment
./setup_external_db.sh  # Setup external database
./docker.sh external    # Start with external PostgreSQL

# Access at: http://localhost:5002
``` Complete Deployment Guide

A modern Flask-based image gallery application with LAION dataset integration, real-time population features, and multiple deployment options.

## 🚀 Quick Start Options

### 1. Docker Deployment (Recommended) 🐳
**Simplest and most reliable deployment method**

```bash
# Quick validation
./validate_docker.sh

# Simple deployment (SQLite)
./docker.sh simple

# Full deployment (PostgreSQL + Redis)
./docker.sh up

# Access at: http://localhost:5002
```

### 2. Host Setup Scripts 🖥️
**For native installation on your server**

```bash
# Shell script (fastest)
./setup_host.sh

# Python script (more robust)
python prepare_host.py

# Manual setup
source .venv/bin/activate && python app.py
```

### 3. Manual Development Setup 👩‍💻
**For development and customization**

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
python init_db.py
python app.py
```

## 📋 Deployment Comparison

| Method | Setup Time | Complexity | Best For | Dependencies |
|--------|------------|------------|----------|--------------|
| **Docker Simple** | 2 minutes | ⭐ Easy | Quick demo, development | Docker only |
| **Docker External DB** | 5 minutes | ⭐⭐ Medium | Production with existing PostgreSQL | Docker + PostgreSQL |
| **Docker Full** | 3 minutes | ⭐⭐ Medium | Complete isolated stack | Docker + Compose |
| **Host Scripts** | 5 minutes | ⭐⭐ Medium | Dedicated servers | Python 3.8+ |
| **Manual Setup** | 10 minutes | ⭐⭐⭐ Advanced | Development, customization | System packages |

## 🐳 Docker Deployment (Recommended)

### Prerequisites
- Docker Engine 20.10+
- Docker Compose 2.0+
- 2GB available disk space

### Quick Commands
```bash
./docker.sh simple      # SQLite (no external DB)
./docker.sh up          # Internal PostgreSQL + Redis
./docker.sh external    # External PostgreSQL (setup first)
./docker.sh down        # Stop all services
./docker.sh clean       # Remove all containers/images
./docker.sh logs        # View application logs
```

### External PostgreSQL Setup
```bash
# Setup external database (one-time)
./setup_external_db.sh

# Start with external database
./docker.sh external
```

### Configuration
```bash
# For internal PostgreSQL
cp .env.docker .env

# For external PostgreSQL  
cp .env.external-db .env

# Edit with your settings
nano .env
```

## 🖥️ Native Host Deployment

### Prerequisites
- Python 3.8+
- System packages for image processing
- PostgreSQL (optional)

### Setup Scripts
```bash
# Option 1: Shell script
./setup_host.sh

# Option 2: Python script  
python prepare_host.py

# Both create:
# - Virtual environment
# - Configuration files
# - Database initialization
# - Startup scripts
```

### Manual Commands
```bash
# After setup, start the app
./start.sh              # Production mode
./start-dev.sh          # Development mode

# Or direct Python
source .venv/bin/activate
python app.py
```

## 🔧 Configuration Options

### Database Types
- **SQLite**: File-based, zero-config, perfect for development
- **PostgreSQL (Internal)**: Docker-managed PostgreSQL, isolated stack
- **PostgreSQL (External)**: Use existing PostgreSQL server, production-ready

### Environment Variables (.env)
```bash
# Flask Configuration
SECRET_KEY=your-very-secure-random-secret-key
FLASK_DEBUG=false
FLASK_HOST=0.0.0.0
FLASK_PORT=5002

# Database Configuration
DATABASE_TYPE=sqlite          # or postgresql

# PostgreSQL (Internal - for docker-compose.yml)
POSTGRES_HOST=postgres        # Docker internal hostname
POSTGRES_DATABASE=imagedb
POSTGRES_USER=gallery_user
POSTGRES_PASSWORD=secure_password

# PostgreSQL (External - for docker-compose.external-db.yml)
POSTGRES_HOST=localhost       # or your PostgreSQL server IP
# Use host.docker.internal on macOS/Windows Docker Desktop
POSTGRES_DATABASE=imagedb
POSTGRES_USER=gallery_user  
POSTGRES_PASSWORD=secure_password
POSTGRES_PORT=5432

# SQLite (if using SQLite)
SQLITE_DATABASE=images.db     # or /app/data/images.db for Docker

# Application Settings
MAX_UPLOAD_SIZE=16777216      # 16MB
ALLOWED_EXTENSIONS=jpg,jpeg,png,gif
DEFAULT_PAGINATION=8
MAX_IMAGES=100

# LAION Dataset
LAION_CSV_FILE=laion_sample.csv
MAX_WORKERS=8
DOWNLOAD_TIMEOUT=15
```

## 🌟 Features

### Core Features
- **📸 Image Gallery**: Responsive grid layout with pagination
- **⬆️ Upload Interface**: Drag-and-drop image upload with preview
- **🤖 Auto-Population**: Populate gallery from LAION dataset with progress tracking
- **📱 Mobile Responsive**: Works perfectly on all screen sizes
- **🌙 Dark Theme**: Modern Monokai-inspired design

### Technical Features
- **🚀 Real-time Progress**: Live progress bar during image population
- **🔄 Parallel Processing**: Multi-threaded image downloading
- **💾 Flexible Storage**: SQLite or PostgreSQL database options
- **🐳 Docker Ready**: Complete containerization with health checks
- **🔒 Secure**: Environment-based configuration, no hardcoded secrets
- **📊 API Endpoints**: RESTful API for integration

## 📊 API Reference

### Gallery Endpoints
- `GET /` - Main gallery page
- `GET /page/<int:page>` - Gallery with pagination
- `GET /upload` - Upload page

### API Endpoints
- `POST /api/upload` - Upload image via API
- `GET /api/images` - Get all images metadata
- `POST /api/populate` - Start gallery population
- `GET /api/populate/progress` - Get population progress
- `POST /api/populate/stop` - Stop population process

### Example API Usage
```bash
# Upload an image
curl -X POST -F "file=@image.jpg" http://localhost:5002/api/upload

# Start populating 50 images
curl -X POST -H "Content-Type: application/json" 
     -d '{"target": 50}' 
     http://localhost:5002/api/populate

# Check progress
curl http://localhost:5002/api/populate/progress
```

## 🛠️ Management Commands

### Database Management
```bash
# Initialize database
python db_manager.py init

# Check database status
python db_manager.py status

# Reset database
python db_manager.py reset

# Quick initialization
python quick_init_db.py
```

### Docker Management
```bash
# View running containers
docker-compose ps

# Access application container
docker exec -it image-gallery-app bash

# View real-time logs
docker-compose logs -f app

# Backup SQLite database (simple mode)
docker cp image-gallery-app-simple:/app/data/images.db backup.db

# Backup PostgreSQL (full mode)
docker exec image-gallery-postgres pg_dump -U gallery_user imagedb > backup.sql
```

## 🚨 Troubleshooting

### Common Issues

#### Port Already in Use
```bash
# Find what's using port 5002
lsof -i :5002

# Or use different port
export FLASK_PORT=5003
```

#### Database Connection Issues
```bash
# Check database status
python db_manager.py status

# Reinitialize database
python db_manager.py reset
python db_manager.py init
```

#### Docker Issues
```bash
# Check Docker status
docker info

# Restart Docker service
sudo systemctl restart docker

# Clean up Docker resources
./docker.sh clean
```

#### Permission Issues
```bash
# Fix file permissions
chmod +x *.sh
chown -R $USER:$USER .

# Docker volume permissions
docker exec -it image-gallery-app chown -R app:app /app/data
```

### Debug Mode
```bash
# Enable debug logging
echo "FLASK_DEBUG=true" >> .env

# Restart application
./docker.sh down && ./docker.sh up
# Or for native: ./start-dev.sh
```

## 📁 Project Structure

```
pwebby/
├── 🐳 Docker Files
│   ├── Dockerfile                 # Application container
│   ├── docker-compose.yml        # Internal PostgreSQL deployment
│   ├── docker-compose.simple.yml # Simple deployment (SQLite)
│   ├── docker-compose.external-db.yml # External PostgreSQL deployment
│   ├── .dockerignore             # Docker ignore patterns
│   └── init_db.sql               # PostgreSQL initialization
│
├── 🚀 Deployment Scripts
│   ├── docker.sh                 # Docker management script
│   ├── setup_host.sh             # Shell host setup
│   ├── prepare_host.py           # Python host setup
│   ├── setup_external_db.sh      # External PostgreSQL setup
│   ├── validate_docker.sh        # Docker validation
│   ├── start.sh                  # Production startup
│   └── start-dev.sh              # Development startup
│
├── 🗄️ Database Scripts
│   ├── db_manager.py             # Database management utility
│   ├── init_db.py                # Database initialization
│   └── quick_init_db.py          # Quick database setup
│
├── 🌐 Application Files
│   ├── app.py                    # Main Flask application
│   ├── requirements.txt          # Python dependencies
│   ├── laion_sample.csv          # LAION dataset sample
│   └── templates/                # HTML templates
│       ├── base.html
│       ├── index.html
│       └── upload.html
│
├── ⚙️ Configuration
│   ├── .env.example              # Environment template
│   ├── .env.docker              # Internal PostgreSQL template
│   ├── .env.external-db         # External PostgreSQL template
│   └── app_configuration.txt     # Legacy config
│
└── 📚 Documentation
    ├── README.md                 # This file
    ├── DOCKER.md                 # Detailed Docker guide
    ├── DEPLOYMENT.md             # Deployment guide
    ├── DATABASE_SCRIPTS.md       # Database documentation
    └── ENVIRONMENT_CONFIG.md     # Environment configuration
```

## 🔄 Updates and Maintenance

### Application Updates
```bash
# Native deployment
git pull
source .venv/bin/activate
pip install -r requirements.txt
./start.sh

# Docker deployment
git pull
./docker.sh down
./docker.sh build
./docker.sh up
```

### Database Backups
```bash
# SQLite backup
cp images.db images_backup_$(date +%Y%m%d).db

# PostgreSQL backup
pg_dump -h localhost -U gallery_user imagedb > backup_$(date +%Y%m%d).sql

# Docker PostgreSQL backup
docker exec image-gallery-postgres pg_dump -U gallery_user imagedb > backup.sql
```

## 🌐 Production Deployment

### Reverse Proxy (Nginx)
```nginx
server {
    listen 80;
    server_name yourdomain.com;
    
    location / {
        proxy_pass http://localhost:5002;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

### Systemd Service
```bash
# Copy service file
sudo cp image-gallery.service /etc/systemd/system/

# Enable and start
sudo systemctl enable image-gallery
sudo systemctl start image-gallery
```

### Environment Security
- Use strong passwords and secret keys
- Don't commit `.env` files to version control
- Use HTTPS in production
- Regular security updates

## 📈 Performance Tips

### Image Optimization
- Images are automatically resized and compressed
- Base64 encoding for database storage
- Thumbnail generation for gallery view

### Database Performance
- Automatic pagination (8 images per page)
- Database indexes on upload_date
- Connection pooling in production

### Docker Performance
- Health checks for service monitoring
- Resource limits in production
- Volume mounts for persistent data

## 🆘 Support

1. **Check Documentation**: Review the appropriate guide above
2. **Validate Setup**: Run `./validate_docker.sh` for Docker issues
3. **Check Logs**: Use `./docker.sh logs` or `python app.py` output
4. **Database Status**: Run `python db_manager.py status`
5. **Clean Install**: Try `./docker.sh clean` then `./docker.sh up`

## 📄 License

This project is open source. See the project repository for license details.

---

🎉 **Ready to deploy?** Start with `./docker.sh simple` for the quickest setup!

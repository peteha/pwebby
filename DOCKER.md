# Docker Deployment Guide

Complete Docker deployment guide for the Image Gallery application with both simple (SQLite) and full (PostgreSQL) deployment options.

## 🚀 Quick Start

### Option 1: One-Click Simple Deployment (SQLite)
```bash
./docker.sh simple
```
- Uses SQLite database (no external dependencies)
- Perfect for development and small deployments
- Starts immediately

### Option 2: Full Production Deployment (PostgreSQL)
```bash
./docker.sh up
```
- Uses PostgreSQL database
- Includes Redis for session storage
- Production-ready with health checks

## 📋 Prerequisites

- Docker Engine 20.10+
- Docker Compose 2.0+
- 2GB available disk space
- Ports 5002, 5433, 6379 available

## 🐳 Docker Images and Services

### Application Stack (Full Deployment)
- **app**: Image Gallery Flask application
- **postgres**: PostgreSQL 15 database
- **redis**: Redis 7 for session storage (optional)

### Simple Deployment
- **app**: Image Gallery Flask application with SQLite

## 🔧 Configuration

### Environment Variables (.env)
```bash
# Flask Configuration
SECRET_KEY=your-very-secure-random-secret-key-here
FLASK_DEBUG=false

# Database Configuration
DATABASE_TYPE=postgresql  # or sqlite for simple mode

# PostgreSQL Configuration (Full deployment)
POSTGRES_DATABASE=imagedb
POSTGRES_USER=gallery_user
POSTGRES_PASSWORD=secure_password_change_this

# Application Settings
MAX_UPLOAD_SIZE=16777216
ALLOWED_EXTENSIONS=jpg,jpeg,png,gif
DEFAULT_PAGINATION=8
MAX_IMAGES=100
MAX_WORKERS=8
DOWNLOAD_TIMEOUT=15
```

### Docker Compose Profiles

#### Full Deployment (docker-compose.yml)
```yaml
services:
  app:          # Flask application
  postgres:     # PostgreSQL database
  redis:        # Redis cache
```

#### Simple Deployment (docker-compose.simple.yml)
```yaml
services:
  app:          # Flask application with SQLite
```

## 📁 Volume Mounts

### Full Deployment
- `postgres_data`: PostgreSQL data persistence
- `uploads`: Image upload storage
- `./laion_sample.csv`: LAION dataset sample

### Simple Deployment
- `app_data`: SQLite database and application data
- `uploads`: Image upload storage
- `./laion_sample.csv`: LAION dataset sample

## 🌐 Network Configuration

### Ports
- **5002**: Image Gallery web interface
- **5433**: PostgreSQL database (external access)
- **6379**: Redis (optional)

### Internal Network
- `image-gallery-network`: Full deployment
- `image-gallery-simple-network`: Simple deployment

## 🛠️ Docker Commands

### Build and Deploy
```bash
# Build image only
./docker.sh build

# Start full deployment (PostgreSQL)
./docker.sh up

# Start simple deployment (SQLite)
./docker.sh simple

# Stop all services
./docker.sh down

# Clean up everything
./docker.sh clean
```

### Management Commands
```bash
# View application logs
./docker.sh logs

# Check service status
docker-compose ps

# Access application container
docker exec -it image-gallery-app bash

# Access PostgreSQL
docker exec -it image-gallery-postgres psql -U gallery_user -d imagedb
```

### Database Operations
```bash
# Initialize database manually
docker exec -it image-gallery-app python db_manager.py

# Reset database
docker exec -it image-gallery-app python db_manager.py reset

# Check database status
docker exec -it image-gallery-app python db_manager.py status
```

## 🏥 Health Checks

### Application Health Check
- **Endpoint**: `http://localhost:5002/`
- **Interval**: 30 seconds
- **Timeout**: 10 seconds
- **Retries**: 3

### PostgreSQL Health Check
- **Command**: `pg_isready`
- **Interval**: 10 seconds
- **Timeout**: 5 seconds
- **Retries**: 5

### Redis Health Check
- **Command**: `redis-cli ping`
- **Interval**: 10 seconds
- **Timeout**: 5 seconds
- **Retries**: 3

## 🔐 Security Considerations

### Environment Security
- Change default passwords in `.env`
- Use strong secret keys
- Don't commit `.env` to version control

### Container Security
- Runs as non-root user (`app`)
- Minimal base image (Python slim)
- No unnecessary packages installed

### Network Security
- Internal network isolation
- Exposed ports only as needed
- Health checks for service monitoring

## 📊 Monitoring and Logs

### Application Logs
```bash
# Real-time logs
docker-compose logs -f app

# All services logs
docker-compose logs -f

# Specific service logs
docker-compose logs postgres
```

### Container Statistics
```bash
# Resource usage
docker stats

# Container inspection
docker inspect image-gallery-app
```

## 🚨 Troubleshooting

### Common Issues

#### Port Conflicts
```bash
# Check port usage
lsof -i :5002
netstat -tulpn | grep 5002

# Use different ports
# Edit docker-compose.yml ports section
```

#### Database Connection Issues
```bash
# Check PostgreSQL logs
docker-compose logs postgres

# Test database connection
docker exec -it image-gallery-app python -c "
from app import get_db_connection
conn = get_db_connection()
print('Connection:', 'OK' if conn else 'Failed')
"
```

#### Permission Issues
```bash
# Fix volume permissions
docker exec -it image-gallery-app chown -R app:app /app/data
docker exec -it image-gallery-app chmod 755 /app/static/uploads
```

#### Memory Issues
```bash
# Monitor memory usage
docker stats --no-stream

# Increase Docker memory limit in Docker Desktop
# Or add memory limits to docker-compose.yml
```

### Debug Mode

#### Enable Debug Logging
```bash
# Edit .env
FLASK_DEBUG=true

# Restart containers
./docker.sh down
./docker.sh up
```

#### Access Container Shell
```bash
# Application container
docker exec -it image-gallery-app bash

# PostgreSQL container
docker exec -it image-gallery-postgres bash

# Check application files
docker exec -it image-gallery-app ls -la /app/
```

## 🔄 Updates and Maintenance

### Application Updates
```bash
# Pull latest code
git pull

# Rebuild and restart
./docker.sh down
./docker.sh build
./docker.sh up
```

### Database Backups
```bash
# PostgreSQL backup
docker exec image-gallery-postgres pg_dump -U gallery_user imagedb > backup.sql

# SQLite backup (simple mode)
docker cp image-gallery-app-simple:/app/data/images.db ./images_backup.db
```

### Database Restoration
```bash
# PostgreSQL restore
docker exec -i image-gallery-postgres psql -U gallery_user imagedb < backup.sql

# SQLite restore (simple mode)
docker cp ./images_backup.db image-gallery-app-simple:/app/data/images.db
```

## 🌟 Production Deployment

### Docker Swarm
```bash
# Initialize swarm
docker swarm init

# Deploy stack
docker stack deploy -c docker-compose.yml image-gallery
```

### Kubernetes
```bash
# Generate Kubernetes manifests
docker-compose config > k8s-manifests.yml

# Apply to cluster
kubectl apply -f k8s-manifests.yml
```

### Environment-Specific Configurations

#### Staging
```bash
# Use staging environment file
cp .env.staging .env
./docker.sh up
```

#### Production
```bash
# Use production environment file
cp .env.production .env

# Deploy with production compose file
docker-compose -f docker-compose.prod.yml up -d
```

## 📈 Performance Tuning

### Resource Limits
```yaml
# Add to docker-compose.yml
services:
  app:
    deploy:
      resources:
        limits:
          cpus: '2'
          memory: 2G
        reservations:
          cpus: '0.5'
          memory: 512M
```

### Database Optimization
```yaml
# PostgreSQL optimization
postgres:
  environment:
    - POSTGRES_SHARED_BUFFERS=256MB
    - POSTGRES_EFFECTIVE_CACHE_SIZE=1GB
```

## 📚 Additional Resources

- [Docker Documentation](https://docs.docker.com/)
- [Docker Compose Documentation](https://docs.docker.com/compose/)
- [Flask Docker Deployment](https://flask.palletsprojects.com/en/2.3.x/deploying/docker/)
- [PostgreSQL Docker Image](https://hub.docker.com/_/postgres)

## 🆘 Support

For issues and questions:
1. Check the troubleshooting section above
2. Review Docker and application logs
3. Verify environment configuration
4. Check system resources and port availability

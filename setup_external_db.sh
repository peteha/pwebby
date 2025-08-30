#!/bin/bash
# External PostgreSQL Setup Script for Image Gallery

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

print_step() {
    echo -e "\n${BLUE}📋 $1...${NC}"
}

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

echo "🗄️ External PostgreSQL Setup for Image Gallery"
echo "=============================================="

# Load environment variables if .env exists
if [[ -f ".env" ]]; then
    source .env
fi

# Default values
DB_HOST="${POSTGRES_HOST:-localhost}"
DB_PORT="${POSTGRES_PORT:-5432}"
DB_NAME="${POSTGRES_DATABASE:-imagedb}"
DB_USER="${POSTGRES_USER:-gallery_user}"
DB_PASS="${POSTGRES_PASSWORD:-gallery_password}"

echo "Database Configuration:"
echo "  Host: $DB_HOST"
echo "  Port: $DB_PORT"
echo "  Database: $DB_NAME"
echo "  User: $DB_USER"
echo ""

# Function to test PostgreSQL connection
test_connection() {
    local host=$1
    local port=$2
    local user=$3
    local password=$4
    local database=$5
    
    PGPASSWORD="$password" psql -h "$host" -p "$port" -U "$user" -d "$database" -c "SELECT 1;" > /dev/null 2>&1
}

# Function to create database and user
create_database() {
    print_step "Creating database and user"
    
    # Connect as postgres user to create database and user
    echo "Please provide PostgreSQL admin credentials:"
    read -p "Admin username (default: postgres): " admin_user
    admin_user=${admin_user:-postgres}
    read -s -p "Admin password: " admin_pass
    echo ""
    
    # Create database
    print_step "Creating database '$DB_NAME'"
    PGPASSWORD="$admin_pass" psql -h "$DB_HOST" -p "$DB_PORT" -U "$admin_user" -d postgres -c "
        CREATE DATABASE $DB_NAME;
    " 2>/dev/null || print_warning "Database might already exist"
    
    # Create user
    print_step "Creating user '$DB_USER'"
    PGPASSWORD="$admin_pass" psql -h "$DB_HOST" -p "$DB_PORT" -U "$admin_user" -d postgres -c "
        CREATE USER $DB_USER WITH PASSWORD '$DB_PASS';
        GRANT ALL PRIVILEGES ON DATABASE $DB_NAME TO $DB_USER;
        ALTER USER $DB_USER CREATEDB;
    " 2>/dev/null || print_warning "User might already exist"
    
    print_success "Database and user setup completed"
}

# Function to initialize schema
initialize_schema() {
    print_step "Initializing database schema"
    
    # Create the images table
    PGPASSWORD="$DB_PASS" psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d "$DB_NAME" -c "
        CREATE TABLE IF NOT EXISTS images (
            id SERIAL PRIMARY KEY,
            filename VARCHAR(255) NOT NULL,
            image_data BYTEA NOT NULL,
            content_type VARCHAR(50) NOT NULL,
            description TEXT,
            upload_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );

        CREATE INDEX IF NOT EXISTS idx_images_filename ON images(filename);
        CREATE INDEX IF NOT EXISTS idx_images_upload_date ON images(upload_date DESC);
    "
    
    print_success "Database schema initialized"
}

# Check if PostgreSQL client is installed
if ! command -v psql &> /dev/null; then
    print_error "PostgreSQL client (psql) is not installed"
    echo ""
    echo "Install PostgreSQL client:"
    echo "  Ubuntu/Debian: sudo apt-get install postgresql-client"
    echo "  CentOS/RHEL:   sudo yum install postgresql"
    echo "  macOS:         brew install postgresql"
    echo ""
    exit 1
fi

print_success "PostgreSQL client found"

# Check if PostgreSQL server is accessible
print_step "Testing PostgreSQL server connection"
if nc -z "$DB_HOST" "$DB_PORT" 2>/dev/null; then
    print_success "PostgreSQL server is accessible at $DB_HOST:$DB_PORT"
else
    print_error "Cannot connect to PostgreSQL server at $DB_HOST:$DB_PORT"
    echo ""
    echo "Please ensure:"
    echo "1. PostgreSQL server is running"
    echo "2. Server is accessible from this host"
    echo "3. Firewall allows connections on port $DB_PORT"
    echo "4. PostgreSQL is configured to accept connections"
    echo ""
    exit 1
fi

# Test if database and user already exist
if test_connection "$DB_HOST" "$DB_PORT" "$DB_USER" "$DB_PASS" "$DB_NAME"; then
    print_success "Database connection successful"
    
    # Check if tables exist
    table_count=$(PGPASSWORD="$DB_PASS" psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d "$DB_NAME" -t -c "
        SELECT COUNT(*) FROM information_schema.tables 
        WHERE table_schema = 'public' AND table_name = 'images';
    " | tr -d ' ')
    
    if [[ "$table_count" -eq "1" ]]; then
        print_success "Database schema already exists"
        
        # Show image count
        image_count=$(PGPASSWORD="$DB_PASS" psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d "$DB_NAME" -t -c "
            SELECT COUNT(*) FROM images;
        " | tr -d ' ')
        
        echo "📊 Current images in database: $image_count"
    else
        initialize_schema
    fi
else
    print_warning "Database connection failed - need to create database and user"
    create_database
    initialize_schema
fi

# Create/update .env file for external database
print_step "Updating environment configuration"
if [[ -f ".env.external-db" ]]; then
    cp .env.external-db .env
else
    cat > .env << EOF
# Flask Configuration
SECRET_KEY=$(openssl rand -hex 32)
FLASK_DEBUG=false

# Database Configuration (External PostgreSQL)
DATABASE_TYPE=postgresql

# External PostgreSQL Configuration
POSTGRES_HOST=$DB_HOST
POSTGRES_DATABASE=$DB_NAME
POSTGRES_USER=$DB_USER
POSTGRES_PASSWORD=$DB_PASS
POSTGRES_PORT=$DB_PORT
POSTGRES_SSLMODE=prefer
POSTGRES_CONNECT_TIMEOUT=10

# Application Settings
MAX_UPLOAD_SIZE=16777216
ALLOWED_EXTENSIONS=jpg,jpeg,png,gif
DEFAULT_PAGINATION=8
MAX_IMAGES=100

# LAION Dataset Configuration
MAX_WORKERS=8
DOWNLOAD_TIMEOUT=15
EOF
fi

print_success "Environment configuration updated"

echo ""
echo "=============================================="
echo "🎉 External PostgreSQL Setup Complete!"
echo "=============================================="
echo ""
echo "📋 Database Information:"
echo "  Host:     $DB_HOST:$DB_PORT"
echo "  Database: $DB_NAME"
echo "  User:     $DB_USER"
echo ""
echo "📋 Next Steps:"
echo "1. Start the Docker application:"
echo "   ./docker.sh external"
echo ""
echo "2. Access your Image Gallery:"
echo "   http://localhost:5002"
echo ""
echo "3. Check application logs:"
echo "   docker-compose -f docker-compose.external-db.yml logs -f app"
echo ""

print_success "Ready to use external PostgreSQL database!"

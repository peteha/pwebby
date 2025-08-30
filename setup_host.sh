#!/bin/bash
# Quick Host Setup Script for Image Gallery Application
# Simple bash version for rapid deployment

set -e  # Exit on any error

echo "🚀 Quick Host Setup for Image Gallery"
echo "====================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Helper functions
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

# Check if we're in the right directory
if [[ ! -f "app.py" ]]; then
    print_error "app.py not found. Please run this script from the project directory."
    exit 1
fi

PROJECT_DIR=$(pwd)
print_success "Project directory: $PROJECT_DIR"

# 1. Check Python version
print_step "Checking Python version"
PYTHON_VERSION=$(python3 --version 2>&1 | cut -d' ' -f2 | cut -d'.' -f1-2)
PYTHON_MAJOR=$(echo $PYTHON_VERSION | cut -d'.' -f1)
PYTHON_MINOR=$(echo $PYTHON_VERSION | cut -d'.' -f2)

if [[ $PYTHON_MAJOR -eq 3 && $PYTHON_MINOR -ge 8 ]]; then
    print_success "Python $PYTHON_VERSION is compatible"
else
    print_error "Python 3.8+ required, found $PYTHON_VERSION"
    exit 1
fi

# 2. Install system dependencies (Ubuntu/Debian)
print_step "Installing system dependencies"
if command -v apt-get &> /dev/null; then
    sudo apt-get update -qq
    sudo apt-get install -y \
        python3-venv \
        python3-pip \
        python3-dev \
        libpq-dev \
        libjpeg-dev \
        libpng-dev \
        zlib1g-dev \
        > /dev/null 2>&1
    print_success "System dependencies installed (Ubuntu/Debian)"
elif command -v yum &> /dev/null; then
    sudo yum install -y \
        python3-venv \
        python3-pip \
        python3-devel \
        postgresql-devel \
        libjpeg-devel \
        libpng-devel \
        zlib-devel \
        > /dev/null 2>&1
    print_success "System dependencies installed (CentOS/RHEL)"
elif [[ "$OSTYPE" == "darwin"* ]]; then
    print_warning "macOS detected - assuming dependencies available via Homebrew"
else
    print_warning "Unknown system - you may need to install dependencies manually"
fi

# 3. Create virtual environment
print_step "Creating virtual environment"
if [[ ! -d ".venv" ]]; then
    python3 -m venv .venv
    print_success "Virtual environment created"
else
    print_success "Virtual environment already exists"
fi

# 4. Activate virtual environment and install requirements
print_step "Installing Python requirements"
source .venv/bin/activate

# Upgrade pip
pip install --upgrade pip > /dev/null 2>&1

# Create requirements.txt if it doesn't exist
if [[ ! -f "requirements.txt" ]]; then
    print_warning "requirements.txt not found, creating basic version"
    cat > requirements.txt << 'EOF'
Flask>=2.3.0
psycopg2-binary>=2.9.0
Pillow>=9.0.0
python-dotenv>=1.0.0
requests>=2.31.0
pandas>=2.0.0
img2dataset>=1.40.0
webdataset>=0.2.0
EOF
fi

pip install -r requirements.txt
print_success "Python requirements installed"

# 5. Set up environment file
print_step "Setting up environment configuration"
if [[ ! -f ".env" ]]; then
    if [[ -f ".env.example" ]]; then
        cp .env.example .env
        print_success "Created .env from .env.example"
    else
        cat > .env << 'EOF'
# Flask Configuration
SECRET_KEY=change-this-to-a-random-secret-key
FLASK_DEBUG=True
FLASK_HOST=0.0.0.0
FLASK_PORT=5002

# Database Configuration
DATABASE_TYPE=sqlite

# PostgreSQL Configuration (if using PostgreSQL)
POSTGRES_HOST=localhost
POSTGRES_DATABASE=imagedb
POSTGRES_USER=your-username
POSTGRES_PASSWORD=your-password
POSTGRES_PORT=5432
POSTGRES_SSLMODE=prefer
POSTGRES_CONNECT_TIMEOUT=10

# SQLite Configuration
SQLITE_DATABASE=images.db

# Application Settings
MAX_UPLOAD_SIZE=16777216
ALLOWED_EXTENSIONS=jpg,jpeg,png,gif
DEFAULT_PAGINATION=8
MAX_IMAGES=100

# LAION Dataset Configuration
LAION_CSV_FILE=laion_sample.csv
MAX_WORKERS=8
DOWNLOAD_TIMEOUT=15
EOF
        print_success "Created basic .env file"
    fi
    print_warning "IMPORTANT: Edit .env file with your actual configuration!"
else
    print_success "Environment file already exists"
fi

# 6. Initialize database
print_step "Initializing database"
if [[ -f "db_manager.py" ]]; then
    python db_manager.py > /dev/null 2>&1 && print_success "Database initialized" || print_warning "Database init had issues (may need .env configuration)"
elif [[ -f "quick_init_db.py" ]]; then
    python quick_init_db.py > /dev/null 2>&1 && print_success "Database initialized" || print_warning "Database init had issues (may need .env configuration)"
else
    print_warning "No database initialization script found"
fi

# 7. Create startup scripts
print_step "Creating startup scripts"

# Start script
cat > start.sh << EOF
#!/bin/bash
cd "$PROJECT_DIR"
source .venv/bin/activate
python app.py
EOF
chmod +x start.sh

# Development start script
cat > start-dev.sh << EOF
#!/bin/bash
cd "$PROJECT_DIR"
source .venv/bin/activate
export FLASK_DEBUG=True
python app.py
EOF
chmod +x start-dev.sh

print_success "Created startup scripts (start.sh, start-dev.sh)"

# 8. Create systemd service (Linux only)
if [[ "$OSTYPE" == "linux-gnu"* ]]; then
    print_step "Creating systemd service"
    cat > image-gallery.service << EOF
[Unit]
Description=Image Gallery Web Application
After=network.target

[Service]
Type=simple
User=$USER
WorkingDirectory=$PROJECT_DIR
Environment=PATH=$PROJECT_DIR/.venv/bin
ExecStart=$PROJECT_DIR/.venv/bin/python app.py
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
EOF
    
    print_success "Created systemd service file"
    echo "To install service:"
    echo "  sudo cp image-gallery.service /etc/systemd/system/"
    echo "  sudo systemctl enable image-gallery"
    echo "  sudo systemctl start image-gallery"
fi

# Summary
echo ""
echo "====================================="
echo "🎉 Setup Complete!"
echo "====================================="
echo ""
echo "📋 Next Steps:"
echo "1. Edit configuration:    nano .env"
echo "2. Start application:     ./start.sh"
echo "3. Development mode:      ./start-dev.sh"
echo "4. Access at:            http://localhost:5002"
echo ""
echo "📁 Important files created:"
echo "  .env              - Configuration"
echo "  .venv/            - Python environment"
echo "  start.sh          - Production start"
echo "  start-dev.sh      - Development start"
if [[ "$OSTYPE" == "linux-gnu"* ]]; then
echo "  image-gallery.service - Systemd service"
fi
echo ""
print_success "Host is ready for Image Gallery application!"

deactivate 2>/dev/null || true

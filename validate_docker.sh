#!/bin/bash
# Docker Setup Validation Script

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

echo "🔍 Docker Setup Validation"
echo "=========================="

# Check required files
required_files=(
    "Dockerfile"
    "docker-compose.yml" 
    "docker-compose.simple.yml"
    "docker-compose.external-db.yml"
    ".dockerignore"
    "init_db.sql"
    ".env.docker"
    ".env.external-db"
    "docker.sh"
    "setup_external_db.sh"
    "app.py"
    "requirements.txt"
)

print_step "Checking required Docker files"
all_files_present=true

for file in "${required_files[@]}"; do
    if [[ -f "$file" ]]; then
        echo "  ✅ $file"
    else
        echo "  ❌ $file (missing)"
        all_files_present=false
    fi
done

if $all_files_present; then
    print_success "All required Docker files are present"
else
    print_error "Some required files are missing"
    exit 1
fi

# Check Dockerfile syntax
print_step "Validating Dockerfile syntax"
if command -v docker &> /dev/null; then
    if docker build --dry-run . &> /dev/null; then
        print_success "Dockerfile syntax is valid"
    else
        print_error "Dockerfile has syntax errors"
        exit 1
    fi
else
    print_warning "Docker not installed - cannot validate Dockerfile syntax"
fi

# Check docker-compose.yml syntax
print_step "Validating docker-compose files"
if command -v docker-compose &> /dev/null; then
    if docker-compose config &> /dev/null; then
        print_success "docker-compose.yml is valid"
    else
        print_error "docker-compose.yml has errors"
        exit 1
    fi
    
    if docker-compose -f docker-compose.simple.yml config &> /dev/null; then
        print_success "docker-compose.simple.yml is valid"
    else
        print_error "docker-compose.simple.yml has errors"
        exit 1
    fi
    
    if docker-compose -f docker-compose.external-db.yml config &> /dev/null; then
        print_success "docker-compose.external-db.yml is valid"
    else
        print_error "docker-compose.external-db.yml has errors"
        exit 1
    fi
else
    print_warning "docker-compose not installed - cannot validate compose files"
fi

# Check environment file template
print_step "Checking environment configuration"
if [[ -f ".env.docker" ]]; then
    required_vars=("SECRET_KEY" "DATABASE_TYPE" "POSTGRES_DATABASE" "POSTGRES_USER" "POSTGRES_PASSWORD")
    for var in "${required_vars[@]}"; do
        if grep -q "^${var}=" .env.docker; then
            echo "  ✅ $var"
        else
            echo "  ❌ $var (missing from .env.docker)"
        fi
    done
    print_success "Environment template checked"
else
    print_error ".env.docker template missing"
fi

# Check Python requirements
print_step "Validating requirements.txt"
if [[ -f "requirements.txt" ]]; then
    required_packages=("Flask" "psycopg2-binary" "Pillow" "python-dotenv" "requests" "pandas")
    for package in "${required_packages[@]}"; do
        if grep -q "^${package}" requirements.txt; then
            echo "  ✅ $package"
        else
            echo "  ❌ $package (missing from requirements.txt)"
        fi
    done
    print_success "Requirements validated"
else
    print_error "requirements.txt missing"
fi

# Check if LAION sample exists or can be created
print_step "Checking LAION dataset sample"
if [[ -f "laion_sample.csv" ]]; then
    print_success "LAION sample dataset exists"
else
    print_warning "LAION sample will be created on first run"
fi

# Check executable permissions
print_step "Checking script permissions"
if [[ -x "docker.sh" ]]; then
    print_success "docker.sh is executable"
else
    print_warning "docker.sh needs execute permission (run: chmod +x docker.sh)"
fi

if [[ -x "setup_external_db.sh" ]]; then
    print_success "setup_external_db.sh is executable"
else
    print_warning "setup_external_db.sh needs execute permission (run: chmod +x setup_external_db.sh)"
fi

# Summary
echo ""
echo "=========================="
echo "🎯 Validation Summary"
echo "=========================="
echo ""

if command -v docker &> /dev/null; then
    print_success "Docker is installed"
else
    print_warning "Docker needs to be installed"
    echo "  Install from: https://docs.docker.com/get-docker/"
fi

if command -v docker-compose &> /dev/null; then
    print_success "Docker Compose is installed"
else
    print_warning "Docker Compose needs to be installed"
    echo "  Install from: https://docs.docker.com/compose/install/"
fi

echo ""
echo "📋 Next Steps:"
echo ""

if ! command -v docker &> /dev/null; then
    echo "1. Install Docker Desktop"
    echo "2. Start Docker"
    echo "3. Run: ./docker.sh simple    # For SQLite deployment"
    echo "   Or: ./docker.sh up        # For PostgreSQL deployment"
else
    echo "1. Copy environment: cp .env.docker .env    # For internal PostgreSQL"
    echo "   Or: cp .env.external-db .env             # For external PostgreSQL"
    echo "2. Edit .env with your settings"
    echo "3. Run: ./docker.sh simple      # For SQLite deployment"
    echo "   Or: ./docker.sh up           # For internal PostgreSQL deployment"  
    echo "   Or: ./setup_external_db.sh && ./docker.sh external  # For external PostgreSQL"
fi

echo ""
echo "🌐 After deployment, access at: http://localhost:5002"
echo ""

print_success "Docker setup validation complete!"

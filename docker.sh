#!/bin/bash
# Docker build and run script for Image Gallery

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

echo "🐳 Image Gallery Docker Setup"
echo "============================="

# Check if Docker is installed and running
if ! command -v docker &> /dev/null; then
    print_error "Docker is not installed. Please install Docker first."
    exit 1
fi

if ! docker info &> /dev/null; then
    print_error "Docker daemon is not running. Please start Docker."
    exit 1
fi

print_success "Docker is available"

# Check if we have the required files
if [[ ! -f "Dockerfile" ]]; then
    print_error "Dockerfile not found. Please run this from the project directory."
    exit 1
fi

if [[ ! -f "docker-compose.yml" ]]; then
    print_error "docker-compose.yml not found."
    exit 1
fi

# Create .env file if it doesn't exist
if [[ ! -f ".env" ]]; then
    print_step "Creating environment file"
    if [[ -f ".env.docker" ]]; then
        cp .env.docker .env
        print_success "Created .env from .env.docker template"
    else
        cat > .env << 'EOF'
SECRET_KEY=your-very-secure-random-secret-key-here
FLASK_DEBUG=false
DATABASE_TYPE=postgresql
POSTGRES_DATABASE=imagedb
POSTGRES_USER=gallery_user
POSTGRES_PASSWORD=secure_password_change_this
MAX_UPLOAD_SIZE=16777216
ALLOWED_EXTENSIONS=jpg,jpeg,png,gif
DEFAULT_PAGINATION=8
MAX_IMAGES=100
MAX_WORKERS=8
DOWNLOAD_TIMEOUT=15
EOF
        print_success "Created basic .env file"
    fi
    print_warning "Please edit .env file with your secure passwords!"
fi

# Create LAION sample if it doesn't exist
if [[ ! -f "laion_sample.csv" ]]; then
    print_step "Creating LAION sample dataset"
    cat > laion_sample.csv << 'EOF'
url,caption,key
https://picsum.photos/800/600?random=1,Beautiful landscape photography,001
https://picsum.photos/800/600?random=2,Urban architecture,002
https://picsum.photos/800/600?random=3,Nature scene,003
https://picsum.photos/800/600?random=4,Abstract art,004
https://picsum.photos/800/600?random=5,Portrait photography,005
https://picsum.photos/800/600?random=6,Street photography,006
https://picsum.photos/800/600?random=7,Minimalist design,007
https://picsum.photos/800/600?random=8,Vintage style,008
https://picsum.photos/800/600?random=9,Modern composition,009
https://picsum.photos/800/600?random=10,Creative perspective,010
EOF
    print_success "Created LAION sample dataset"
fi

# Function to show usage
show_usage() {
    echo ""
    echo "Usage: $0 [OPTION]"
    echo ""
    echo "Options:"
    echo "  build      Build the Docker image only"
    echo "  up         Start with internal PostgreSQL (full setup)"
    echo "  external   Start with external PostgreSQL database"
    echo "  simple     Start with SQLite (simple setup)"
    echo "  down       Stop all containers"
    echo "  clean      Remove containers and images"
    echo "  logs       Show application logs"
    echo "  help       Show this help message"
    echo ""
}

# Parse command line argument
case "${1:-up}" in
    build)
        print_step "Building Docker image"
        docker build -t image-gallery .
        print_success "Docker image built successfully"
        ;;
    
    up)
        print_step "Starting Image Gallery with PostgreSQL"
        docker-compose up -d
        print_success "Application started with PostgreSQL"
        print_step "Waiting for services to be ready"
        sleep 10
        
        if docker-compose ps | grep -q "Up"; then
            print_success "Services are running"
            echo ""
            echo "🌐 Access your Image Gallery at: http://localhost:5002"
            echo "🗄️  PostgreSQL is available at: localhost:5433"
            echo ""
            echo "📋 Useful commands:"
            echo "  docker-compose logs -f app       # View app logs"
            echo "  docker-compose ps               # Check status"
            echo "  docker-compose down             # Stop services"
        else
            print_error "Some services failed to start. Check logs:"
            docker-compose logs
        fi
        ;;
    
    external)
        print_step "Starting Image Gallery with External PostgreSQL"
        if [[ ! -f ".env" ]]; then
            if [[ -f ".env.external-db" ]]; then
                cp .env.external-db .env
                print_success "Created .env from external database template"
            else
                print_error ".env file not found. Please create one with external database settings."
                exit 1
            fi
        fi
        docker-compose -f docker-compose.external-db.yml up -d
        print_success "Application started with external PostgreSQL"
        
        print_step "Waiting for service to be ready"
        sleep 10
        
        if docker-compose -f docker-compose.external-db.yml ps | grep -q "Up"; then
            print_success "Service is running"
            echo ""
            echo "🌐 Access your Image Gallery at: http://localhost:5002"
            echo "🗄️  Using external PostgreSQL database"
            echo ""
            print_warning "Make sure your external PostgreSQL is running and accessible"
            echo ""
            echo "📋 Useful commands:"
            echo "  docker-compose -f docker-compose.external-db.yml logs -f app  # View logs"
            echo "  docker-compose -f docker-compose.external-db.yml down        # Stop service"
        else
            print_error "Service failed to start. Check logs:"
            docker-compose -f docker-compose.external-db.yml logs
        fi
        ;;
        
    simple)
        print_step "Starting Image Gallery with SQLite (simple mode)"
        # Update environment for SQLite
        sed -i.bak 's/DATABASE_TYPE=postgresql/DATABASE_TYPE=sqlite/' .env
        docker-compose -f docker-compose.simple.yml up -d
        print_success "Application started with SQLite"
        
        print_step "Waiting for service to be ready"
        sleep 5
        
        if docker-compose -f docker-compose.simple.yml ps | grep -q "Up"; then
            print_success "Service is running"
            echo ""
            echo "🌐 Access your Image Gallery at: http://localhost:5002"
            echo ""
            echo "📋 Useful commands:"
            echo "  docker-compose -f docker-compose.simple.yml logs -f app  # View logs"
            echo "  docker-compose -f docker-compose.simple.yml down        # Stop service"
        else
            print_error "Service failed to start. Check logs:"
            docker-compose -f docker-compose.simple.yml logs
        fi
        ;;
        
    down)
        print_step "Stopping all services"
        docker-compose down 2>/dev/null || true
        docker-compose -f docker-compose.simple.yml down 2>/dev/null || true
        docker-compose -f docker-compose.external-db.yml down 2>/dev/null || true
        print_success "All services stopped"
        ;;
        
    clean)
        print_step "Cleaning up Docker resources"
        docker-compose down --rmi all --volumes --remove-orphans 2>/dev/null || true
        docker-compose -f docker-compose.simple.yml down --rmi all --volumes --remove-orphans 2>/dev/null || true
        docker-compose -f docker-compose.external-db.yml down --rmi all --volumes --remove-orphans 2>/dev/null || true
        docker rmi image-gallery 2>/dev/null || true
        print_success "Docker resources cleaned up"
        ;;
        
    logs)
        print_step "Showing application logs"
        if docker-compose ps | grep -q "Up"; then
            docker-compose logs -f app
        elif docker-compose -f docker-compose.simple.yml ps | grep -q "Up"; then
            docker-compose -f docker-compose.simple.yml logs -f app
        elif docker-compose -f docker-compose.external-db.yml ps | grep -q "Up"; then
            docker-compose -f docker-compose.external-db.yml logs -f app
        else
            print_warning "No running services found"
        fi
        ;;
        
    help|--help|-h)
        show_usage
        ;;
        
    *)
        print_error "Unknown option: $1"
        show_usage
        exit 1
        ;;
esac

#!/bin/bash

# Image Gallery Deployment Script
echo "🚀 Starting Image Gallery deployment..."

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is required but not installed."
    exit 1
fi

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Install/upgrade pip
echo "⬆️ Upgrading pip..."
pip install --upgrade pip

# Install requirements
echo "📥 Installing dependencies..."
pip install -r requirements.txt

# Check if .env exists
if [ ! -f ".env" ]; then
    echo "⚠️ Warning: .env file not found. Using default configuration."
    echo "🔧 Creating .env from template..."
    cat > .env << EOF
SECRET_KEY=change-this-secret-key-in-production
FLASK_ENV=production
FLASK_DEBUG=False

DB_HOST=pgblin1.pgnet.io
DB_NAME=dbadmin
DB_USER=dbadmin
DB_PASSWORD=pgdb##123

MAX_IMAGES=100
EOF
fi

# Initialize database
echo "🗄️ Initializing database..."
python init_db.py

if [ $? -eq 0 ]; then
    echo "✅ Database initialized successfully!"
else
    echo "❌ Database initialization failed!"
    exit 1
fi

echo ""
echo "🎉 Deployment complete!"
echo ""
echo "To start the application:"
echo "  source venv/bin/activate"
echo "  python app.py"
echo ""
echo "Or use Gunicorn for production:"
echo "  pip install gunicorn"
echo "  gunicorn --bind 0.0.0.0:5000 app:app"
echo ""
echo "📱 Access your app at: http://localhost:5000"

#!/usr/bin/env python3
"""
Host Preparation Script for Image Gallery Application
Prepares a new host with all requirements and configurations
"""

import os
import sys
import subprocess
import platform
import shutil
from pathlib import Path

class HostPreparation:
    def __init__(self):
        self.script_dir = Path(__file__).parent.absolute()
        self.venv_path = self.script_dir / '.venv'
        self.requirements_file = self.script_dir / 'requirements.txt'
        self.env_file = self.script_dir / '.env'
        self.env_example = self.script_dir / '.env.example'
        
        # System info
        self.system = platform.system()
        self.python_version = sys.version_info
        
        print(f"🖥️  System: {self.system}")
        print(f"🐍 Python: {self.python_version.major}.{self.python_version.minor}.{self.python_version.micro}")
        print(f"📁 Project directory: {self.script_dir}")

    def check_python_version(self):
        """Check if Python version is compatible"""
        print("\n🔍 Checking Python version...")
        
        if self.python_version < (3, 8):
            print(f"❌ Python 3.8+ required, found {self.python_version.major}.{self.python_version.minor}")
            return False
        else:
            print(f"✅ Python {self.python_version.major}.{self.python_version.minor} is compatible")
            return True

    def check_system_dependencies(self):
        """Check and install system dependencies"""
        print("\n🔍 Checking system dependencies...")
        
        if self.system == "Linux":
            return self._check_linux_dependencies()
        elif self.system == "Darwin":  # macOS
            return self._check_macos_dependencies()
        elif self.system == "Windows":
            return self._check_windows_dependencies()
        else:
            print(f"⚠️  Unknown system: {self.system}")
            return True

    def _check_linux_dependencies(self):
        """Check Linux system dependencies"""
        dependencies = [
            ('python3-venv', 'Python virtual environment support'),
            ('python3-pip', 'Python package installer'),
            ('python3-dev', 'Python development headers'),
            ('libpq-dev', 'PostgreSQL development headers'),
            ('libjpeg-dev', 'JPEG library for Pillow'),
            ('libpng-dev', 'PNG library for Pillow'),
            ('zlib1g-dev', 'Compression library'),
        ]
        
        missing = []
        for package, description in dependencies:
            if not self._command_exists(f"dpkg -l | grep {package}"):
                missing.append((package, description))
        
        if missing:
            print("📦 Missing system packages:")
            for pkg, desc in missing:
                print(f"   - {pkg}: {desc}")
            
            print("\n🚀 Install with:")
            packages = ' '.join([pkg for pkg, _ in missing])
            print(f"   sudo apt-get update && sudo apt-get install -y {packages}")
            
            return False
        else:
            print("✅ All system dependencies are installed")
            return True

    def _check_macos_dependencies(self):
        """Check macOS system dependencies"""
        print("✅ macOS: Most dependencies should be available")
        
        # Check for Homebrew
        if not self._command_exists('brew --version'):
            print("⚠️  Homebrew not found. Install from: https://brew.sh")
            print("   Some packages may need manual installation")
        else:
            print("✅ Homebrew is available")
        
        return True

    def _check_windows_dependencies(self):
        """Check Windows system dependencies"""
        print("✅ Windows: Python dependencies will be installed via pip")
        print("⚠️  For PostgreSQL support, ensure PostgreSQL client libraries are installed")
        return True

    def _command_exists(self, command):
        """Check if a command exists"""
        try:
            subprocess.run(command, shell=True, capture_output=True, check=True)
            return True
        except subprocess.CalledProcessError:
            return False

    def create_virtual_environment(self):
        """Create Python virtual environment"""
        print("\n🐍 Setting up Python virtual environment...")
        
        if self.venv_path.exists():
            print(f"✅ Virtual environment already exists at {self.venv_path}")
            return True
        
        try:
            subprocess.run([sys.executable, '-m', 'venv', str(self.venv_path)], 
                          check=True, capture_output=True)
            print(f"✅ Virtual environment created at {self.venv_path}")
            return True
        except subprocess.CalledProcessError as e:
            print(f"❌ Failed to create virtual environment: {e}")
            return False

    def install_python_requirements(self):
        """Install Python requirements"""
        print("\n📦 Installing Python requirements...")
        
        # Determine pip path
        if self.system == "Windows":
            pip_path = self.venv_path / 'Scripts' / 'pip'
        else:
            pip_path = self.venv_path / 'bin' / 'pip'
        
        if not pip_path.exists():
            print(f"❌ pip not found at {pip_path}")
            return False
        
        # Check if requirements.txt exists
        if not self.requirements_file.exists():
            print("⚠️  requirements.txt not found. Creating basic requirements...")
            self._create_requirements_file()
        
        try:
            # Upgrade pip first
            subprocess.run([str(pip_path), 'install', '--upgrade', 'pip'], 
                          check=True, capture_output=True)
            print("✅ pip upgraded")
            
            # Install requirements
            subprocess.run([str(pip_path), 'install', '-r', str(self.requirements_file)], 
                          check=True, capture_output=False)
            print("✅ Python requirements installed")
            return True
            
        except subprocess.CalledProcessError as e:
            print(f"❌ Failed to install requirements: {e}")
            return False

    def _create_requirements_file(self):
        """Create basic requirements.txt if it doesn't exist"""
        requirements = [
            "Flask>=2.3.0",
            "psycopg2-binary>=2.9.0",
            "Pillow>=9.0.0",
            "python-dotenv>=1.0.0",
            "requests>=2.31.0",
            "pandas>=2.0.0",
            "img2dataset>=1.40.0",
            "webdataset>=0.2.0"
        ]
        
        with open(self.requirements_file, 'w') as f:
            f.write('\n'.join(requirements) + '\n')
        
        print(f"📝 Created {self.requirements_file}")

    def setup_environment_file(self):
        """Set up environment configuration"""
        print("\n🔧 Setting up environment configuration...")
        
        if self.env_file.exists():
            print(f"✅ Environment file already exists: {self.env_file}")
            return True
        
        if self.env_example.exists():
            # Copy from example
            shutil.copy2(self.env_example, self.env_file)
            print(f"✅ Created .env from .env.example")
        else:
            # Create basic .env file
            self._create_basic_env_file()
            print(f"✅ Created basic .env file")
        
        print("⚠️  IMPORTANT: Edit .env file with your actual configuration!")
        print(f"   nano {self.env_file}")
        return True

    def _create_basic_env_file(self):
        """Create basic .env file"""
        env_content = """# Flask Configuration
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
"""
        
        with open(self.env_file, 'w') as f:
            f.write(env_content)

    def initialize_database(self):
        """Initialize the database"""
        print("\n🗄️  Initializing database...")
        
        # Determine python path in venv
        if self.system == "Windows":
            python_path = self.venv_path / 'Scripts' / 'python'
        else:
            python_path = self.venv_path / 'bin' / 'python'
        
        # Check if database initialization scripts exist
        db_scripts = ['db_manager.py', 'quick_init_db.py', 'init_db.py']
        available_script = None
        
        for script in db_scripts:
            script_path = self.script_dir / script
            if script_path.exists():
                available_script = script_path
                break
        
        if not available_script:
            print("⚠️  No database initialization script found")
            print("   You'll need to initialize the database manually")
            return True
        
        try:
            subprocess.run([str(python_path), str(available_script)], 
                          check=True, capture_output=False, cwd=str(self.script_dir))
            print("✅ Database initialized successfully")
            return True
        except subprocess.CalledProcessError as e:
            print(f"⚠️  Database initialization failed: {e}")
            print("   You may need to configure database settings in .env first")
            return True  # Don't fail the entire setup for this

    def create_startup_scripts(self):
        """Create convenient startup scripts"""
        print("\n📜 Creating startup scripts...")
        
        # Create start script
        if self.system == "Windows":
            start_script = self.script_dir / 'start.bat'
            start_content = f"""@echo off
cd /d "{self.script_dir}"
.venv\\Scripts\\python app.py
pause
"""
        else:
            start_script = self.script_dir / 'start.sh'
            start_content = f"""#!/bin/bash
cd "{self.script_dir}"
source .venv/bin/activate
python app.py
"""
        
        with open(start_script, 'w') as f:
            f.write(start_content)
        
        if self.system != "Windows":
            os.chmod(start_script, 0o755)
        
        print(f"✅ Created startup script: {start_script}")
        
        # Create development script
        if self.system == "Windows":
            dev_script = self.script_dir / 'start-dev.bat'
            dev_content = f"""@echo off
cd /d "{self.script_dir}"
set FLASK_DEBUG=True
.venv\\Scripts\\python app.py
pause
"""
        else:
            dev_script = self.script_dir / 'start-dev.sh'
            dev_content = f"""#!/bin/bash
cd "{self.script_dir}"
source .venv/bin/activate
export FLASK_DEBUG=True
python app.py
"""
        
        with open(dev_script, 'w') as f:
            f.write(dev_content)
        
        if self.system != "Windows":
            os.chmod(dev_script, 0o755)
        
        print(f"✅ Created development script: {dev_script}")
        return True

    def create_systemd_service(self):
        """Create systemd service file for Linux"""
        if self.system != "Linux":
            return True
        
        print("\n🔧 Creating systemd service...")
        
        service_content = f"""[Unit]
Description=Image Gallery Web Application
After=network.target

[Service]
Type=simple
User=$USER
WorkingDirectory={self.script_dir}
Environment=PATH={self.venv_path}/bin
ExecStart={self.venv_path}/bin/python app.py
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
"""
        
        service_file = self.script_dir / 'image-gallery.service'
        with open(service_file, 'w') as f:
            f.write(service_content)
        
        print(f"✅ Created systemd service file: {service_file}")
        print("   To install:")
        print(f"     sudo cp {service_file} /etc/systemd/system/")
        print("     sudo systemctl enable image-gallery")
        print("     sudo systemctl start image-gallery")
        
        return True

    def run_setup(self):
        """Run the complete setup process"""
        print("🚀 Starting Host Preparation for Image Gallery Application")
        print("=" * 60)
        
        steps = [
            ("Checking Python version", self.check_python_version),
            ("Checking system dependencies", self.check_system_dependencies),
            ("Creating virtual environment", self.create_virtual_environment),
            ("Installing Python requirements", self.install_python_requirements),
            ("Setting up environment file", self.setup_environment_file),
            ("Initializing database", self.initialize_database),
            ("Creating startup scripts", self.create_startup_scripts),
            ("Creating systemd service", self.create_systemd_service),
        ]
        
        failed_steps = []
        
        for step_name, step_function in steps:
            print(f"\n{'='*20}")
            print(f"📋 {step_name}...")
            if not step_function():
                failed_steps.append(step_name)
                print(f"❌ {step_name} failed")
            else:
                print(f"✅ {step_name} completed")
        
        print("\n" + "=" * 60)
        print("🏁 Host Preparation Summary")
        print("=" * 60)
        
        if failed_steps:
            print(f"⚠️  {len(failed_steps)} step(s) had issues:")
            for step in failed_steps:
                print(f"   - {step}")
            print("\nSome manual intervention may be required.")
        else:
            print("🎉 All steps completed successfully!")
        
        print(f"\n📋 Next Steps:")
        print(f"1. Edit configuration: nano {self.env_file}")
        print(f"2. Start application: ./start.sh (or start.bat on Windows)")
        print(f"3. Access at: http://localhost:5002")
        
        return len(failed_steps) == 0

def main():
    """Main function"""
    if len(sys.argv) > 1 and sys.argv[1] in ['--help', '-h']:
        print("""
Host Preparation Script for Image Gallery Application

This script prepares a new host with all requirements:
- Python virtual environment
- Required packages
- Environment configuration
- Database initialization
- Startup scripts
- System service (Linux)

Usage:
    python prepare_host.py    # Run full setup
    python prepare_host.py -h # Show this help
        """)
        return
    
    try:
        preparer = HostPreparation()
        success = preparer.run_setup()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n⚠️  Setup interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n💥 Unexpected error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()

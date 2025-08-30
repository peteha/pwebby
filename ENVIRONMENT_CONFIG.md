# Environment Configuration

This application is now fully configured to use environment variables for all sensitive data and configuration settings.

## 🔒 **Security Implementation**

### **Environment Variables Only**
- ✅ No hardcoded passwords or database credentials in code
- ✅ All configuration via `.env` file
- ✅ `.env` file excluded from version control
- ✅ `.env.example` provided for reference

## 📋 **Configuration Options**

### **Flask Settings**
```bash
SECRET_KEY=your-super-secret-key-change-this-in-production
FLASK_DEBUG=True
FLASK_HOST=0.0.0.0
FLASK_PORT=5002
```

### **Database Settings**
```bash
# Choose 'postgresql' or 'sqlite'
DATABASE_TYPE=postgresql

# PostgreSQL Configuration
POSTGRES_HOST=your-postgres-host
POSTGRES_DATABASE=your-database-name
POSTGRES_USER=your-username
POSTGRES_PASSWORD=your-password
POSTGRES_PORT=5432
POSTGRES_SSLMODE=prefer
POSTGRES_CONNECT_TIMEOUT=10

# SQLite Configuration (fallback)
SQLITE_DATABASE=images.db
```

### **Application Settings**
```bash
MAX_UPLOAD_SIZE=16777216        # 16MB in bytes
ALLOWED_EXTENSIONS=jpg,jpeg,png,gif
DEFAULT_PAGINATION=8
MAX_IMAGES=100
```

### **LAION Dataset Settings**
```bash
LAION_CSV_FILE=laion_sample.csv
MAX_WORKERS=8
DOWNLOAD_TIMEOUT=15
```

## 🚀 **Setup Instructions**

1. **Copy the example environment file:**
   ```bash
   cp .env.example .env
   ```

2. **Edit `.env` with your actual values:**
   ```bash
   nano .env
   ```

3. **Update database credentials, secret keys, etc.**

4. **Start the application:**
   ```bash
   python app.py
   ```

## 🛡️ **Security Best Practices Implemented**

- **No secrets in code:** All sensitive data in environment variables
- **Version control safety:** `.env` excluded from Git
- **Configurable environments:** Easy to switch between dev/staging/prod
- **Fallback options:** SQLite fallback if PostgreSQL unavailable
- **Type validation:** Environment values properly cast to correct types

## 🔧 **Environment Switching**

### **Development:**
```bash
DATABASE_TYPE=sqlite
FLASK_DEBUG=True
```

### **Production:**
```bash
DATABASE_TYPE=postgresql
FLASK_DEBUG=False
SECRET_KEY=<strong-random-key>
```

Your application is now properly secured with environment-based configuration! 🎉

# Database Management Scripts

This directory contains several database management utilities for the image gallery application.

## 📋 **Available Scripts**

### 1. **`init_db.py`** - Comprehensive Initialization
```bash
python init_db.py
```
- **Full featured initialization script**
- Creates database if it doesn't exist
- Sets up all tables with proper schema
- Displays detailed progress and table structure
- Handles both PostgreSQL and SQLite

### 2. **`quick_init_db.py`** - Quick Setup
```bash
python quick_init_db.py
```
- **Fast and simple setup**
- Minimal output, just gets the job done
- Perfect for scripts and automation
- Creates database and tables in one step

### 3. **`db_manager.py`** - Full Management Suite
```bash
# Default: Full initialization
python db_manager.py

# Show database status
python db_manager.py status

# Create database only (no tables)
python db_manager.py create

# Full initialization (database + tables)
python db_manager.py init

# Reset database (WARNING: deletes all data)
python db_manager.py reset
```

## 🚀 **Quick Start**

### **New Installation:**
```bash
# Option 1: Use the comprehensive script
python init_db.py

# Option 2: Use the quick script  
python quick_init_db.py

# Option 3: Use the manager (default action)
python db_manager.py
```

### **Check Status:**
```bash
python db_manager.py status
```

### **Reset Database (if needed):**
```bash
python db_manager.py reset
```

## ⚙️ **Configuration**

All scripts read from your `.env` file:

```bash
# Database type
DATABASE_TYPE=postgresql  # or 'sqlite'

# PostgreSQL settings
POSTGRES_HOST=your-host
POSTGRES_DATABASE=your-db-name
POSTGRES_USER=your-username
POSTGRES_PASSWORD=your-password

# SQLite settings  
SQLITE_DATABASE=images.db
```

## 🔧 **Features**

- ✅ **Auto-detects database type** from environment
- ✅ **Creates database if missing** (PostgreSQL)
- ✅ **Sets up complete schema** with indexes
- ✅ **Handles existing databases** gracefully
- ✅ **Migration support** (adds missing columns)
- ✅ **Status checking** and diagnostics
- ✅ **Safe reset functionality** with confirmation

## 📊 **Database Schema**

All scripts create this table structure:

```sql
CREATE TABLE images (
    id SERIAL PRIMARY KEY,              -- Auto-incrementing ID
    filename VARCHAR(255) NOT NULL,     -- Original filename
    image_data BYTEA NOT NULL,          -- Image binary data
    content_type VARCHAR(50) NOT NULL,  -- MIME type
    description TEXT,                   -- LAION caption
    upload_date TIMESTAMP DEFAULT NOW() -- Upload timestamp
);

CREATE INDEX idx_images_upload_date ON images (upload_date DESC);
```

## 🛡️ **Safety Features**

- **No destructive operations** without confirmation
- **Graceful error handling** with clear messages
- **Environment-based configuration** (no hardcoded values)
- **Transaction safety** for PostgreSQL operations
- **Fallback support** (PostgreSQL → SQLite)

Choose the script that best fits your needs! 🎯

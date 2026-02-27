# 🚀 Project Synergy: Oracle to DB2 Takeout Engine

**Enterprise Migration Command Center** - A comprehensive tool for migrating Oracle databases to IBM DB2 with automated schema conversion, data migration, and ROI analysis.

![IBM](https://img.shields.io/badge/IBM-DB2-blue)
![Python](https://img.shields.io/badge/Python-3.8+-green)
![React](https://img.shields.io/badge/React-19+-blue)
![FastAPI](https://img.shields.io/badge/FastAPI-0.133+-teal)
![Vite](https://img.shields.io/badge/Vite-7.3+-purple)
![TailwindCSS](https://img.shields.io/badge/TailwindCSS-3.4+-cyan)

## 📋 Table of Contents

- [Features](#features)
- [Architecture](#architecture)
- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Running the Application](#running-the-application)
- [Usage Guide](#usage-guide)
- [API Documentation](#api-documentation)
- [Project Structure](#project-structure)
- [Configuration](#configuration)
- [Testing](#testing)
- [Troubleshooting](#troubleshooting)

## ✨ Features

### 🔄 **Automated Schema Conversion**
- Converts Oracle SQL DDL to DB2-compatible SQL
- Handles 28+ Oracle data types with intelligent mapping
- Preserves constraints, indexes, and foreign keys
- Generates side-by-side comparison views

### 📊 **Data Migration Engine**
- JSON-driven migration configuration
- 13 built-in data transformations
- 9 validation types for data integrity
- Real-time migration progress tracking
- Comprehensive verification reports

### 💰 **Oracle Takeout ROI Calculator**
- Real industry benchmarks (Oracle vs DB2 costs)
- Interactive database size slider (10-1000 GB)
- Detailed cost breakdowns:
  - Licensing costs
  - Support fees
  - Storage costs (with DB2 compression)
  - DBA labor costs
- 5-year financial projections
- ROI payback period calculation

### 🎨 **Modern Web Interface**
- Built with React 18 + Vite
- IBM Carbon Design System
- Real-time updates with hot module reload
- Responsive design for all devices

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    React Frontend                        │
│              (Port 3000 - Vite Dev Server)              │
│  • Source Ingestion  • SQL Diff Viewer                  │
│  • Migration & Data Audit  • TCO Calculator             │
└────────────────────┬────────────────────────────────────┘
                     │ HTTP/REST API
┌────────────────────▼────────────────────────────────────┐
│                  FastAPI Backend                         │
│               (Port 8000 - Uvicorn)                     │
│  • /api/process-raw-sql  • /api/run-full-migration     │
│  • /api/get-tco-analysis • /api/health                  │
└────────────────────┬────────────────────────────────────┘
                     │
┌────────────────────▼────────────────────────────────────┐
│              Migration Engine                            │
│  • Schema Converter  • Data Mapper                      │
│  • Validation Engine • Statistics Tracker               │
└─────────────────────────────────────────────────────────┘
```

## 📦 Prerequisites

### Required Software

1. **Python 3.8+**
   ```bash
   python --version  # Should be 3.8 or higher
   ```

2. **Node.js 18+** and **npm**
   ```bash
   node --version  # Should be 18 or higher
   npm --version
   ```

3. **IBM DB2 Client** (Optional - for actual database connections)
   - Download from [IBM DB2 Downloads](https://www.ibm.com/products/db2/downloads)

### System Requirements
- **OS:** macOS, Linux, or Windows
- **RAM:** 4GB minimum, 8GB recommended
- **Disk Space:** 500MB for dependencies

## 🚀 Installation

### 1. Clone the Repository

```bash
git clone <repository-url>
cd "Product Synergy"
```

### 2. Backend Setup

```bash
# Create Python virtual environment
python3 -m venv venv

# Activate virtual environment
# On macOS/Linux:
source venv/bin/activate
# On Windows:
# venv\Scripts\activate

# Install Python dependencies
pip install -r requirements.txt
```

### 3. Frontend Setup

```bash
# Navigate to frontend directory
cd frontend

# Install Node.js dependencies
npm install

# Return to project root
cd ..
```

## 🎯 Running the Application

### Option 1: Run Both Services (Recommended)

Open **two separate terminals**:

**Terminal 1 - Backend:**
```bash
cd "Product Synergy"
source venv/bin/activate
uvicorn api.main:app --reload --host 0.0.0.0 --port 8000
```

**Terminal 2 - Frontend:**
```bash
cd "Product Synergy/frontend"
npm run dev
```

### Option 2: Quick Start Script

```bash
# Make script executable (first time only)
chmod +x start.sh

# Run both services
./start.sh
```

### Access the Application

- **Frontend:** http://localhost:3000
- **Backend API:** http://localhost:8000
- **API Docs:** http://localhost:8000/docs

## 📖 Usage Guide

### 1. Source Ingestion

1. Navigate to **Source Ingestion** tab
2. Upload your Oracle SQL file (DDL statements)
3. System automatically:
   - Detects tables and columns
   - Analyzes data types
   - Generates DB2-compatible SQL

### 2. SQL Diff Viewer

1. View side-by-side comparison:
   - **Left:** Original Oracle SQL
   - **Right:** Converted DB2 SQL
2. Toggle **"Highlight Differences"** to see:
   - Oracle-specific types (red)
   - DB2 replacement types (green)

### 3. Migration & Data Audit

1. Click **"🚀 Run Full Migration"** button
2. System performs:
   - Schema creation
   - Mock data generation
   - Data migration with transformations
   - Integrity verification
3. View results table with:
   - Records migrated per table
   - Transformations applied
   - Validations passed
   - Green "VERIFIED" badges

### 4. TCO Calculator

1. Adjust **Database Size** slider (10-1000 GB)
2. View real-time calculations:
   - Annual cost comparison
   - Savings percentage
   - ROI payback period
3. Explore detailed breakdowns:
   - Oracle costs (license, support, storage, labor)
   - DB2 costs (with compression benefits)
   - 5-year financial projection

## 🔌 API Documentation

### Health Check
```bash
GET /api/health
```

### Process Oracle SQL
```bash
POST /api/process-raw-sql
Content-Type: multipart/form-data

file: <oracle_sql_file>
```

### Run Full Migration
```bash
POST /api/run-full-migration?mapping_file=table_mappings.json
```

### Get TCO Analysis
```bash
GET /api/get-tco-analysis?table_count=7&column_count=100&database_size_gb=100
```

**Interactive API Documentation:** http://localhost:8000/docs

## 📁 Project Structure

```
Product Synergy/
├── api/
│   └── main.py                 # FastAPI backend server
├── database/
│   ├── migrations/
│   │   ├── table_mappings.json # Migration configuration
│   │   └── type_mappings_reference.json
│   └── schemas/
│       ├── oracle_source_schema.sql
│       └── db2_target_schema.sql
├── frontend/
│   ├── src/
│   │   ├── App.jsx            # Main React application
│   │   └── index.css          # Tailwind CSS styles
│   ├── package.json
│   └── vite.config.js
├── scripts/
│   ├── clone_oracle_schema.py # Schema generator
│   ├── migrate_data.py        # Data migration engine
│   └── data_mapper.py         # Data transformation utilities
├── tests/
│   ├── sample_oracle_data.json
│   ├── test_complex_queries.py
│   └── run_all_tests.py
├── uploads/                    # Uploaded SQL files
├── requirements.txt           # Python dependencies
├── README.md                  # This file
└── .gitignore
```

## ⚙️ Configuration

### Backend Configuration

Edit `api/main.py` to configure:

```python
# CORS settings
origins = [
    "http://localhost:3000",
    "http://localhost:3001",
]

# File upload settings
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB
```

### Frontend Configuration

Edit `frontend/src/App.jsx`:

```javascript
const API_BASE_URL = 'http://localhost:8000';
```

### Database Configuration

Edit `database/migrations/table_mappings.json` to customize:
- Table definitions
- Column mappings
- Data type conversions
- Transformations
- Validations

## 🧪 Testing

### Run Backend Tests

```bash
source venv/bin/activate
python tests/run_all_tests.py
```

### Test Individual Scripts

```bash
# Test schema generation
python scripts/clone_oracle_schema.py

# Test data migration
python scripts/migrate_data.py
```

### Test API Endpoints

```bash
# Health check
curl http://localhost:8000/api/health

# TCO Analysis
curl "http://localhost:8000/api/get-tco-analysis?table_count=7&column_count=100&database_size_gb=100"
```

## 🔧 Troubleshooting

### Backend Issues

**Problem:** `ModuleNotFoundError: No module named 'fastapi'`
```bash
# Solution: Activate virtual environment and reinstall
source venv/bin/activate
pip install -r requirements.txt
```

**Problem:** Port 8000 already in use
```bash
# Solution: Use different port
uvicorn api.main:app --reload --port 8001
# Update frontend API_BASE_URL accordingly
```

### Frontend Issues

**Problem:** `npm: command not found`
```bash
# Solution: Install Node.js from https://nodejs.org/
```

**Problem:** Port 3000 already in use
```bash
# Solution: Kill process or use different port
# Edit vite.config.js to change port
lsof -ti:3000 | xargs kill -9
```

### Database Connection Issues

**Problem:** DB2 connection fails
```bash
# This is expected if DB2 is not installed
# The tool works in simulation mode without actual DB2
# For production use, install IBM DB2 client
```

## 📊 Data Type Mappings

| Oracle Type | DB2 Type | Notes |
|------------|----------|-------|
| VARCHAR2 | VARCHAR | Direct mapping |
| NUMBER | DECIMAL | Precision preserved |
| DATE | DATE | Compatible |
| CLOB | CLOB | Large objects |
| BLOB | BLOB | Binary data |
| TIMESTAMP | TIMESTAMP | Time precision |
| RAW | VARBINARY | Binary conversion |
| NVARCHAR2 | VARGRAPHIC | Unicode support |

## 🤝 Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit changes (`git commit -m 'Add AmazingFeature'`)
4. Push to branch (`git push origin feature/AmazingFeature`)
5. Open Pull Request

## 📄 License

This project is proprietary software developed for IBM DB2 migration services.

## 👥 Authors

- **Arth Soni** - Software Engineer
- **Team Code-Your-Skills** - IBM

## 🙏 Acknowledgments

- IBM DB2 Documentation
- FastAPI Framework
- React + Vite
- IBM Carbon Design System
- Tailwind CSS

## 📞 Support

For issues and questions:
- Create an issue in the repository
- Contact the development team
- Check API documentation at `/docs`

---

**Made with ❤️ for Enterprise Database Migration**
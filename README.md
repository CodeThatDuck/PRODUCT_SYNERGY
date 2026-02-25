# 🚀 Oracle to DB2 Migration Tool

A clean, JSON-driven tool for migrating Oracle databases to IBM DB2 with automatic schema conversion and data transformation.

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)

## 📋 Table of Contents

- [Features](#-features)
- [Architecture](#-architecture)
- [Prerequisites](#-prerequisites)
- [Installation](#-installation)
- [Quick Start](#-quick-start)
- [Configuration](#-configuration)
- [Usage](#-usage)
- [Testing](#-testing)
- [Project Structure](#-project-structure)
- [Data Type Mappings](#-data-type-mappings)
- [Troubleshooting](#-troubleshooting)
- [Contributing](#-contributing)
- [License](#-license)

---

## ✨ Features

- **🎯 JSON-Driven**: No hardcoded schemas - everything configured in JSON
- **🔄 Automatic Type Conversion**: 28+ Oracle to DB2 data type mappings
- **🏗️ Schema Cloning**: Creates DB2 tables from JSON configuration
- **📊 Data Migration**: Transforms and loads data with validation
- **🔗 Relationship Handling**: Automatic foreign keys and indexes
- **✅ Comprehensive Testing**: End-to-end test suite included
- **📝 SQL Generation**: Produces reference SQL files for both databases
- **🧹 Clean Architecture**: Modular, maintainable, and extensible

---

## 🏛️ Architecture

```
┌─────────────────────────────────────────────────────────┐
│                   MIGRATION WORKFLOW                     │
└─────────────────────────────────────────────────────────┘

Step 1: Configuration
├── Input: table_mappings.json
├── Defines: Oracle schema, DB2 mappings, transformations
└── Purpose: Single source of truth

Step 2: Clone Schema
├── Script: clone_oracle_schema.py
├── Reads: table_mappings.json
├── Creates: DB2 tables, indexes, constraints
├── Generates: oracle_source_schema.sql, db2_target_schema.sql
└── Output: Empty DB2 schema

Step 3: Migrate Data
├── Script: migrate_data.py
├── Reads: table_mappings.json
├── Extracts: Data from Oracle (or mock data)
├── Transforms: Based on JSON rules
├── Loads: Into DB2 tables
└── Output: Migrated data in DB2
```

---

## 📦 Prerequisites

### Required Software

1. **Python 3.8+**
   ```bash
   python --version  # Should be 3.8 or higher
   ```

2. **Podman or Docker** (for DB2 container)
   ```bash
   podman --version
   # or
   docker --version
   ```

3. **IBM DB2 Database**
   - Option A: Use provided Podman container
   - Option B: Connect to existing DB2 instance

---

## 🔧 Installation

### 1. Clone the Repository

```bash
git clone https://github.com/CodeThatDuck/PRODUCT_SYNERGY.git
cd PRODUCT_SYNERGY
```

### 2. Set Up Python Virtual Environment

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# On macOS/Linux:
source venv/bin/activate

# On Windows:
venv\Scripts\activate
```

### 3. Install Python Dependencies

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

**Note:** Installing `ibm_db` may take a few minutes as it compiles native extensions.

### 4. Set Up DB2 Container (Optional)

If you don't have an existing DB2 instance:

```bash
# Start DB2 container using Podman
bash scripts/setup_db.sh

# Verify container is running
podman ps | grep db2

# Check DB2 logs
podman logs product-synergy-db2
```

**Container Details:**
- **Database Name:** `proddb`
- **Port:** `5001`
- **Username:** `db2inst1`
- **Password:** `password`

---

## 🚀 Quick Start

### 1. Configure Your Schema

Edit `database/migrations/table_mappings.json` to define your tables:

```json
{
  "tables": {
    "YOUR_TABLE": {
      "description": "Your table description",
      "primary_key": "ID",
      "columns": {
        "ID": {
          "oracle_type": "NUMBER(10)",
          "db2_type": "DECIMAL(10,0)",
          "nullable": false,
          "transformation": "string_to_integer"
        },
        "NAME": {
          "oracle_type": "VARCHAR2(255)",
          "db2_type": "VARCHAR(255)",
          "nullable": false,
          "transformation": "trim_string"
        }
      }
    }
  }
}
```

### 2. Clone Oracle Schema to DB2

```bash
python scripts/clone_oracle_schema.py
```

**This will:**
- ✅ Read your JSON configuration
- ✅ Generate `oracle_source_schema.sql` (reference)
- ✅ Generate `db2_target_schema.sql` (reference)
- ✅ Create all tables in DB2
- ✅ Add foreign keys and indexes
- ✅ Verify table creation

### 3. Migrate Data

```bash
python scripts/migrate_data.py
```

**This will:**
- ✅ Extract data from Oracle (currently mocked)
- ✅ Transform data based on JSON rules
- ✅ Load data into DB2 tables
- ✅ Generate migration report

---

## ⚙️ Configuration

### Main Configuration File

**Location:** `database/migrations/table_mappings.json`

#### Table Definition Structure

```json
{
  "tables": {
    "TABLE_NAME": {
      "description": "Table description",
      "primary_key": "COLUMN_NAME",
      "foreign_keys": {
        "FK_COLUMN": "REFERENCED_TABLE.REFERENCED_COLUMN"
      },
      "columns": {
        "COLUMN_NAME": {
          "oracle_type": "Oracle data type",
          "db2_type": "DB2 data type",
          "nullable": true/false,
          "transformation": "transformation_rule",
          "validation": {
            "type": "data_type",
            "min": minimum_value,
            "max": maximum_value
          },
          "notes": "Optional notes"
        }
      }
    }
  }
}
```

#### Available Transformations

| Transformation | Description | Example |
|---------------|-------------|---------|
| `string_to_integer` | Convert string to integer | `"123"` → `123` |
| `string_to_decimal` | Convert string to decimal | `"99.99"` → `99.99` |
| `trim_string` | Remove whitespace | `"  text  "` → `"text"` |
| `string_to_timestamp` | Parse timestamp | `"2024-01-01"` → `TIMESTAMP` |
| `pass_through` | No transformation | Binary data unchanged |

### Database Connection

**Location:** `scripts/clone_oracle_schema.py` and `scripts/migrate_data.py`

```python
DB2_CONFIG = {
    "DATABASE": "proddb",
    "HOSTNAME": "localhost",
    "PORT": "5001",
    "PROTOCOL": "TCPIP",
    "UID": "db2inst1",
    "PWD": "password"
}
```

---

## 📖 Usage

### Basic Workflow

```bash
# 1. Activate virtual environment
source venv/bin/activate

# 2. Clone schema
python scripts/clone_oracle_schema.py

# 3. Migrate data
python scripts/migrate_data.py
```

### Advanced Options

#### Verify DB2 Connection

```bash
python -c "import ibm_db; conn = ibm_db.connect('DATABASE=proddb;HOSTNAME=localhost;PORT=5001;PROTOCOL=TCPIP;UID=db2inst1;PWD=password;', '', ''); print('✅ Connected to DB2')"
```

#### Check Tables in DB2

```bash
podman exec product-synergy-db2 su - db2inst1 -c "db2 connect to proddb && db2 list tables && db2 connect reset"
```

#### Query Data

```bash
podman exec product-synergy-db2 su - db2inst1 -c "db2 connect to proddb && db2 'SELECT * FROM PRODUCTS' && db2 connect reset"
```

---

## 🧪 Testing

### Run Complete End-to-End Test

```bash
python tests/test_complete_migration.py
```

**Test Coverage:**
- ✅ Drops existing tables (clean slate)
- ✅ Creates schema from JSON
- ✅ Loads sample data
- ✅ Verifies record counts
- ✅ Displays sample data with SELECT queries
- ✅ Tests all 4 tables (14 records total)

### Expected Output

```
============================================================
Complete End-to-End Migration Test
============================================================

📋 Loading configuration...
✅ Config: 4 tables
✅ Sample data: 14 total records

🔌 Connecting to DB2...
✅ Connected

🗑️  Dropping existing tables...
  ✅ Dropped ORACLE_DATATYPE_COMPREHENSIVE
  ✅ Dropped DATATYPE_TEST
  ✅ Dropped SYNERGIES
  ✅ Dropped PRODUCTS

🔨 Creating tables...
  ✅ Created table PRODUCTS
  ✅ Created table SYNERGIES
  ✅ Created table DATATYPE_TEST
  ✅ Created table ORACLE_DATATYPE_COMPREHENSIVE

📥 Loading sample data...
  ✅ PRODUCTS: Loaded 5/5 records
  ✅ SYNERGIES: Loaded 5/5 records
  ✅ DATATYPE_TEST: Loaded 2/2 records
  ✅ ORACLE_DATATYPE_COMPREHENSIVE: Loaded 2/2 records

✓ Verifying data...
  ✅ PRODUCTS: 5 rows (expected 5)
  ✅ SYNERGIES: 5 rows (expected 5)
  ✅ DATATYPE_TEST: 2 rows (expected 2)
  ✅ ORACLE_DATATYPE_COMPREHENSIVE: 2 rows (expected 2)

============================================================
✅ ALL TESTS PASSED!
✅ Successfully migrated 14 records
============================================================
```

### Test Data

Sample data is located in `tests/sample_oracle_data.json`. Modify this file to test with your own data.

---

## 📁 Project Structure

```
PRODUCT_SYNERGY/
├── database/
│   ├── migrations/
│   │   ├── table_mappings.json          # Main configuration
│   │   └── type_mappings_reference.json # Type conversion reference
│   └── schemas/
│       ├── oracle_source_schema.sql     # Generated Oracle schema
│       └── db2_target_schema.sql        # Generated DB2 schema
├── scripts/
│   ├── clone_oracle_schema.py           # Schema cloning script
│   ├── migrate_data.py                  # Data migration script
│   └── setup_db.sh                      # DB2 container setup
├── tests/
│   ├── sample_oracle_data.json          # Test data
│   ├── test_complete_migration.py       # End-to-end test
│   └── 00_connection_test.py            # Connection test
├── docs/
│   └── ORACLE_TO_DB2_DATATYPE_MAPPINGS.md  # Type reference
├── requirements.txt                     # Python dependencies
├── podman-compose.yml                   # Container configuration
├── .gitignore                           # Git ignore rules
└── README.md                            # This file
```

---

## 🔄 Data Type Mappings

### Common Mappings

| Oracle Type | DB2 Type | Notes |
|------------|----------|-------|
| `NUMBER(p,s)` | `DECIMAL(p,s)` | Precision preserved |
| `VARCHAR2(n)` | `VARCHAR(n)` | Direct mapping |
| `DATE` | `TIMESTAMP` | Oracle DATE includes time |
| `CLOB` | `CLOB` | Large text objects |
| `BLOB` | `BLOB` | Binary objects |
| `FLOAT` | `DOUBLE` | Floating point |
| `NVARCHAR2(n)` | `VARGRAPHIC(n)` | Unicode support |
| `ROWID` | `VARCHAR(18)` | No direct equivalent |

**See `docs/ORACLE_TO_DB2_DATATYPE_MAPPINGS.md` for complete reference (28+ types).**

---

## 🔍 Troubleshooting

### Common Issues

#### 1. `ibm_db` Installation Fails

**Problem:** Compilation errors during `pip install ibm_db`

**Solution:**
```bash
# macOS
brew install gcc

# Ubuntu/Debian
sudo apt-get install gcc python3-dev

# Then retry
pip install ibm_db
```

#### 2. DB2 Container Won't Start

**Problem:** Port 5001 already in use

**Solution:**
```bash
# Check what's using the port
lsof -i :5001

# Stop the container
podman stop product-synergy-db2

# Remove the container
podman rm product-synergy-db2

# Restart
bash scripts/setup_db.sh
```

#### 3. Connection Refused

**Problem:** Cannot connect to DB2

**Solution:**
```bash
# Check container status
podman ps -a | grep db2

# Check logs
podman logs product-synergy-db2

# Restart container
podman restart product-synergy-db2

# Wait 30 seconds for DB2 to initialize
sleep 30
```

#### 4. Table Already Exists

**Problem:** Tables already exist in DB2

**Solution:**
```bash
# Drop tables manually
podman exec product-synergy-db2 su - db2inst1 -c "db2 connect to proddb && db2 'DROP TABLE SYNERGIES' && db2 'DROP TABLE PRODUCTS' && db2 connect reset"

# Or run the test script (it drops tables automatically)
python tests/test_complete_migration.py
```

---

## 🤝 Contributing

Contributions are welcome! Please ensure:

1. **No hardcoded schemas** - All configurations in JSON
2. **Clean, modular code** - Follow existing patterns
3. **Documentation updates** - Update README for new features
4. **Tests pass** - Run `python tests/test_complete_migration.py`

### Development Setup

```bash
# Fork and clone the repository
git clone https://github.com/YOUR_USERNAME/PRODUCT_SYNERGY.git
cd PRODUCT_SYNERGY

# Create a feature branch
git checkout -b feature/your-feature-name

# Make changes and test
python tests/test_complete_migration.py

# Commit and push
git add .
git commit -m "Add your feature"
git push origin feature/your-feature-name

# Create a Pull Request on GitHub
```

---

## 📄 License

MIT License - Feel free to use and modify

---

## 🙏 Acknowledgments

- IBM DB2 Documentation
- Oracle Database Documentation
- Python `ibm_db` driver maintainers

---

## 📞 Support

- **Issues:** [GitHub Issues](https://github.com/CodeThatDuck/PRODUCT_SYNERGY/issues)
- **Discussions:** [GitHub Discussions](https://github.com/CodeThatDuck/PRODUCT_SYNERGY/discussions)

---

**Built with ❤️ for clean, maintainable database migrations**

---

## 🗺️ Roadmap

- [ ] SQL Parser (auto-generate JSON from Oracle SQL)
- [ ] Real Oracle connection (replace mock data)
- [ ] Incremental migration support
- [ ] Data validation and verification
- [ ] Migration rollback support
- [ ] Performance optimization for large datasets
- [ ] Web UI for configuration
- [ ] Docker Compose support
- [ ] CI/CD integration examples

---

**⭐ Star this repo if you find it useful!**
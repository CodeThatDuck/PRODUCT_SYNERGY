# 🚀 Project Synergy: Final Workflow Guide

**Oracle to DB2 Takeout Engine** — Complete step-by-step execution guide for the full migration pipeline.

---

## 📋 Table of Contents

1. [Prerequisites](#prerequisites)
2. [Architecture Overview](#architecture-overview)
3. [Step-by-Step Workflow](#step-by-step-workflow)
   - [Phase 0: Environment Setup](#phase-0-environment-setup)
   - [Phase 1: DB2 Container Setup](#phase-1-db2-container-setup)
   - [Phase 2: Connection Validation](#phase-2-connection-validation)
   - [Phase 3: Schema Generation & Cloning](#phase-3-schema-generation--cloning)
   - [Phase 4: Data Migration](#phase-4-data-migration)
   - [Phase 5: Full Test Suite](#phase-5-full-test-suite)
   - [Phase 6: Web Application](#phase-6-web-application)
4. [Script Reference](#script-reference)
5. [Configuration Files](#configuration-files)
6. [Troubleshooting](#troubleshooting)

---

## Prerequisites

| Requirement | Version | Check Command |
|-------------|---------|---------------|
| Python | 3.8+ | `python3 --version` |
| Node.js | 16+ | `node --version` |
| Podman | 4.0+ | `podman --version` |
| ibm_db | 3.x | `pip show ibm_db` |

### Install Python Dependencies

```bash
# Create and activate virtual environment
python3 -m venv venv
source venv/bin/activate   # macOS/Linux
# venv\Scripts\activate    # Windows

# Install all dependencies
pip install -r requirements.txt
```

### Install Frontend Dependencies

```bash
cd frontend
npm install
cd ..
```

---

## Architecture Overview

```
Oracle Source (SQL DDL)
        │
        ▼
┌───────────────────┐
│  table_mappings   │  ← JSON-driven configuration
│      .json        │    (7 tables, types, transforms)
└────────┬──────────┘
         │
    ┌────▼────┐
    │ Phase 3 │  clone_oracle_schema.py
    │ Schema  │  → Generates oracle_source_schema.sql
    │ Cloner  │  → Generates db2_target_schema.sql
    └────┬────┘  → Creates tables in DB2
         │
    ┌────▼────┐
    │ Phase 4 │  test_complete_flow.py
    │  Data   │  → DataMapper transforms 39 records
    │ Migrate │  → Loads into DB2 (7 tables)
    └────┬────┘  → Verifies row counts
         │
    ┌────▼────┐
    │ Phase 5 │  test_complex_queries.py
    │  Query  │  → JOINs, aggregates, subqueries
    │  Tests  │  → Validates DB2 SQL compatibility
    └─────────┘
         │
    ┌────▼────┐
    │ Phase 6 │  FastAPI + React
    │   Web   │  → Upload Oracle SQL
    │   App   │  → View SQL diff
    └─────────┘  → Run migration
                 → TCO Calculator
```

---

## Step-by-Step Workflow

### Phase 0: Environment Setup

```bash
# 1. Navigate to project root
cd "Product Synergy"

# 2. Activate Python virtual environment
source venv/bin/activate

# 3. Verify all dependencies are installed
python -c "import ibm_db, fastapi, uvicorn; print('✅ All dependencies OK')"
```

---

### Phase 1: DB2 Container Setup

Start the IBM DB2 container using Podman:

```bash
# Start DB2 container (first time - takes ~5 minutes to initialize)
podman-compose up -d

# OR if container already exists but is stopped:
podman start product-synergy-db2

# Monitor initialization progress (wait for "DB2START processing was successful")
podman logs -f product-synergy-db2 2>&1 | grep -E "DB2START|Task #|completed"
```

**Container Configuration:**

| Setting | Value |
|---------|-------|
| Container Name | `product-synergy-db2` |
| Image | `ibmcom/db2:latest` |
| Host Port | `5001` |
| Container Port | `50000` |
| Database Name | `proddb` |
| Username | `db2inst1` |
| Password | `password` |

**Verify DB2 is running:**

```bash
# Check container status
podman ps | grep db2

# Test DB2 connection from inside container
podman exec product-synergy-db2 su - db2inst1 -c "db2 connect to proddb"
```

---

### Phase 2: Connection Validation

Run the connection test to verify DB2 is accessible:

```bash
source venv/bin/activate
python tests/00_connection_test.py
```

**Expected Output:**
```
============================================================
PHASE 0: DATABASE CONNECTION VALIDATION
============================================================
[1/3] Attempting database connection...
✅ Connection Established Successfully
[2/3] Querying SYNERGY_LOG table...
[3/3] Validating data...
✅ PHASE 0 COMPLETE: SYSTEM IS READY FOR SYNERGY
```

> **Note:** If `SYNERGY_LOG` table doesn't exist yet, run `scripts/setup_db.sh` first.

---

### Phase 3: Schema Generation & Cloning

This script reads `table_mappings.json` and:
1. Generates `oracle_source_schema.sql` (Oracle DDL)
2. Generates `db2_target_schema.sql` (DB2 DDL)
3. Creates all 7 tables in the live DB2 database

```bash
source venv/bin/activate
python scripts/clone_oracle_schema.py
```

**What it does:**
- **Phase 1:** Creates 7 tables (PRODUCTS, CUSTOMERS, ORDERS, ORDER_ITEMS, SYNERGIES, DATATYPE_TEST, ORACLE_DATATYPE_COMPREHENSIVE)
- **Phase 2:** Adds foreign key constraints
- **Phase 3:** Creates indexes on foreign key columns
- **Phase 4:** Adds table and column comments
- **Verification:** Queries each table to confirm creation

**Expected Output:**
```
============================================================
Oracle to DB2 Schema Cloner
JSON-Driven Schema Creation
============================================================
✅ Loaded 7 table definitions

GENERATING SQL FILES
📝 Generating Oracle schema...
✅ Saved: database/schemas/oracle_source_schema.sql
📝 Generating DB2 schema...
✅ Saved: database/schemas/db2_target_schema.sql

PHASE 1: Creating Tables
🔨 Creating table: PRODUCTS
  ✅ Created table PRODUCTS
...
✅ Schema cloning completed successfully!
```

---

### Phase 4: Data Migration

#### Option A: Run the complete end-to-end flow test (Recommended)

```bash
source venv/bin/activate
python tests/test_complete_flow.py
```

This runs all 6 steps:
1. **Verify** Oracle schema file exists
2. **Map** sample data using `DataMapper` (13 transformations, 9 validations)
3. **Clone** schema to DB2 (drop + recreate for clean slate)
4. **Migrate** 39 mock records across 7 tables
5. **Verify** row counts match expected
6. **Query** sample data from DB2

**Expected Output:**
```
COMPLETE END-TO-END MIGRATION FLOW TEST
Oracle SQL → JSON Mapping → DB2 Schema → Data Migration

STEP 1: Verify Oracle SQL Schema File
✅ Oracle schema file found

STEP 2: Create Mapped JSON File using DataMapper
✅ DataMapper initialized
✅ Loaded 7 tables with sample data
   Total rows processed: 39
   Success rate: 100.00%
✅ Mapped JSON file created: tests/mapped_data_output.json

STEP 3: Clone Schema from JSON to DB2
✅ Connected to DB2
✅ Schema cloning completed successfully!

STEP 4: Migrate Mock Data to DB2
✅ Total records migrated: 39

STEP 5: Verify Data Migration
✅ PRODUCTS: 5 rows (expected 5)
✅ CUSTOMERS: 5 rows (expected 5)
✅ ORDERS: 5 rows (expected 5)
...

✅ ALL TESTS PASSED!
✅ Complete migration flow successful!
```

#### Option B: Run migrate_data.py (production mode)

```bash
source venv/bin/activate
python scripts/migrate_data.py
```

> **Note:** This script connects to a real Oracle source. Without Oracle, it returns 0 records (mock mode). Use `test_complete_flow.py` for demo with sample data.

#### Option C: Load sample data directly

```bash
# First ensure schema exists (Phase 3), then:
source venv/bin/activate
python scripts/load_sample_data_to_db2.py
```

---

### Phase 5: Full Test Suite

Run all tests in sequence:

```bash
source venv/bin/activate
python tests/run_all_tests.py
```

**Test sequence:**
1. `scripts/clone_oracle_schema.py` — Schema generation
2. `tests/test_complete_flow.py` — End-to-end migration
3. `tests/test_complex_queries.py` — Complex SQL queries

**What's tested:**
- ✅ Schema generation (Oracle → DB2)
- ✅ Table creation with foreign keys and indexes
- ✅ Data mapping and transformation (39 records)
- ✅ Simple JOINs (INNER, LEFT)
- ✅ Multi-table JOINs (3-4 tables)
- ✅ Aggregate functions (COUNT, SUM, AVG, MIN, MAX)
- ✅ Subqueries and complex WHERE clauses
- ✅ Advanced analytics (CASE, date functions, self-JOINs)

---

### Phase 6: Web Application

Start the full web application:

```bash
# Terminal 1: Backend API (FastAPI)
source venv/bin/activate
uvicorn api.main:app --reload --host 0.0.0.0 --port 8000

# Terminal 2: Frontend (React + Vite)
cd frontend
npm run dev
```

**Access Points:**

| Service | URL |
|---------|-----|
| Frontend UI | http://localhost:3001 |
| Backend API | http://localhost:8000 |
| API Docs (Swagger) | http://localhost:8000/docs |

**UI Tabs:**

| Tab | Description |
|-----|-------------|
| 📥 Source Ingestion | Upload Oracle SQL DDL file |
| 🔍 SQL Diff Viewer | Side-by-side Oracle vs DB2 SQL comparison |
| 🚀 Migration & Data Audit | Run migration, view results table |
| 💰 TCO Calculator | Oracle vs DB2 cost analysis with ROI |

---

## Script Reference

| Script | Purpose | Requires DB2 |
|--------|---------|:------------:|
| `tests/00_connection_test.py` | Validate DB2 connection | ✅ |
| `scripts/clone_oracle_schema.py` | Generate SQL files + create DB2 tables | ✅ |
| `scripts/migrate_data.py` | Migrate data from Oracle to DB2 | ✅ |
| `scripts/load_sample_data_to_db2.py` | Load sample JSON data into DB2 | ✅ |
| `scripts/data_mapper.py` | Data transformation utility (importable) | ❌ |
| `tests/test_complete_flow.py` | Full end-to-end test with sample data | ✅ |
| `tests/test_complex_queries.py` | Complex SQL query tests | ✅ |
| `tests/run_all_tests.py` | Master test runner (runs all above) | ✅ |
| `scripts/setup_db2_schemas.sh` | Shell script to apply DB2 schema SQL | ✅ |
| `api/main.py` | FastAPI backend server | ❌ |

---

## Configuration Files

### `database/migrations/table_mappings.json`

The **central configuration** that drives everything. Defines:
- 7 tables with Oracle → DB2 type mappings
- Column-level transformations (13 types)
- Validation rules (9 types)
- Foreign key relationships
- Primary keys

**Transformation types available:**
```
string_to_integer    string_to_decimal    trim_string
string_to_timestamp  pass_through         uppercase
lowercase            remove_special_chars  normalize_phone
normalize_email      string_to_boolean    pad_string
truncate_string
```

**Validation types available:**
```
integer   decimal   string   timestamp   binary
email     phone     url      range
```

### `database/migrations/type_mappings_reference.json`

Reference guide for Oracle → DB2 data type conversions (28+ types).

---

## Troubleshooting

### DB2 Container Not Starting

```bash
# Check container status
podman ps -a | grep db2

# View logs
podman logs product-synergy-db2 2>&1 | tail -50

# Restart container
podman restart product-synergy-db2

# Wait for full initialization (~5 minutes on first start)
podman logs -f product-synergy-db2 2>&1 | grep "DB2START"
```

### Connection Refused (Port 5001)

```bash
# Verify port mapping
podman port product-synergy-db2

# Test from inside container
podman exec product-synergy-db2 su - db2inst1 -c "db2 connect to proddb"

# Check if DB2 is listening
podman exec product-synergy-db2 netstat -tlnp | grep 50000
```

### `ibm_db` Module Not Found

```bash
# Ensure virtual environment is active
source venv/bin/activate

# Reinstall ibm_db
pip install ibm_db==3.2.3
```

### Table Already Exists Error

The `test_complete_flow.py` script automatically drops and recreates tables. For `clone_oracle_schema.py`, it skips existing tables with a warning. To force recreate:

```bash
# Drop all tables manually
podman exec product-synergy-db2 su - db2inst1 -c "
db2 connect to proddb
db2 'DROP TABLE ORDER_ITEMS'
db2 'DROP TABLE ORDERS'
db2 'DROP TABLE SYNERGIES'
db2 'DROP TABLE CUSTOMERS'
db2 'DROP TABLE PRODUCTS'
db2 'DROP TABLE DATATYPE_TEST'
db2 'DROP TABLE ORACLE_DATATYPE_COMPREHENSIVE'
db2 connect reset
"
```

### Frontend Not Loading

```bash
# Check if backend is running
curl http://localhost:8000/api/health

# Reinstall frontend dependencies
cd frontend && npm install && npm run dev
```

---

## Quick Reference: Run Everything

```bash
# 1. Start DB2
podman start product-synergy-db2
sleep 90  # Wait for initialization

# 2. Activate Python env
source venv/bin/activate

# 3. Test connection
python tests/00_connection_test.py

# 4. Run full test suite
python tests/run_all_tests.py

# 5. Start web app (two terminals)
uvicorn api.main:app --reload --port 8000 &
cd frontend && npm run dev
```

---

*Made with ❤️ for Enterprise Database Migration — Project Synergy*
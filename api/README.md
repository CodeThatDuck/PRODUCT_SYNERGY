# Oracle to DB2 Migration API

FastAPI-based REST API for converting Oracle SQL to DB2 and migrating data.

## Installation

```bash
# Install dependencies
pip install -r requirements.txt
```

## Running the API

```bash
# Start the server
cd /Users/abhinavb/PRODUCT_SYNERGY
uvicorn api.main:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at: `http://localhost:8000`

## API Documentation

Once running, visit:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## Endpoints

### 1. Health Check
```http
GET /api/health
```

**Response:**
```json
{
  "status": "healthy",
  "service": "Oracle to DB2 Migration API",
  "version": "1.0.0"
}
```

---

### 2. Upload Oracle SQL File
```http
POST /api/upload
Content-Type: multipart/form-data
```

**Parameters:**
- `file`: SQL file (only .sql files accepted)

**Response:**
```json
{
  "status": "success",
  "message": "Oracle SQL file uploaded successfully",
  "file_info": {
    "filename": "oracle_schema.sql",
    "saved_as": "oracle_schema_oracle.sql",
    "size_bytes": 2048,
    "total_lines": 86,
    "preview": "-- First 10 lines of the file..."
  }
}
```

**Example using curl:**
```bash
curl -X POST "http://localhost:8000/api/upload" \
  -H "accept: application/json" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@database/schemas/oracle_source_schema.sql"
```

---

### 3. Convert Oracle SQL to DB2 (3-Part Process)
```http
POST /api/convert?filename=oracle_schema_oracle.sql
```

**Parameters:**
- `filename`: Name of the uploaded SQL file (from upload endpoint)

**Response:**
```json
{
  "status": "success",
  "filename": "oracle_schema_oracle.sql",
  "parts": {
    "part_a_parse_to_json": {
      "status": "completed",
      "message": "Oracle SQL parsed to JSON successfully",
      "output_file": "oracle_schema_mapped.json",
      "tables_found": 4,
      "json_preview": {
        "tables": ["PRODUCTS", "SYNERGIES", "DATATYPE_TEST", "ORACLE_DATATYPE_COMPREHENSIVE"]
      }
    },
    "part_b_clone_schema": {
      "status": "completed",
      "message": "DB2 schema generated successfully",
      "output_file": "oracle_schema_db2_schema.sql",
      "statistics": {
        "tables_created": 4,
        "foreign_keys": 2,
        "indexes": 2
      },
      "schema_preview": ["PRODUCTS", "SYNERGIES", "DATATYPE_TEST", "ORACLE_DATATYPE_COMPREHENSIVE"]
    },
    "part_c_migrate_data": {
      "status": "completed",
      "message": "Data migration completed (using dummy data)",
      "note": "Currently using sample data. Will be updated to use actual data tomorrow.",
      "output_file": "oracle_schema_mapped_data.json",
      "statistics": {
        "total_rows_processed": 14,
        "successful_rows": 14,
        "failed_rows": 0,
        "transformations_applied": 107,
        "success_rate": "100.00%"
      },
      "tables_migrated": ["PRODUCTS", "SYNERGIES", "DATATYPE_TEST", "ORACLE_DATATYPE_COMPREHENSIVE"]
    }
  },
  "summary": {
    "total_parts": 3,
    "completed_parts": 3,
    "overall_status": "success"
  }
}
```

**Example using curl:**
```bash
curl -X POST "http://localhost:8000/api/convert?filename=oracle_schema_oracle.sql" \
  -H "accept: application/json"
```

---

## Complete Workflow Example

### Step 1: Upload Oracle SQL File
```bash
curl -X POST "http://localhost:8000/api/upload" \
  -F "file=@database/schemas/oracle_source_schema.sql"
```

### Step 2: Convert to DB2
```bash
curl -X POST "http://localhost:8000/api/convert?filename=oracle_source_schema_oracle.sql"
```

### Step 3: Check Output Files
Generated files will be in the `outputs/` directory:
- `{filename}_mapped.json` - Parsed JSON structure
- `{filename}_db2_schema.sql` - DB2 schema SQL
- `{filename}_mapped_data.json` - Migrated data (dummy data for now)

---

## Directory Structure

```
PRODUCT_SYNERGY/
├── api/
│   ├── main.py          # FastAPI application
│   └── README.md        # This file
├── uploads/             # Uploaded SQL files (auto-created)
├── outputs/             # Generated output files (auto-created)
├── database/
│   └── migrations/
│       └── table_mappings.json  # Configuration
└── scripts/
    ├── data_mapper.py           # Data mapping utility
    └── clone_oracle_schema.py   # Schema cloning utility
```

---

## Error Handling

### 400 Bad Request
- Invalid file type (not .sql)
- Missing required parameters

### 404 Not Found
- File not found (must upload first)

### 500 Internal Server Error
- Conversion process failed
- Check error details in response

---

## Notes

- **Part C (Data Migration)**: Currently uses dummy sample data from `tests/sample_oracle_data.json`
- **Tomorrow's Update**: Will be modified to use actual data from the uploaded SQL file
- **Comparison Endpoint**: Will be added tomorrow

---

## Testing

```bash
# Run the API
uvicorn api.main:app --reload

# In another terminal, test the endpoints
python api/test_api.py
```

---

**Made with Bob**
#!/usr/bin/env python3
"""
Oracle to DB2 Data Migration
Reads JSON configuration and migrates data dynamically
No hardcoded schemas - purely JSON-driven
"""

import json
import sys
import ibm_db
from pathlib import Path
from typing import Dict, List, Any
from decimal import Decimal
from datetime import datetime

# Paths
SCRIPT_DIR = Path(__file__).parent
PROJECT_ROOT = SCRIPT_DIR.parent
CONFIG_PATH = PROJECT_ROOT / "database" / "migrations" / "table_mappings.json"

# DB2 Connection Configuration
DB2_CONFIG = {
    "DATABASE": "proddb",
    "HOSTNAME": "localhost",
    "PORT": "5001",
    "PROTOCOL": "TCPIP",
    "UID": "db2inst1",
    "PWD": "password"
}

# Batch size for inserts
BATCH_SIZE = 100


def load_json_config(config_path: Path) -> Dict:
    """Load JSON configuration file"""
    try:
        with open(config_path, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"❌ Configuration file not found: {config_path}")
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"❌ Invalid JSON: {e}")
        sys.exit(1)


def connect_to_db2() -> Any:
    """Connect to DB2 database"""
    dsn = ";".join([f"{k}={v}" for k, v in DB2_CONFIG.items()])
    try:
        conn = ibm_db.connect(dsn, "", "")
        print("✅ Connected to DB2")
        return conn
    except Exception as e:
        print(f"❌ DB2 connection failed: {e}")
        sys.exit(1)


def extract_from_oracle_mock(table_name: str, columns: Dict) -> List[Dict]:
    """
    Mock Oracle data extraction
    In production, this would connect to Oracle and extract real data
    
    Returns empty list - no hardcoded data
    To add test data, connect to real Oracle or create a separate data file
    """
    # Return empty list - no mock data
    # In production: Connect to Oracle and execute SELECT * FROM table_name
    return []


def transform_value(value: Any, col_config: Dict) -> Any:
    """Transform value based on column configuration"""
    if value is None or value == '':
        return None
    
    transformation = col_config.get('transformation', 'pass_through')
    
    try:
        if transformation == 'string_to_integer':
            return int(str(value).strip())
        
        elif transformation == 'string_to_decimal':
            return Decimal(str(value).strip())
        
        elif transformation == 'trim_string':
            return str(value).strip()
        
        elif transformation == 'string_to_timestamp':
            # Parse timestamp string
            if isinstance(value, str):
                return datetime.fromisoformat(value.strip())
            return value
        
        elif transformation == 'pass_through':
            return value
        
        else:
            return value
            
    except Exception as e:
        print(f"    ⚠️  Transformation error for value '{value}': {e}")
        return None


def transform_row(row: Dict, columns: Dict) -> Dict:
    """Transform a single row based on column configurations"""
    transformed = {}
    
    for col_name, col_config in columns.items():
        if col_name in row:
            transformed[col_name] = transform_value(row[col_name], col_config)
        else:
            transformed[col_name] = None
    
    return transformed


def build_insert_sql(table_name: str, columns: List[str]) -> str:
    """Build INSERT SQL statement"""
    placeholders = ", ".join(["?" for _ in columns])
    col_list = ", ".join(columns)
    return f"INSERT INTO {table_name} ({col_list}) VALUES ({placeholders})"


def insert_batch(conn: Any, table_name: str, columns: List[str], rows: List[Dict]) -> int:
    """Insert a batch of rows"""
    if not rows:
        return 0
    
    sql = build_insert_sql(table_name, columns)
    inserted = 0
    
    try:
        # Prepare statement
        stmt = ibm_db.prepare(conn, sql)
        
        for row in rows:
            try:
                # Bind parameters
                values = tuple(row[col] for col in columns)
                ibm_db.execute(stmt, values)
                inserted += 1
            except Exception as e:
                error_msg = str(e)
                if "SQL0803N" in error_msg or "duplicate" in error_msg.lower():
                    # Duplicate key - skip
                    continue
                else:
                    print(f"    ⚠️  Insert failed: {e}")
        
        return inserted
        
    except Exception as e:
        print(f"    ❌ Batch insert failed: {e}")
        return 0


def migrate_table(conn: Any, table_name: str, table_config: Dict):
    """Migrate data for a single table"""
    print(f"\n{'=' * 60}")
    print(f"MIGRATING TABLE: {table_name}")
    print(f"{'=' * 60}")
    
    columns = table_config.get('columns', {})
    
    # Phase 1: Extract
    print(f"\n📥 PHASE 1: Extracting data from Oracle (Mock)")
    oracle_data = extract_from_oracle_mock(table_name, columns)
    print(f"  ✅ Extracted {len(oracle_data)} records")
    
    if not oracle_data:
        print(f"  ⚠️  No data to migrate for {table_name}")
        return
    
    # Phase 2: Transform
    print(f"\n🔄 PHASE 2: Transforming data")
    transformed_data = []
    for row in oracle_data:
        transformed_row = transform_row(row, columns)
        transformed_data.append(transformed_row)
    print(f"  ✅ Transformed {len(transformed_data)} records")
    
    # Phase 3: Load
    print(f"\n📤 PHASE 3: Loading data into DB2")
    column_names = list(columns.keys())
    
    # Insert in batches
    total_inserted = 0
    for i in range(0, len(transformed_data), BATCH_SIZE):
        batch = transformed_data[i:i + BATCH_SIZE]
        inserted = insert_batch(conn, table_name, column_names, batch)
        total_inserted += inserted
    
    print(f"  ✅ Loaded {total_inserted} records")
    
    # Phase 4: Verify
    print(f"\n✓ PHASE 4: Verifying data")
    try:
        sql = f"SELECT COUNT(*) FROM {table_name}"
        stmt = ibm_db.exec_immediate(conn, sql)
        if stmt:
            row = ibm_db.fetch_tuple(stmt)
            count = row[0] if row else 0
            print(f"  ✅ Total records in {table_name}: {count}")
    except Exception as e:
        print(f"  ⚠️  Verification failed: {e}")


def generate_migration_report(config: Dict, conn: Any):
    """Generate migration summary report"""
    print(f"\n{'=' * 60}")
    print("MIGRATION REPORT")
    print(f"{'=' * 60}\n")
    
    tables = config.get('tables', {})
    
    for table_name in tables.keys():
        try:
            sql = f"SELECT COUNT(*) FROM {table_name}"
            stmt = ibm_db.exec_immediate(conn, sql)
            if stmt:
                row = ibm_db.fetch_tuple(stmt)
                count = row[0] if row else 0
                print(f"  {table_name}: {count} rows")
        except Exception as e:
            print(f"  {table_name}: Error - {e}")
    
    print(f"\n{'=' * 60}")
    print("✅ Migration completed!")
    print(f"{'=' * 60}")


def main():
    """Main execution"""
    print("=" * 60)
    print("Oracle to DB2 Data Migration")
    print("JSON-Driven Data Migration")
    print("=" * 60)
    
    # Load configuration
    print(f"\n📋 Loading configuration: {CONFIG_PATH}")
    config = load_json_config(CONFIG_PATH)
    tables = config.get('tables', {})
    print(f"✅ Loaded {len(tables)} table definitions")
    
    # Connect to DB2
    print("\n🔌 Connecting to DB2...")
    conn = connect_to_db2()
    
    try:
        # Migrate each table
        for table_name, table_config in tables.items():
            migrate_table(conn, table_name, table_config)
        
        # Generate report
        generate_migration_report(config, conn)
        
    finally:
        ibm_db.close(conn)
        print("\n🔌 Connection closed")


if __name__ == "__main__":
    main()

# Made with Bob

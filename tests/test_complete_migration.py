#!/usr/bin/env python3
"""
Complete End-to-End Migration Test
1. Clones Oracle schema to DB2
2. Loads sample data from JSON file
3. Verifies data migration
"""

import json
import sys
import ibm_db
from pathlib import Path
from decimal import Decimal
from datetime import datetime

# Paths
SCRIPT_DIR = Path(__file__).parent
PROJECT_ROOT = SCRIPT_DIR.parent
CONFIG_PATH = PROJECT_ROOT / "database" / "migrations" / "table_mappings.json"
SAMPLE_DATA_PATH = SCRIPT_DIR / "sample_oracle_data.json"

# Add scripts to path
sys.path.insert(0, str(PROJECT_ROOT / "scripts"))

# DB2 Connection
DB2_CONFIG = {
    "DATABASE": "proddb",
    "HOSTNAME": "localhost",
    "PORT": "5001",
    "PROTOCOL": "TCPIP",
    "UID": "db2inst1",
    "PWD": "password"
}


def connect_to_db2():
    """Connect to DB2"""
    dsn = ";".join([f"{k}={v}" for k, v in DB2_CONFIG.items()])
    try:
        conn = ibm_db.connect(dsn, "", "")
        return conn
    except Exception as e:
        print(f"❌ DB2 connection failed: {e}")
        sys.exit(1)


def load_json(path):
    """Load JSON file"""
    with open(path, 'r') as f:
        return json.load(f)


def drop_all_tables(conn, config):
    """Drop all tables for clean test"""
    print("\n🗑️  Dropping existing tables...")
    tables = list(config.get('tables', {}).keys())
    
    # Drop in reverse order (to handle foreign keys)
    for table_name in reversed(tables):
        try:
            ibm_db.exec_immediate(conn, f"DROP TABLE {table_name}")
            print(f"  ✅ Dropped {table_name}")
        except:
            print(f"  ⚠️  {table_name} doesn't exist, skipping")


def clone_schema(conn, config):
    """Clone schema from JSON to DB2"""
    print("\n🔨 Creating tables...")
    
    from clone_oracle_schema import (
        build_create_table_sql,
        build_foreign_key_sql,
        build_index_sql,
        execute_sql
    )
    
    tables = config.get('tables', {})
    
    # Phase 1: Create tables
    for table_name, table_config in tables.items():
        sql = build_create_table_sql(table_name, table_config)
        execute_sql(conn, sql, f"Created table {table_name}")
    
    # Phase 2: Add foreign keys
    for table_name, table_config in tables.items():
        for fk_sql in build_foreign_key_sql(table_name, table_config):
            execute_sql(conn, fk_sql, f"Added FK")
    
    # Phase 3: Create indexes
    for table_name, table_config in tables.items():
        for idx_sql in build_index_sql(table_name, table_config):
            execute_sql(conn, idx_sql, f"Created index")


def format_for_db2(value):
    """Safely format values for literal SQL insertion"""
    if value is None:
        return "NULL"
    if isinstance(value, (int, float, Decimal)):
        return str(value)
    # Escape single quotes for strings
    val_str = str(value).replace("'", "''")
    return f"'{val_str}'"


def transform_value(value, col_config):
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
            if isinstance(value, str):
                return datetime.fromisoformat(value.strip())
            return value
        else:
            return value
    except Exception as e:
        print(f"    ⚠️  Transform error: {e}")
        return None


def load_data(conn, config, sample_data):
    """Load sample data into DB2"""
    print("\n📥 Loading sample data...")
    
    tables = config.get('tables', {})
    total_loaded = 0
    
    for table_name, table_config in tables.items():
        if table_name not in sample_data:
            print(f"  ⚠️  No sample data for {table_name}")
            continue
        
        rows = sample_data[table_name]
        columns = table_config.get('columns', {})
        column_names = list(columns.keys())
        
        loaded = 0
        for row_idx, row in enumerate(rows):
            try:
                # Transform values
                transformed = {}
                for col_name, col_config in columns.items():
                    if col_name in row:
                        value = row[col_name]
                        # Handle None/null values
                        if value is None:
                            transformed[col_name] = None
                        else:
                            transformed[col_name] = transform_value(value, col_config)
                    else:
                        transformed[col_name] = None
                
                # Build INSERT SQL with literal values (bypasses parameter binding issues)
                formatted_values = [format_for_db2(transformed[col]) for col in column_names]
                col_list = ", ".join(column_names)
                val_list = ", ".join(formatted_values)
                sql = f"INSERT INTO {table_name} ({col_list}) VALUES ({val_list})"
                
                # Execute with literal values
                ibm_db.exec_immediate(conn, sql)
                loaded += 1
                
            except Exception as e:
                error_msg = str(e)
                if "duplicate" in error_msg.lower() or "SQL0803N" in error_msg:
                    # Duplicate key, skip
                    continue
                else:
                    print(f"    ⚠️  Insert failed for row {row_idx + 1}: {e}")
        
        print(f"  ✅ {table_name}: Loaded {loaded}/{len(rows)} records")
        total_loaded += loaded
    
    return total_loaded


def verify_data(conn, config, sample_data):
    """Verify data was loaded correctly"""
    print("\n✓ Verifying data...")
    
    tables = config.get('tables', {})
    all_passed = True
    
    for table_name in tables.keys():
        try:
            # Count rows
            sql = f"SELECT COUNT(*) FROM {table_name}"
            stmt = ibm_db.exec_immediate(conn, sql)
            if stmt:
                row = ibm_db.fetch_tuple(stmt)
                actual_count = row[0] if row else 0
                expected_count = len(sample_data.get(table_name, []))
                
                if actual_count == expected_count:
                    print(f"  ✅ {table_name}: {actual_count} rows (expected {expected_count})")
                else:
                    print(f"  ❌ {table_name}: {actual_count} rows (expected {expected_count})")
                    all_passed = False
        except Exception as e:
            print(f"  ❌ {table_name}: Verification failed - {e}")
            all_passed = False
    
    return all_passed


def query_sample_data(conn, config):
    """Query and display sample data from each table"""
    print("\n" + "=" * 60)
    print("SAMPLE DATA VERIFICATION (SELECT Queries)")
    print("=" * 60)
    
    tables = config.get('tables', {})
    
    for table_name in tables.keys():
        try:
            print(f"\n📊 {table_name}:")
            print("-" * 60)
            
            # Get first 3 rows
            sql = f"SELECT * FROM {table_name} FETCH FIRST 3 ROWS ONLY"
            stmt = ibm_db.exec_immediate(conn, sql)
            
            if stmt:
                row_count = 0
                while True:
                    row = ibm_db.fetch_tuple(stmt)
                    if not row:
                        break
                    row_count += 1
                    # Display first few columns
                    display_cols = row[:min(5, len(row))]
                    print(f"  Row {row_count}: {display_cols}")
                
                if row_count == 0:
                    print("  (No data)")
            
        except Exception as e:
            print(f"  ❌ Query failed: {e}")


def main():
    """Main test execution"""
    print("=" * 60)
    print("Complete End-to-End Migration Test")
    print("=" * 60)
    
    # Load configurations
    print(f"\n📋 Loading configuration...")
    config = load_json(CONFIG_PATH)
    sample_data = load_json(SAMPLE_DATA_PATH)
    print(f"✅ Config: {len(config.get('tables', {}))} tables")
    print(f"✅ Sample data: {sum(len(v) for v in sample_data.values())} total records")
    
    # Connect to DB2
    print(f"\n🔌 Connecting to DB2...")
    conn = connect_to_db2()
    print(f"✅ Connected")
    
    try:
        # Step 1: Drop existing tables (clean slate)
        drop_all_tables(conn, config)
        
        # Step 2: Clone schema
        clone_schema(conn, config)
        
        # Step 3: Load data
        total_loaded = load_data(conn, config, sample_data)
        
        # Step 4: Verify counts
        all_passed = verify_data(conn, config, sample_data)
        
        # Step 5: Query sample data
        query_sample_data(conn, config)
        
        # Final result
        print("\n" + "=" * 60)
        if all_passed:
            print("✅ ALL TESTS PASSED!")
            print(f"✅ Successfully migrated {total_loaded} records")
        else:
            print("❌ SOME TESTS FAILED!")
            sys.exit(1)
        print("=" * 60)
        
    finally:
        ibm_db.close(conn)
        print("\n🔌 Connection closed")


if __name__ == "__main__":
    main()

# Made with Bob

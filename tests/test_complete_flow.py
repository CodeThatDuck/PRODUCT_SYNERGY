#!/usr/bin/env python3
"""
Complete End-to-End Migration Flow Test
This test follows the complete migration workflow:
1. Parse Oracle SQL file (already in schema folder)
2. Use JSON mapper to create mapped JSON file
3. Clone schema from JSON to DB2
4. Migrate mock data to DB2

This demonstrates the full Oracle to DB2 migration pipeline.
"""

import json
import sys
import ibm_db  # type: ignore
from pathlib import Path
from decimal import Decimal
from datetime import datetime

# Paths
SCRIPT_DIR = Path(__file__).parent
PROJECT_ROOT = SCRIPT_DIR.parent
CONFIG_PATH = PROJECT_ROOT / "database" / "migrations" / "table_mappings.json"
ORACLE_SCHEMA_PATH = PROJECT_ROOT / "database" / "schemas" / "oracle_source_schema.sql"
SAMPLE_DATA_PATH = SCRIPT_DIR / "sample_oracle_data.json"

# Output paths for generated files
MAPPED_JSON_OUTPUT = SCRIPT_DIR / "mapped_data_output.json"
DB2_SCHEMA_OUTPUT = PROJECT_ROOT / "database" / "schemas" / "db2_generated_schema.sql"

# Add scripts to path
sys.path.insert(0, str(PROJECT_ROOT / "scripts"))

# DB2 Connection
DB2_CONFIG = {
    "DATABASE": "proddb",
    "HOSTNAME": "localhost",
    "PORT": "5000",
    "PROTOCOL": "TCPIP",
    "UID": "db2inst1",
    "PWD": "password"
}


def print_section(title):
    """Print a formatted section header"""
    print("\n" + "=" * 70)
    print(f"  {title}")
    print("=" * 70)


def print_step(step_num, description):
    """Print a formatted step"""
    print(f"\n{'='*70}")
    print(f"STEP {step_num}: {description}")
    print(f"{'='*70}")


def connect_to_db2():
    """Connect to DB2"""
    dsn = ";".join([f"{k}={v}" for k, v in DB2_CONFIG.items()])
    try:
        conn = ibm_db.connect(dsn, "", "")
        if conn is None:
            raise Exception("Connection returned None")
        return conn
    except Exception as e:
        print(f"❌ DB2 connection failed: {e}")
        sys.exit(1)


def load_json(path):
    """Load JSON file"""
    with open(path, 'r') as f:
        return json.load(f)


def save_json(data, path):
    """Save data to JSON file"""
    with open(path, 'w') as f:
        json.dump(data, f, indent=2, default=str)


def step1_verify_oracle_schema():
    """Step 1: Verify Oracle SQL file exists"""
    print_step(1, "Verify Oracle SQL Schema File")
    
    if not ORACLE_SCHEMA_PATH.exists():
        print(f"❌ Oracle schema file not found: {ORACLE_SCHEMA_PATH}")
        return False
    
    print(f"✅ Oracle schema file found: {ORACLE_SCHEMA_PATH}")
    
    # Read and display first few lines
    with open(ORACLE_SCHEMA_PATH, 'r') as f:
        lines = f.readlines()[:10]
    
    print(f"\n📄 First 10 lines of Oracle schema:")
    print("-" * 70)
    for i, line in enumerate(lines, 1):
        print(f"{i:3d} | {line.rstrip()}")
    
    print(f"\n✅ Total lines in Oracle schema: {len(open(ORACLE_SCHEMA_PATH).readlines())}")
    return True


def step2_create_mapped_json():
    """Step 2: Use DataMapper to create mapped JSON file"""
    print_step(2, "Create Mapped JSON File using DataMapper")
    
    from data_mapper import DataMapper  # type: ignore
    
    # Initialize mapper
    print("\n🔧 Initializing DataMapper...")
    mapper = DataMapper(CONFIG_PATH)
    print("✅ DataMapper initialized")
    
    # Load sample data
    print(f"\n📥 Loading sample data from: {SAMPLE_DATA_PATH}")
    sample_data = load_json(SAMPLE_DATA_PATH)
    print(f"✅ Loaded {len(sample_data)} tables with sample data")
    
    # Map all data
    print("\n🔄 Mapping data for all tables...")
    mapped_data = {}
    
    for table_name, rows in sample_data.items():
        print(f"\n  📊 Processing {table_name}...")
        print(f"     Source rows: {len(rows)}")
        
        # Map table data with validation
        mapped_rows = mapper.map_table_data(rows, table_name, validate=True)
        mapped_data[table_name] = mapped_rows
        
        print(f"     Mapped rows: {len(mapped_rows)}")
        
        if mapped_rows:
            print(f"     ✅ Sample mapped row:")
            sample = mapped_rows[0]
            # Show first 3 fields
            for i, (key, value) in enumerate(list(sample.items())[:3]):
                print(f"        {key}: {value} (type: {type(value).__name__})")
    
    # Save mapped data to JSON file
    print(f"\n💾 Saving mapped data to: {MAPPED_JSON_OUTPUT}")
    save_json(mapped_data, MAPPED_JSON_OUTPUT)
    print(f"✅ Mapped JSON file created successfully!")
    
    # Print statistics
    print("\n📊 Mapping Statistics:")
    stats = mapper.get_statistics()
    print(f"   Total rows processed: {stats['total_rows']}")
    print(f"   Successful mappings: {stats['successful_rows']}")
    print(f"   Failed mappings: {stats['failed_rows']}")
    print(f"   Transformations applied: {stats['transformations_applied']}")
    
    if stats['total_rows'] > 0:
        success_rate = (stats['successful_rows'] / stats['total_rows']) * 100
        print(f"   Success rate: {success_rate:.2f}%")
    
    return mapped_data


def step3_clone_schema_to_db2(config):
    """Step 3: Clone schema from JSON to DB2"""
    print_step(3, "Clone Schema from JSON to DB2")
    
    from clone_oracle_schema import (  # type: ignore
        build_create_table_sql,
        build_foreign_key_sql,
        build_index_sql,
        execute_sql,
        generate_db2_sql
    )
    
    # Generate DB2 SQL file
    print(f"\n📝 Generating DB2 SQL schema file...")
    db2_sql = generate_db2_sql(config)
    with open(DB2_SCHEMA_OUTPUT, 'w') as f:
        f.write(db2_sql)
    print(f"✅ DB2 schema file created: {DB2_SCHEMA_OUTPUT}")
    
    # Connect to DB2
    print(f"\n🔌 Connecting to DB2...")
    conn = connect_to_db2()
    print(f"✅ Connected to DB2")
    
    try:
        tables = config.get('tables', {})
        
        # Drop existing tables first (clean slate)
        print("\n🗑️  Dropping existing tables (if any)...")
        for table_name in reversed(list(tables.keys())):
            try:
                ibm_db.exec_immediate(conn, f"DROP TABLE {table_name}")
                print(f"  ✅ Dropped {table_name}")
            except:
                print(f"  ⚠️  {table_name} doesn't exist, skipping")
        
        # Phase 1: Create tables
        print("\n🔨 Phase 1: Creating Tables")
        print("-" * 70)
        for table_name, table_config in tables.items():
            print(f"\n  Creating table: {table_name}")
            sql = build_create_table_sql(table_name, table_config)
            execute_sql(conn, sql, f"Created table {table_name}")
        
        # Phase 2: Add foreign keys
        print("\n🔗 Phase 2: Adding Foreign Keys")
        print("-" * 70)
        for table_name, table_config in tables.items():
            fk_statements = build_foreign_key_sql(table_name, table_config)
            if fk_statements:
                print(f"\n  Adding foreign keys for: {table_name}")
                for sql in fk_statements:
                    execute_sql(conn, sql, f"Added foreign key")
        
        # Phase 3: Create indexes
        print("\n📇 Phase 3: Creating Indexes")
        print("-" * 70)
        for table_name, table_config in tables.items():
            index_statements = build_index_sql(table_name, table_config)
            if index_statements:
                print(f"\n  Creating indexes for: {table_name}")
                for sql in index_statements:
                    execute_sql(conn, sql, f"Created index")
        
        print("\n✅ Schema cloning completed successfully!")
        return conn
        
    except Exception as e:
        print(f"\n❌ Schema cloning failed: {e}")
        ibm_db.close(conn)
        raise


def format_for_db2(value):
    """Safely format values for literal SQL insertion"""
    if value is None:
        return "NULL"
    if isinstance(value, (int, float, Decimal)):
        return str(value)
    # Escape single quotes for strings
    val_str = str(value).replace("'", "''")
    return f"'{val_str}'"


def step4_migrate_mock_data(conn, config, mapped_data):
    """Step 4: Migrate mock data to DB2"""
    print_step(4, "Migrate Mock Data to DB2")
    
    tables = config.get('tables', {})
    total_loaded = 0
    
    print("\n📥 Loading mapped data into DB2 tables...")
    
    for table_name, table_config in tables.items():
        if table_name not in mapped_data:
            print(f"\n  ⚠️  No mapped data for {table_name}")
            continue
        
        rows = mapped_data[table_name]
        columns = table_config.get('columns', {})
        column_names = list(columns.keys())
        
        print(f"\n  📊 Loading {table_name}...")
        print(f"     Rows to insert: {len(rows)}")
        
        loaded = 0
        for row_idx, row in enumerate(rows):
            try:
                # Build INSERT SQL with literal values
                formatted_values = [format_for_db2(row.get(col)) for col in column_names]
                col_list = ", ".join(column_names)
                val_list = ", ".join(formatted_values)
                sql = f"INSERT INTO {table_name} ({col_list}) VALUES ({val_list})"
                
                # Execute
                ibm_db.exec_immediate(conn, sql)
                loaded += 1
                
            except Exception as e:
                error_msg = str(e)
                if "duplicate" in error_msg.lower() or "SQL0803N" in error_msg:
                    # Duplicate key, skip
                    continue
                else:
                    print(f"     ⚠️  Insert failed for row {row_idx + 1}: {e}")
        
        print(f"     ✅ Loaded {loaded}/{len(rows)} records")
        total_loaded += loaded
    
    print(f"\n✅ Total records migrated: {total_loaded}")
    return total_loaded


def step5_verify_migration(conn, config, mapped_data):
    """Step 5: Verify data migration"""
    print_step(5, "Verify Data Migration")
    
    tables = config.get('tables', {})
    all_passed = True
    
    print("\n🔍 Verifying row counts...")
    for table_name in tables.keys():
        try:
            # Count rows
            sql = f"SELECT COUNT(*) FROM {table_name}"
            stmt = ibm_db.exec_immediate(conn, sql)
            if stmt and stmt is not True:
                row = ibm_db.fetch_tuple(stmt)
                actual_count = row[0] if row else 0
                expected_count = len(mapped_data.get(table_name, []))
                
                if actual_count == expected_count:
                    print(f"  ✅ {table_name}: {actual_count} rows (expected {expected_count})")
                else:
                    print(f"  ❌ {table_name}: {actual_count} rows (expected {expected_count})")
                    all_passed = False
        except Exception as e:
            print(f"  ❌ {table_name}: Verification failed - {e}")
            all_passed = False
    
    return all_passed


def step6_query_sample_data(conn, config):
    """Step 6: Query and display sample data"""
    print_step(6, "Query Sample Data from DB2")
    
    tables = config.get('tables', {})
    
    for table_name in tables.keys():
        try:
            print(f"\n📊 {table_name}:")
            print("-" * 70)
            
            # Get first 3 rows
            sql = f"SELECT * FROM {table_name} FETCH FIRST 3 ROWS ONLY"
            stmt = ibm_db.exec_immediate(conn, sql)
            
            if stmt and stmt is not True:
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
    print("=" * 70)
    print("  COMPLETE END-TO-END MIGRATION FLOW TEST")
    print("  Oracle SQL → JSON Mapping → DB2 Schema → Data Migration")
    print("=" * 70)
    
    try:
        # Step 1: Verify Oracle schema file
        if not step1_verify_oracle_schema():
            print("\n❌ Step 1 failed!")
            sys.exit(1)
        
        # Step 2: Create mapped JSON file
        mapped_data = step2_create_mapped_json()
        if not mapped_data:
            print("\n❌ Step 2 failed!")
            sys.exit(1)
        
        # Load configuration
        print(f"\n📋 Loading table configuration...")
        config = load_json(CONFIG_PATH)
        print(f"✅ Loaded {len(config.get('tables', {}))} table definitions")
        
        # Step 3: Clone schema to DB2
        conn = step3_clone_schema_to_db2(config)
        
        # Step 4: Migrate mock data
        total_loaded = step4_migrate_mock_data(conn, config, mapped_data)
        
        # Step 5: Verify migration
        all_passed = step5_verify_migration(conn, config, mapped_data)
        
        # Step 6: Query sample data
        step6_query_sample_data(conn, config)
        
        # Final summary
        print_section("FINAL SUMMARY")
        print(f"\n✅ Oracle Schema File: {ORACLE_SCHEMA_PATH}")
        print(f"✅ Mapped JSON File Created: {MAPPED_JSON_OUTPUT}")
        print(f"✅ DB2 Schema File Created: {DB2_SCHEMA_OUTPUT}")
        print(f"✅ DB2 Tables Created: {len(config.get('tables', {}))}")
        print(f"✅ Records Migrated: {total_loaded}")
        
        if all_passed:
            print("\n" + "=" * 70)
            print("  ✅ ALL TESTS PASSED!")
            print("  ✅ Complete migration flow successful!")
            print("=" * 70)
        else:
            print("\n" + "=" * 70)
            print("  ⚠️  SOME VERIFICATIONS FAILED!")
            print("=" * 70)
            sys.exit(1)
        
        # Close connection
        ibm_db.close(conn)
        print("\n🔌 DB2 connection closed")
        
    except Exception as e:
        print(f"\n❌ TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()

# Made with Bob
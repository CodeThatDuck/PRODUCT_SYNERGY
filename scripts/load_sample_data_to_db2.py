#!/usr/bin/env python3
"""
Load Sample Oracle Data into DB2
Reads sample_oracle_data.json and inserts into DB2 tables
"""

import json
import sys
import ibm_db
from pathlib import Path
from datetime import datetime

# Paths
SCRIPT_DIR = Path(__file__).parent
PROJECT_ROOT = SCRIPT_DIR.parent
DATA_FILE = PROJECT_ROOT / "tests" / "sample_oracle_data.json"

# DB2 Connection Configuration
DB2_CONFIG = {
    "DATABASE": "proddb",
    "HOSTNAME": "localhost",
    "PORT": "5001",
    "PROTOCOL": "TCPIP",
    "UID": "db2inst1",
    "PWD": "password"
}

def connect_to_db2():
    """Connect to DB2 database"""
    dsn = ";".join([f"{k}={v}" for k, v in DB2_CONFIG.items()])
    try:
        conn = ibm_db.connect(dsn, "", "")
        print("✓ Connected to DB2")
        return conn
    except Exception as e:
        print(f"❌ Failed to connect to DB2: {e}")
        sys.exit(1)

def load_sample_data():
    """Load sample data from JSON file"""
    try:
        with open(DATA_FILE, 'r') as f:
            data = json.load(f)
        print(f"✓ Loaded sample data from {DATA_FILE}")
        return data
    except FileNotFoundError:
        print(f"❌ Data file not found: {DATA_FILE}")
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"❌ Invalid JSON: {e}")
        sys.exit(1)

def clear_tables(conn):
    """Clear all tables before inserting new data"""
    tables = [
        "ORDER_ITEMS",
        "ORDERS", 
        "SYNERGIES",
        "CUSTOMERS",
        "PRODUCTS",
        "DATATYPE_TEST",
        "ORACLE_DATATYPE_COMPREHENSIVE"
    ]
    
    print("\nClearing existing data...")
    for table in tables:
        try:
            sql = f"DELETE FROM {table}"
            stmt = ibm_db.exec_immediate(conn, sql)
            print(f"  ✓ Cleared {table}")
        except Exception as e:
            print(f"  ⚠ Warning clearing {table}: {e}")

def insert_data(conn, table_name, records):
    """Insert records into a table"""
    if not records:
        print(f"  ⚠ No data for {table_name}")
        return
    
    # Get column names from first record
    columns = list(records[0].keys())
    placeholders = ", ".join(["?" for _ in columns])
    column_names = ", ".join(columns)
    
    sql = f"INSERT INTO {table_name} ({column_names}) VALUES ({placeholders})"
    
    inserted = 0
    failed = 0
    
    for record in records:
        try:
            stmt = ibm_db.prepare(conn, sql)
            if not stmt:
                failed += 1
                continue
            
            # Bind parameters
            for i, col in enumerate(columns, 1):
                value = record[col]
                
                # Handle None/NULL values
                if value is None:
                    ibm_db.bind_param(stmt, i, "")  # Use empty string for NULL
                else:
                    # Convert to string for binding
                    ibm_db.bind_param(stmt, i, str(value))
            
            ibm_db.execute(stmt)
            inserted += 1
            
        except Exception as e:
            failed += 1
            print(f"    ⚠ Failed to insert record: {e}")
    
    print(f"  ✓ {table_name}: Inserted {inserted} records" + 
          (f" ({failed} failed)" if failed > 0 else ""))

def main():
    print("=" * 60)
    print("Load Sample Oracle Data into DB2")
    print("=" * 60)
    
    # Connect to DB2
    conn = connect_to_db2()
    
    # Load sample data
    data = load_sample_data()
    
    # Clear existing data
    clear_tables(conn)
    
    # Insert data in correct order (respecting foreign keys)
    print("\nInserting data...")
    
    # Tables without foreign keys first
    insert_data(conn, "PRODUCTS", data.get("PRODUCTS", []))
    insert_data(conn, "CUSTOMERS", data.get("CUSTOMERS", []))
    insert_data(conn, "DATATYPE_TEST", data.get("DATATYPE_TEST", []))
    insert_data(conn, "ORACLE_DATATYPE_COMPREHENSIVE", 
                data.get("ORACLE_DATATYPE_COMPREHENSIVE", []))
    
    # Tables with foreign keys
    insert_data(conn, "ORDERS", data.get("ORDERS", []))
    insert_data(conn, "ORDER_ITEMS", data.get("ORDER_ITEMS", []))
    insert_data(conn, "SYNERGIES", data.get("SYNERGIES", []))
    
    # Verify data
    print("\nVerifying data...")
    for table_name in ["PRODUCTS", "CUSTOMERS", "ORDERS", "ORDER_ITEMS", "SYNERGIES"]:
        try:
            sql = f"SELECT COUNT(*) FROM {table_name}"
            stmt = ibm_db.exec_immediate(conn, sql)
            result = ibm_db.fetch_tuple(stmt)
            count = result[0] if result else 0
            print(f"  {table_name}: {count} records")
        except Exception as e:
            print(f"  ⚠ Error checking {table_name}: {e}")
    
    # Close connection
    ibm_db.close(conn)
    
    print("\n" + "=" * 60)
    print("✓ Data loading complete!")
    print("=" * 60)

if __name__ == "__main__":
    main()

# Made with Bob

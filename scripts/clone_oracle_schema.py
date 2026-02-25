#!/usr/bin/env python3
"""
Oracle to DB2 Schema Cloner
Reads JSON configuration and creates DB2 tables dynamically
No hardcoded schemas - purely JSON-driven
"""

import json
import sys
import ibm_db
from pathlib import Path
from typing import Dict, List, Any

# Paths
SCRIPT_DIR = Path(__file__).parent
PROJECT_ROOT = SCRIPT_DIR.parent
CONFIG_PATH = PROJECT_ROOT / "database" / "migrations" / "table_mappings.json"
ORACLE_SCHEMA_PATH = PROJECT_ROOT / "database" / "schemas" / "oracle_source_schema.sql"
DB2_SCHEMA_PATH = PROJECT_ROOT / "database" / "schemas" / "db2_target_schema.sql"

# DB2 Connection Configuration
DB2_CONFIG = {
    "DATABASE": "proddb",
    "HOSTNAME": "localhost",
    "PORT": "5001",
    "PROTOCOL": "TCPIP",
    "UID": "db2inst1",
    "PWD": "password"
}


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


def build_create_table_sql(table_name: str, table_config: Dict) -> str:
    """Build CREATE TABLE SQL from JSON configuration"""
    columns = table_config.get('columns', {})
    primary_key = table_config.get('primary_key')
    
    # Build column definitions
    col_defs = []
    for col_name, col_config in columns.items():
        db2_type = col_config.get('db2_type', 'VARCHAR(255)')
        nullable = col_config.get('nullable', True)
        null_clause = "" if nullable else " NOT NULL"
        col_defs.append(f"    {col_name} {db2_type}{null_clause}")
    
    # Add primary key constraint
    if primary_key:
        col_defs.append(f"    CONSTRAINT PK_{table_name} PRIMARY KEY ({primary_key})")
    
    # Build CREATE TABLE statement
    sql = f"CREATE TABLE {table_name} (\n"
    sql += ",\n".join(col_defs)
    sql += "\n)"
    
    return sql


def build_foreign_key_sql(table_name: str, table_config: Dict) -> List[str]:
    """Build ALTER TABLE statements for foreign keys"""
    foreign_keys = table_config.get('foreign_keys', {})
    fk_statements = []
    
    for fk_col, ref_table_col in foreign_keys.items():
        ref_table, ref_col = ref_table_col.split('.')
        sql = f"""ALTER TABLE {table_name}
    ADD CONSTRAINT FK_{table_name}_{fk_col}
    FOREIGN KEY ({fk_col})
    REFERENCES {ref_table}({ref_col})"""
        fk_statements.append(sql)
    
    return fk_statements


def build_index_sql(table_name: str, table_config: Dict) -> List[str]:
    """Build CREATE INDEX statements"""
    foreign_keys = table_config.get('foreign_keys', {})
    index_statements = []
    
    for fk_col in foreign_keys.keys():
        sql = f"CREATE INDEX IDX_{table_name}_{fk_col} ON {table_name}({fk_col})"
        index_statements.append(sql)
    
    return index_statements


def build_comment_sql(table_name: str, table_config: Dict) -> List[str]:
    """Build COMMENT statements"""
    comment_statements = []
    
    # Table comment
    description = table_config.get('description', 'No description')
    comment_statements.append(f"COMMENT ON TABLE {table_name} IS '{description}'")
    
    # Column comments
    columns = table_config.get('columns', {})
    for col_name, col_config in columns.items():
        notes = col_config.get('notes', f'{col_name} column')
        comment_statements.append(f"COMMENT ON COLUMN {table_name}.{col_name} IS '{notes}'")
    
    return comment_statements


def execute_sql(conn: Any, sql: str, description: str) -> bool:
    """Execute SQL statement with error handling"""
    try:
        ibm_db.exec_immediate(conn, sql)
        print(f"  ✅ {description}")
        return True
    except Exception as e:
        error_msg = str(e)
        if "SQL0601N" in error_msg or "already exists" in error_msg.lower():
            print(f"  ⚠️  {description} - Already exists, skipping")
            return True
        else:
            print(f"  ❌ {description} - Failed: {error_msg}")
            return False


def clone_schema(config: Dict, conn: Any):
    """Clone Oracle schema to DB2 based on JSON configuration"""
    tables = config.get('tables', {})
    
    print(f"\n📋 Found {len(tables)} tables to create\n")
    
    # Phase 1: Create tables
    print("=" * 60)
    print("PHASE 1: Creating Tables")
    print("=" * 60)
    for table_name, table_config in tables.items():
        print(f"\n🔨 Creating table: {table_name}")
        sql = build_create_table_sql(table_name, table_config)
        execute_sql(conn, sql, f"Created table {table_name}")
    
    # Phase 2: Add foreign keys
    print("\n" + "=" * 60)
    print("PHASE 2: Adding Foreign Keys")
    print("=" * 60)
    for table_name, table_config in tables.items():
        fk_statements = build_foreign_key_sql(table_name, table_config)
        if fk_statements:
            print(f"\n🔗 Adding foreign keys for: {table_name}")
            for sql in fk_statements:
                execute_sql(conn, sql, f"Added foreign key")
    
    # Phase 3: Create indexes
    print("\n" + "=" * 60)
    print("PHASE 3: Creating Indexes")
    print("=" * 60)
    for table_name, table_config in tables.items():
        index_statements = build_index_sql(table_name, table_config)
        if index_statements:
            print(f"\n📇 Creating indexes for: {table_name}")
            for sql in index_statements:
                execute_sql(conn, sql, f"Created index")
    
    # Phase 4: Add comments
    print("\n" + "=" * 60)
    print("PHASE 4: Adding Comments")
    print("=" * 60)
    for table_name, table_config in tables.items():
        comment_statements = build_comment_sql(table_name, table_config)
        if comment_statements:
            print(f"\n💬 Adding comments for: {table_name}")
            for sql in comment_statements:
                execute_sql(conn, sql, f"Added comment")


def verify_tables(config: Dict, conn: Any):
    """Verify created tables"""
    print("\n" + "=" * 60)
    print("VERIFICATION: Checking Created Tables")
    print("=" * 60)
    
    tables = config.get('tables', {})
    for table_name in tables.keys():
        try:
            sql = f"SELECT COUNT(*) FROM {table_name}"
            stmt = ibm_db.exec_immediate(conn, sql)
            row = ibm_db.fetch_tuple(stmt)
            count = row[0] if row else 0
            print(f"  ✅ {table_name}: {count} rows")
        except Exception as e:
            print(f"  ❌ {table_name}: Not found or error - {e}")


def generate_oracle_sql(config: Dict) -> str:
    """Generate Oracle SQL schema from JSON"""
    lines = []
    lines.append("-- " + "=" * 60)
    lines.append("-- ORACLE SOURCE SCHEMA")
    lines.append("-- Auto-generated from table_mappings.json")
    lines.append("-- " + "=" * 60)
    lines.append("")
    
    tables = config.get('tables', {})
    for table_name, table_config in tables.items():
        sql = build_create_table_sql(table_name, table_config)
        # Replace DB2 types with Oracle types
        for col_name, col_config in table_config.get('columns', {}).items():
            oracle_type = col_config.get('oracle_type', 'VARCHAR2(255)')
            db2_type = col_config.get('db2_type', 'VARCHAR(255)')
            sql = sql.replace(f" {db2_type}", f" {oracle_type}")
        
        lines.append(f"-- Table: {table_name}")
        lines.append(sql + ";")
        lines.append("")
        
        # Add foreign keys
        for fk_sql in build_foreign_key_sql(table_name, table_config):
            lines.append(fk_sql + ";")
            lines.append("")
        
        # Add indexes
        for idx_sql in build_index_sql(table_name, table_config):
            lines.append(idx_sql + ";")
        lines.append("")
    
    return "\n".join(lines)


def generate_db2_sql(config: Dict) -> str:
    """Generate DB2 SQL schema from JSON"""
    lines = []
    lines.append("-- " + "=" * 60)
    lines.append("-- DB2 TARGET SCHEMA")
    lines.append("-- Auto-generated from table_mappings.json")
    lines.append("-- " + "=" * 60)
    lines.append("")
    
    tables = config.get('tables', {})
    for table_name, table_config in tables.items():
        lines.append(f"-- Table: {table_name}")
        lines.append(build_create_table_sql(table_name, table_config) + ";")
        lines.append("")
        
        # Add foreign keys
        for fk_sql in build_foreign_key_sql(table_name, table_config):
            lines.append(fk_sql + ";")
            lines.append("")
        
        # Add indexes
        for idx_sql in build_index_sql(table_name, table_config):
            lines.append(idx_sql + ";")
        lines.append("")
    
    return "\n".join(lines)


def save_sql_files(config: Dict):
    """Generate and save SQL schema files"""
    print("\n" + "=" * 60)
    print("GENERATING SQL FILES")
    print("=" * 60)
    
    # Generate Oracle SQL
    print(f"\n📝 Generating Oracle schema...")
    oracle_sql = generate_oracle_sql(config)
    with open(ORACLE_SCHEMA_PATH, 'w') as f:
        f.write(oracle_sql)
    print(f"✅ Saved: {ORACLE_SCHEMA_PATH}")
    
    # Generate DB2 SQL
    print(f"\n📝 Generating DB2 schema...")
    db2_sql = generate_db2_sql(config)
    with open(DB2_SCHEMA_PATH, 'w') as f:
        f.write(db2_sql)
    print(f"✅ Saved: {DB2_SCHEMA_PATH}")


def main():
    """Main execution"""
    print("=" * 60)
    print("Oracle to DB2 Schema Cloner")
    print("JSON-Driven Schema Creation")
    print("=" * 60)
    
    # Load configuration
    print(f"\n📋 Loading configuration: {CONFIG_PATH}")
    config = load_json_config(CONFIG_PATH)
    print(f"✅ Loaded {len(config.get('tables', {}))} table definitions")
    
    # Generate SQL files
    save_sql_files(config)
    
    # Connect to DB2
    print("\n🔌 Connecting to DB2...")
    conn = connect_to_db2()
    
    try:
        # Clone schema
        clone_schema(config, conn)
        
        # Verify
        verify_tables(config, conn)
        
        print("\n" + "=" * 60)
        print("✅ Schema cloning completed successfully!")
        print("=" * 60)
        
    finally:
        ibm_db.close(conn)
        print("\n🔌 Connection closed")


if __name__ == "__main__":
    main()

# Made with Bob

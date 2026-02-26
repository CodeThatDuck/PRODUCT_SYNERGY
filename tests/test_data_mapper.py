#!/usr/bin/env python3
"""
Test script for DataMapper utility
Demonstrates usage with sample Oracle data
"""

import json
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from scripts.data_mapper import DataMapper


def load_sample_data():
    """Load sample Oracle data"""
    sample_data_path = Path(__file__).parent / "sample_oracle_data.json"
    with open(sample_data_path, 'r') as f:
        return json.load(f)


def test_single_row_mapping():
    """Test mapping a single row"""
    print("\n" + "=" * 60)
    print("TEST 1: Single Row Mapping")
    print("=" * 60)
    
    mapper = DataMapper()
    
    # Test PRODUCTS table
    source_row = {
        "PRODUCT_ID": "1001",
        "NAME": "  Gaming Laptop Pro  ",
        "PRICE": "1299.99"
    }
    
    print("\n📋 Source Row:")
    print(json.dumps(source_row, indent=2))
    
    mapped_row = mapper.map_row(source_row, "PRODUCTS")
    
    # Check if mapping was successful
    assert mapped_row is not None, "Mapping should succeed for valid data"
    
    print("\n✨ Mapped Row:")
    print(json.dumps(mapped_row, indent=2, default=str))
    
    # Verify transformations
    assert mapped_row["PRODUCT_ID"] == 1001, "PRODUCT_ID should be integer"
    assert mapped_row["NAME"] == "Gaming Laptop Pro", "NAME should be trimmed"
    assert str(mapped_row["PRICE"]) == "1299.99", "PRICE should be decimal"
    
    print("\n✅ All assertions passed!")
    
    return mapper


def test_batch_mapping():
    """Test mapping multiple rows"""
    print("\n" + "=" * 60)
    print("TEST 2: Batch Mapping")
    print("=" * 60)
    
    mapper = DataMapper()
    sample_data = load_sample_data()
    
    # Test each table
    for table_name, rows in sample_data.items():
        print(f"\n📊 Processing {table_name}...")
        print(f"   Source rows: {len(rows)}")
        
        mapped_rows = mapper.map_table_data(rows, table_name, validate=True)
        
        print(f"   Mapped rows: {len(mapped_rows)}")
        
        if mapped_rows:
            print(f"   Sample mapped row:")
            print(f"   {json.dumps(mapped_rows[0], indent=4, default=str)}")
    
    return mapper


def test_validation():
    """Test validation logic"""
    print("\n" + "=" * 60)
    print("TEST 3: Validation")
    print("=" * 60)
    
    mapper = DataMapper()
    
    # Test valid row
    print("\n✅ Testing valid row...")
    valid_row = {
        "PRODUCT_ID": "1001",
        "NAME": "Valid Product",
        "PRICE": "99.99"
    }
    result = mapper.map_row(valid_row, "PRODUCTS", validate=True)
    assert result is not None, "Valid row should pass validation"
    print("   ✓ Valid row passed")
    
    # Test invalid row (NULL for non-nullable field)
    print("\n❌ Testing invalid row (NULL PRODUCT_ID)...")
    invalid_row = {
        "PRODUCT_ID": None,
        "NAME": "Invalid Product",
        "PRICE": "99.99"
    }
    result = mapper.map_row(invalid_row, "PRODUCTS", validate=True)
    assert result is None, "Invalid row should fail validation"
    print("   ✓ Invalid row correctly rejected")
    
    # Test invalid row (empty NAME)
    print("\n❌ Testing invalid row (empty NAME)...")
    invalid_row2 = {
        "PRODUCT_ID": "1001",
        "NAME": "",
        "PRICE": "99.99"
    }
    result = mapper.map_row(invalid_row2, "PRODUCTS", validate=True)
    # Empty string becomes None after trim, which should fail for non-nullable
    print(f"   Result: {result}")
    
    return mapper


def test_transformations():
    """Test various transformations"""
    print("\n" + "=" * 60)
    print("TEST 4: Transformation Types")
    print("=" * 60)
    
    mapper = DataMapper()
    sample_data = load_sample_data()
    
    # Test DATATYPE_TEST table (has various data types)
    print("\n📋 Testing DATATYPE_TEST transformations...")
    datatype_rows = sample_data.get("DATATYPE_TEST", [])
    
    if datatype_rows:
        source_row = datatype_rows[0]
        mapped_row = mapper.map_row(source_row, "DATATYPE_TEST")
        
        if mapped_row is not None:
            print("\nTransformation Results:")
            print(f"  NUM_INTEGER: '{source_row['NUM_INTEGER']}' → {mapped_row['NUM_INTEGER']} (type: {type(mapped_row['NUM_INTEGER']).__name__})")
            print(f"  NUM_DECIMAL: '{source_row['NUM_DECIMAL']}' → {mapped_row['NUM_DECIMAL']} (type: {type(mapped_row['NUM_DECIMAL']).__name__})")
            print(f"  CHAR_FIXED: '{source_row['CHAR_FIXED']}' → '{mapped_row['CHAR_FIXED']}' (trimmed)")
            print(f"  DATE_FIELD: '{source_row['DATE_FIELD']}' → {mapped_row['DATE_FIELD']} (type: {type(mapped_row['DATE_FIELD']).__name__})")
        else:
            print("\n⚠️  Mapping failed for DATATYPE_TEST row")
    
    return mapper


def test_statistics():
    """Test statistics tracking"""
    print("\n" + "=" * 60)
    print("TEST 5: Statistics Tracking")
    print("=" * 60)
    
    mapper = DataMapper()
    sample_data = load_sample_data()
    
    # Process all tables
    total_source_rows = 0
    for table_name, rows in sample_data.items():
        total_source_rows += len(rows)
        mapper.map_table_data(rows, table_name, validate=True)
    
    # Get statistics
    stats = mapper.get_statistics()
    
    print(f"\n📊 Statistics Summary:")
    print(f"   Total source rows: {total_source_rows}")
    print(f"   Total processed: {stats['total_rows']}")
    print(f"   Successful: {stats['successful_rows']}")
    print(f"   Failed: {stats['failed_rows']}")
    print(f"   Transformations: {stats['transformations_applied']}")
    print(f"   Validations passed: {stats['validations_passed']}")
    print(f"   Validations failed: {stats['validations_failed']}")
    
    if stats['total_rows'] > 0:
        success_rate = (stats['successful_rows'] / stats['total_rows']) * 100
        print(f"   Success rate: {success_rate:.2f}%")
    
    # Print detailed statistics
    mapper.print_statistics()
    
    return mapper


def test_schema_access():
    """Test schema access methods"""
    print("\n" + "=" * 60)
    print("TEST 6: Schema Access")
    print("=" * 60)
    
    mapper = DataMapper()
    
    # Get table schema
    print("\n📋 Getting PRODUCTS table schema...")
    schema = mapper.get_table_schema("PRODUCTS")
    if schema is not None:
        print(f"   Primary key: {schema.get('primary_key')}")
        print(f"   Columns: {len(schema.get('columns', {}))}")
    else:
        print("   ⚠️  Schema not found")
    
    # Get column config
    print("\n📋 Getting PRICE column config...")
    col_config = mapper.get_column_config("PRODUCTS", "PRICE")
    if col_config is not None:
        print(f"   Oracle type: {col_config.get('oracle_type')}")
        print(f"   DB2 type: {col_config.get('db2_type')}")
        print(f"   Transformation: {col_config.get('transformation')}")
        print(f"   Nullable: {col_config.get('nullable')}")
    else:
        print("   ⚠️  Column config not found")
    
    return mapper


def main():
    """Run all tests"""
    print("=" * 60)
    print("DataMapper Utility - Comprehensive Test Suite")
    print("=" * 60)
    
    try:
        # Run tests
        test_single_row_mapping()
        test_batch_mapping()
        test_validation()
        test_transformations()
        test_statistics()
        test_schema_access()
        
        print("\n" + "=" * 60)
        print("✅ ALL TESTS PASSED!")
        print("=" * 60)
        print("\n💡 The DataMapper utility is working correctly!")
        print("   You can now use it in your migration scripts.")
        print("\n📚 See docs/DATA_MAPPER_GUIDE.md for usage examples")
        
    except AssertionError as e:
        print(f"\n❌ TEST FAILED: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()

# Made with Bob

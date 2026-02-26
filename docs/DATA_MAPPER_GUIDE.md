# 📘 Data Mapper Utility Guide

## Overview

The **Data Mapper** is an advanced utility for Oracle to DB2 data migration that provides comprehensive field mapping, transformation, and validation capabilities. It complements the existing migration scripts by offering a reusable, extensible mapping framework.

## Features

- ✅ **13 Built-in Transformations** - String, numeric, date, and specialized transformations
- ✅ **9 Validation Types** - Comprehensive data quality checks
- ✅ **Statistics Tracking** - Monitor transformation and validation success rates
- ✅ **Extensible Architecture** - Easy to add custom transformations and validations
- ✅ **JSON-Driven Configuration** - Uses existing `table_mappings.json`
- ✅ **Type-Safe Conversions** - Handles edge cases and null values gracefully

---

## Quick Start

### Basic Usage

```python
from scripts.data_mapper import DataMapper

# Initialize the mapper
mapper = DataMapper()

# Map a single row
source_row = {
    "PRODUCT_ID": "1001",
    "NAME": "  Gaming Laptop  ",
    "PRICE": "1299.99"
}

mapped_row = mapper.map_row(source_row, "PRODUCTS")
print(mapped_row)
# Output: {'PRODUCT_ID': 1001, 'NAME': 'Gaming Laptop', 'PRICE': Decimal('1299.99')}
```

### Batch Processing

```python
# Map multiple rows
source_rows = [
    {"PRODUCT_ID": "1001", "NAME": "Product 1", "PRICE": "99.99"},
    {"PRODUCT_ID": "1002", "NAME": "Product 2", "PRICE": "149.99"}
]

mapped_rows = mapper.map_table_data(source_rows, "PRODUCTS")
print(f"Mapped {len(mapped_rows)} rows")
```

### View Statistics

```python
# Get mapping statistics
stats = mapper.get_statistics()
print(f"Success rate: {stats['successful_rows'] / stats['total_rows'] * 100}%")

# Or print formatted statistics
mapper.print_statistics()
```

---

## Available Transformations

### Numeric Transformations

#### `string_to_integer`
Converts string to integer, handles whitespace and null values.

```python
# Configuration in table_mappings.json
"PRODUCT_ID": {
    "oracle_type": "NUMBER(10)",
    "db2_type": "DECIMAL(10,0)",
    "transformation": "string_to_integer"
}

# Examples:
"1001"      → 1001
"  42  "    → 42
""          → None
null        → None
```

#### `string_to_decimal`
Converts string to Decimal with precision and scale handling.

```python
"PRICE": {
    "oracle_type": "NUMBER(10,2)",
    "db2_type": "DECIMAL(10,2)",
    "transformation": "string_to_decimal",
    "validation": {
        "scale": 2
    }
}

# Examples:
"99.99"     → Decimal('99.99')
"100"       → Decimal('100.00')
"1.999"     → Decimal('2.00')  # Rounded to scale
```

### String Transformations

#### `trim_string`
Removes leading and trailing whitespace.

```python
"NAME": {
    "transformation": "trim_string"
}

# Examples:
"  Product  "  → "Product"
"Test"         → "Test"
""             → None
```

#### `uppercase`
Converts string to uppercase.

```python
"CODE": {
    "transformation": "uppercase"
}

# Examples:
"product"  → "PRODUCT"
"Test123"  → "TEST123"
```

#### `lowercase`
Converts string to lowercase.

```python
"EMAIL": {
    "transformation": "lowercase"
}

# Examples:
"USER@EXAMPLE.COM"  → "user@example.com"
```

#### `remove_special_chars`
Removes all special characters, keeping only alphanumeric and spaces.

```python
"CLEAN_TEXT": {
    "transformation": "remove_special_chars"
}

# Examples:
"Hello, World!"     → "Hello World"
"Test@123#"         → "Test123"
```

#### `pad_string`
Pads string to specified length with spaces.

```python
"CODE": {
    "transformation": "pad_string",
    "validation": {
        "max_length": 10
    }
}

# Examples:
"ABC"  → "ABC       "  (padded to 10 chars)
```

#### `truncate_string`
Truncates string to maximum length.

```python
"DESCRIPTION": {
    "transformation": "truncate_string",
    "validation": {
        "max_length": 50
    }
}

# Examples:
"Very long description..."  → "Very long description..." (first 50 chars)
```

### Date/Time Transformations

#### `string_to_timestamp`
Converts string to datetime, supports multiple formats.

```python
"CREATED_DATE": {
    "oracle_type": "DATE",
    "db2_type": "TIMESTAMP",
    "transformation": "string_to_timestamp"
}

# Supported formats:
"2024-01-15"              → datetime(2024, 1, 15, 0, 0, 0)
"2024-01-15T10:30:00"     → datetime(2024, 1, 15, 10, 30, 0)
"2024/01/15"              → datetime(2024, 1, 15, 0, 0, 0)
"15-01-2024"              → datetime(2024, 1, 15, 0, 0, 0)
"01/15/2024"              → datetime(2024, 1, 15, 0, 0, 0)
```

### Specialized Transformations

#### `normalize_phone`
Extracts digits from phone number.

```python
"PHONE": {
    "transformation": "normalize_phone"
}

# Examples:
"(555) 123-4567"  → "5551234567"
"+1-555-123-4567" → "15551234567"
```

#### `normalize_email`
Normalizes email to lowercase and validates format.

```python
"EMAIL": {
    "transformation": "normalize_email"
}

# Examples:
"User@Example.COM"  → "user@example.com"
"  test@test.com "  → "test@test.com"
```

#### `string_to_boolean`
Converts string to boolean.

```python
"IS_ACTIVE": {
    "transformation": "string_to_boolean"
}

# Examples:
"true", "1", "yes", "y", "t"   → True
"false", "0", "no", "n", "f"   → False
```

#### `pass_through`
No transformation, passes value as-is.

```python
"BLOB_DATA": {
    "transformation": "pass_through"
}
```

---

## Available Validations

### Numeric Validations

#### `integer`
Validates integer values with optional min/max.

```json
{
    "validation": {
        "type": "integer",
        "min": 1,
        "max": 9999999999
    }
}
```

#### `decimal`
Validates decimal values with precision, scale, and range.

```json
{
    "validation": {
        "type": "decimal",
        "precision": 10,
        "scale": 2,
        "min": 0,
        "max": 99999999.99
    }
}
```

### String Validations

#### `string`
Validates string length and pattern.

```json
{
    "validation": {
        "type": "string",
        "max_length": 255,
        "allow_empty": false,
        "pattern": "^[A-Z][a-z]+"
    }
}
```

#### `email`
Validates email format.

```json
{
    "validation": {
        "type": "email"
    }
}
```

#### `phone`
Validates phone number length.

```json
{
    "validation": {
        "type": "phone",
        "min_length": 10,
        "max_length": 15
    }
}
```

#### `url`
Validates URL format.

```json
{
    "validation": {
        "type": "url"
    }
}
```

### Date/Time Validations

#### `timestamp`
Validates timestamp with optional date range.

```json
{
    "validation": {
        "type": "timestamp",
        "min_date": "2020-01-01",
        "max_date": "2030-12-31"
    }
}
```

### Other Validations

#### `binary`
Validates binary data (bytes/bytearray).

```json
{
    "validation": {
        "type": "binary"
    }
}
```

#### `range`
Validates numeric value is within range.

```json
{
    "validation": {
        "type": "range",
        "min": 0,
        "max": 100
    }
}
```

---

## Integration with Existing Scripts

### Using with migrate_data.py

Create a new migration script that uses the DataMapper:

```python
#!/usr/bin/env python3
"""
Enhanced migration script using DataMapper
"""

import json
import ibm_db
from pathlib import Path
from scripts.data_mapper import DataMapper

# Initialize mapper
mapper = DataMapper()

# Load sample data
with open('tests/sample_oracle_data.json', 'r') as f:
    sample_data = json.load(f)

# Connect to DB2
conn = ibm_db.connect("DATABASE=proddb;HOSTNAME=localhost;PORT=5001;PROTOCOL=TCPIP;UID=db2inst1;PWD=password;", "", "")

# Process each table
for table_name, rows in sample_data.items():
    print(f"\nProcessing {table_name}...")
    
    # Map the data
    mapped_rows = mapper.map_table_data(rows, table_name, validate=True)
    
    # Insert into DB2
    for row in mapped_rows:
        # Build INSERT statement
        columns = list(row.keys())
        placeholders = ", ".join(["?" for _ in columns])
        sql = f"INSERT INTO {table_name} ({', '.join(columns)}) VALUES ({placeholders})"
        
        # Execute
        stmt = ibm_db.prepare(conn, sql)
        values = tuple(row[col] for col in columns)
        ibm_db.execute(stmt, values)
    
    print(f"✅ Inserted {len(mapped_rows)} rows into {table_name}")

# Print statistics
mapper.print_statistics()

# Close connection
ibm_db.close(conn)
```

### Standalone Data Quality Check

```python
from scripts.data_mapper import DataMapper

# Initialize mapper
mapper = DataMapper()

# Load data to validate
with open('data_to_validate.json', 'r') as f:
    data = json.load(f)

# Validate without inserting
for table_name, rows in data.items():
    print(f"\nValidating {table_name}...")
    
    valid_rows = []
    invalid_rows = []
    
    for row in rows:
        mapped_row = mapper.map_row(row, table_name, validate=True)
        if mapped_row:
            valid_rows.append(mapped_row)
        else:
            invalid_rows.append(row)
    
    print(f"✅ Valid: {len(valid_rows)}")
    print(f"❌ Invalid: {len(invalid_rows)}")
    
    if invalid_rows:
        print("Invalid rows:")
        for row in invalid_rows:
            print(f"  {row}")

mapper.print_statistics()
```

---

## Advanced Usage

### Custom Configuration Path

```python
from pathlib import Path
from scripts.data_mapper import DataMapper

# Use custom config
custom_config = Path("/path/to/custom_mappings.json")
mapper = DataMapper(config_path=custom_config)
```

### Get Table Schema

```python
# Get full table configuration
schema = mapper.get_table_schema("PRODUCTS")
print(schema)

# Get specific column configuration
col_config = mapper.get_column_config("PRODUCTS", "PRICE")
print(col_config)
```

### Reset Statistics

```python
# Process first batch
mapper.map_table_data(batch1, "PRODUCTS")
mapper.print_statistics()

# Reset for next batch
mapper.reset_statistics()

# Process second batch
mapper.map_table_data(batch2, "PRODUCTS")
mapper.print_statistics()
```

### Disable Validation

```python
# Map without validation (faster, but less safe)
mapped_row = mapper.map_row(source_row, "PRODUCTS", validate=False)
```

---

## Error Handling

The DataMapper handles errors gracefully:

- **Invalid transformations**: Returns `None` and logs warning
- **Validation failures**: Returns `None` for the row
- **Missing configuration**: Logs error and returns `None`
- **Type conversion errors**: Returns `None` and increments failed count

Example:

```python
# This will fail validation (negative price)
invalid_row = {
    "PRODUCT_ID": "1001",
    "NAME": "Test",
    "PRICE": "-99.99"  # Invalid: min is 0
}

result = mapper.map_row(invalid_row, "PRODUCTS")
# result will be None

stats = mapper.get_statistics()
print(f"Failed rows: {stats['failed_rows']}")  # Will be 1
```

---

## Performance Considerations

### Batch Processing
Process data in batches for better performance:

```python
BATCH_SIZE = 1000

for i in range(0, len(all_rows), BATCH_SIZE):
    batch = all_rows[i:i + BATCH_SIZE]
    mapped_batch = mapper.map_table_data(batch, "PRODUCTS")
    # Insert batch into DB2
```

### Disable Validation for Trusted Data
If data is pre-validated, disable validation:

```python
# 30-50% faster without validation
mapped_rows = mapper.map_table_data(rows, "PRODUCTS", validate=False)
```

### Reuse Mapper Instance
Create one mapper instance and reuse it:

```python
# Good: Reuse mapper
mapper = DataMapper()
for table_name, rows in all_data.items():
    mapper.map_table_data(rows, table_name)

# Bad: Create new mapper each time
for table_name, rows in all_data.items():
    mapper = DataMapper()  # Reloads config each time
    mapper.map_table_data(rows, table_name)
```

---

## Extending the Mapper

### Add Custom Transformation

```python
from scripts.data_mapper import DataMapper

class CustomMapper(DataMapper):
    def _build_transformation_registry(self):
        registry = super()._build_transformation_registry()
        
        # Add custom transformation
        registry['custom_transform'] = self._custom_transform
        
        return registry
    
    def _custom_transform(self, value, col_config):
        """Your custom transformation logic"""
        if value is None:
            return None
        # Your logic here
        return transformed_value

# Use custom mapper
mapper = CustomMapper()
```

### Add Custom Validation

```python
class CustomMapper(DataMapper):
    def _build_validation_registry(self):
        registry = super()._build_validation_registry()
        
        # Add custom validation
        registry['custom_validation'] = self._custom_validate
        
        return registry
    
    def _custom_validate(self, value, validation_config):
        """Your custom validation logic"""
        if value is None:
            return True
        # Your validation logic here
        return is_valid

# Use custom mapper
mapper = CustomMapper()
```

---

## Testing

### Unit Test Example

```python
import unittest
from scripts.data_mapper import DataMapper

class TestDataMapper(unittest.TestCase):
    def setUp(self):
        self.mapper = DataMapper()
    
    def test_string_to_integer(self):
        row = {"PRODUCT_ID": "1001", "NAME": "Test", "PRICE": "99.99"}
        result = self.mapper.map_row(row, "PRODUCTS")
        self.assertEqual(result["PRODUCT_ID"], 1001)
        self.assertIsInstance(result["PRODUCT_ID"], int)
    
    def test_trim_string(self):
        row = {"PRODUCT_ID": "1001", "NAME": "  Test  ", "PRICE": "99.99"}
        result = self.mapper.map_row(row, "PRODUCTS")
        self.assertEqual(result["NAME"], "Test")
    
    def test_validation_failure(self):
        # Invalid: NULL for non-nullable field
        row = {"PRODUCT_ID": None, "NAME": "Test", "PRICE": "99.99"}
        result = self.mapper.map_row(row, "PRODUCTS")
        self.assertIsNone(result)

if __name__ == '__main__':
    unittest.main()
```

---

## Troubleshooting

### Issue: Transformation not applied

**Problem**: Value not being transformed

**Solution**: Check transformation name in `table_mappings.json` matches registry

```python
# List available transformations
mapper = DataMapper()
print(mapper.transformation_registry.keys())
```

### Issue: Validation always fails

**Problem**: Validation type mismatch

**Solution**: Ensure validation type matches data type

```json
{
    "transformation": "string_to_integer",
    "validation": {
        "type": "integer"  // Must match transformed type
    }
}
```

### Issue: Statistics not updating

**Problem**: Using multiple mapper instances

**Solution**: Reuse single mapper instance

```python
# Good
mapper = DataMapper()
mapper.map_table_data(data1, "TABLE1")
mapper.map_table_data(data2, "TABLE2")
mapper.print_statistics()  // Shows combined stats
```

---

## Best Practices

1. **Always validate production data**: Use `validate=True` for production migrations
2. **Test transformations**: Test with sample data before full migration
3. **Monitor statistics**: Check success rates to identify data quality issues
4. **Handle nulls**: Configure `nullable` correctly in table mappings
5. **Use appropriate transformations**: Match transformation to data type
6. **Batch processing**: Process large datasets in batches
7. **Error logging**: Log failed rows for manual review
8. **Reuse mapper**: Create one instance per migration session

---

## API Reference

### DataMapper Class

#### Constructor
```python
DataMapper(config_path: Optional[Path] = None)
```

#### Methods

- `map_row(row: Dict, table_name: str, validate: bool = True) -> Optional[Dict]`
- `map_table_data(rows: List[Dict], table_name: str, validate: bool = True) -> List[Dict]`
- `transform_value(value: Any, col_config: Dict) -> Any`
- `validate_value(value: Any, col_config: Dict) -> bool`
- `get_table_schema(table_name: str) -> Optional[Dict]`
- `get_column_config(table_name: str, column_name: str) -> Optional[Dict]`
- `get_statistics() -> Dict`
- `reset_statistics() -> None`
- `print_statistics() -> None`

---

## Support

For issues or questions:
- Check existing table_mappings.json configuration
- Review transformation and validation types
- Test with small sample data first
- Check statistics for error patterns

---

**Built with ❤️ for clean, reliable data migrations**
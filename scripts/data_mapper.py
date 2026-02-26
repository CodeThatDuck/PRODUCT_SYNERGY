#!/usr/bin/env python3
"""
Advanced Data Mapper Utility for Oracle to DB2 Migration
Provides comprehensive field mapping, transformation, and validation capabilities
This is a NEW utility that complements existing migration scripts
"""

import json
import sys
from pathlib import Path
from typing import Dict, List, Any, Optional, Callable
from decimal import Decimal, InvalidOperation
from datetime import datetime, date
import re


class DataMapper:
    """
    Advanced data mapper for Oracle to DB2 migrations
    Handles field mapping, transformations, validations, and data quality checks
    """
    
    def __init__(self, config_path: Optional[Path] = None):
        """Initialize the data mapper with configuration"""
        if config_path is None:
            script_dir = Path(__file__).parent
            project_root = script_dir.parent
            config_path = project_root / "database" / "migrations" / "table_mappings.json"
        
        self.config_path = config_path
        self.config = self._load_config()
        self.transformation_registry = self._build_transformation_registry()
        self.validation_registry = self._build_validation_registry()
        self.stats = {
            'total_rows': 0,
            'successful_rows': 0,
            'failed_rows': 0,
            'transformations_applied': 0,
            'validations_passed': 0,
            'validations_failed': 0
        }
    
    def _load_config(self) -> Dict:
        """Load JSON configuration"""
        try:
            with open(self.config_path, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            print(f"❌ Configuration file not found: {self.config_path}")
            sys.exit(1)
        except json.JSONDecodeError as e:
            print(f"❌ Invalid JSON: {e}")
            sys.exit(1)
    
    def _build_transformation_registry(self) -> Dict[str, Callable]:
        """Build registry of transformation functions"""
        return {
            'string_to_integer': self._transform_string_to_integer,
            'string_to_decimal': self._transform_string_to_decimal,
            'trim_string': self._transform_trim_string,
            'string_to_timestamp': self._transform_string_to_timestamp,
            'pass_through': self._transform_pass_through,
            'uppercase': self._transform_uppercase,
            'lowercase': self._transform_lowercase,
            'remove_special_chars': self._transform_remove_special_chars,
            'normalize_phone': self._transform_normalize_phone,
            'normalize_email': self._transform_normalize_email,
            'string_to_boolean': self._transform_string_to_boolean,
            'pad_string': self._transform_pad_string,
            'truncate_string': self._transform_truncate_string
        }
    
    def _build_validation_registry(self) -> Dict[str, Callable]:
        """Build registry of validation functions"""
        return {
            'integer': self._validate_integer,
            'decimal': self._validate_decimal,
            'string': self._validate_string,
            'timestamp': self._validate_timestamp,
            'binary': self._validate_binary,
            'email': self._validate_email,
            'phone': self._validate_phone,
            'url': self._validate_url,
            'range': self._validate_range
        }
    
    # ==================== TRANSFORMATION FUNCTIONS ====================
    
    def _transform_string_to_integer(self, value: Any, col_config: Dict) -> Optional[int]:
        """Convert string to integer"""
        if value is None or value == '':
            return None
        try:
            return int(str(value).strip())
        except (ValueError, TypeError):
            return None
    
    def _transform_string_to_decimal(self, value: Any, col_config: Dict) -> Optional[Decimal]:
        """Convert string to decimal with precision"""
        if value is None or value == '':
            return None
        try:
            decimal_value = Decimal(str(value).strip())
            # Apply scale if specified
            validation = col_config.get('validation', {})
            scale = validation.get('scale')
            if scale is not None:
                quantize_value = Decimal(10) ** -scale
                decimal_value = decimal_value.quantize(quantize_value)
            return decimal_value
        except (InvalidOperation, ValueError, TypeError):
            return None
    
    def _transform_trim_string(self, value: Any, col_config: Dict) -> Optional[str]:
        """Trim whitespace from string"""
        if value is None or value == '':
            return None
        return str(value).strip()
    
    def _transform_string_to_timestamp(self, value: Any, col_config: Dict) -> Optional[datetime]:
        """Convert string to timestamp"""
        if value is None or value == '':
            return None
        try:
            if isinstance(value, datetime):
                return value
            if isinstance(value, date):
                return datetime.combine(value, datetime.min.time())
            
            # Try ISO format first
            value_str = str(value).strip()
            try:
                return datetime.fromisoformat(value_str)
            except ValueError:
                pass
            
            # Try common date formats
            formats = [
                '%Y-%m-%d',
                '%Y-%m-%d %H:%M:%S',
                '%Y/%m/%d',
                '%d-%m-%Y',
                '%d/%m/%Y',
                '%m-%d-%Y',
                '%m/%d/%Y'
            ]
            
            for fmt in formats:
                try:
                    return datetime.strptime(value_str, fmt)
                except ValueError:
                    continue
            
            return None
        except (ValueError, TypeError):
            return None
    
    def _transform_pass_through(self, value: Any, col_config: Dict) -> Any:
        """Pass value through without transformation"""
        return value
    
    def _transform_uppercase(self, value: Any, col_config: Dict) -> Optional[str]:
        """Convert string to uppercase"""
        if value is None or value == '':
            return None
        return str(value).upper()
    
    def _transform_lowercase(self, value: Any, col_config: Dict) -> Optional[str]:
        """Convert string to lowercase"""
        if value is None or value == '':
            return None
        return str(value).lower()
    
    def _transform_remove_special_chars(self, value: Any, col_config: Dict) -> Optional[str]:
        """Remove special characters from string"""
        if value is None or value == '':
            return None
        return re.sub(r'[^a-zA-Z0-9\s]', '', str(value))
    
    def _transform_normalize_phone(self, value: Any, col_config: Dict) -> Optional[str]:
        """Normalize phone number format"""
        if value is None or value == '':
            return None
        # Remove all non-digit characters
        digits = re.sub(r'\D', '', str(value))
        return digits if digits else None
    
    def _transform_normalize_email(self, value: Any, col_config: Dict) -> Optional[str]:
        """Normalize email address"""
        if value is None or value == '':
            return None
        email = str(value).strip().lower()
        return email if '@' in email else None
    
    def _transform_string_to_boolean(self, value: Any, col_config: Dict) -> Optional[bool]:
        """Convert string to boolean"""
        if value is None or value == '':
            return None
        value_str = str(value).strip().lower()
        if value_str in ('true', '1', 'yes', 'y', 't'):
            return True
        elif value_str in ('false', '0', 'no', 'n', 'f'):
            return False
        return None
    
    def _transform_pad_string(self, value: Any, col_config: Dict) -> Optional[str]:
        """Pad string to specified length"""
        if value is None or value == '':
            return None
        value_str = str(value)
        validation = col_config.get('validation', {})
        max_length = validation.get('max_length', len(value_str))
        return value_str.ljust(max_length)
    
    def _transform_truncate_string(self, value: Any, col_config: Dict) -> Optional[str]:
        """Truncate string to maximum length"""
        if value is None or value == '':
            return None
        value_str = str(value)
        validation = col_config.get('validation', {})
        max_length = validation.get('max_length')
        if max_length and len(value_str) > max_length:
            return value_str[:max_length]
        return value_str
    
    # ==================== VALIDATION FUNCTIONS ====================
    
    def _validate_integer(self, value: Any, validation_config: Dict) -> bool:
        """Validate integer value"""
        if value is None:
            return True
        
        try:
            int_value = int(value)
            
            # Check min/max
            if 'min' in validation_config and int_value < validation_config['min']:
                return False
            if 'max' in validation_config and int_value > validation_config['max']:
                return False
            
            return True
        except (ValueError, TypeError):
            return False
    
    def _validate_decimal(self, value: Any, validation_config: Dict) -> bool:
        """Validate decimal value"""
        if value is None:
            return True
        
        try:
            decimal_value = Decimal(str(value))
            
            # Check min/max
            if 'min' in validation_config and decimal_value < Decimal(str(validation_config['min'])):
                return False
            if 'max' in validation_config and decimal_value > Decimal(str(validation_config['max'])):
                return False
            
            # Check precision and scale
            if 'precision' in validation_config or 'scale' in validation_config:
                value_str = str(decimal_value)
                if 'E' in value_str or 'e' in value_str:
                    # Scientific notation
                    return True
                
                parts = value_str.lstrip('-').split('.')
                integer_part = parts[0]
                decimal_part = parts[1] if len(parts) > 1 else ''
                
                precision = validation_config.get('precision')
                scale = validation_config.get('scale')
                
                if precision and len(integer_part) + len(decimal_part) > precision:
                    return False
                if scale and len(decimal_part) > scale:
                    return False
            
            return True
        except (InvalidOperation, ValueError, TypeError):
            return False
    
    def _validate_string(self, value: Any, validation_config: Dict) -> bool:
        """Validate string value"""
        if value is None:
            return True
        
        value_str = str(value)
        
        # Check max length
        max_length = validation_config.get('max_length')
        if max_length and len(value_str) > max_length:
            return False
        
        # Check if empty allowed
        allow_empty = validation_config.get('allow_empty', True)
        if not allow_empty and not value_str.strip():
            return False
        
        # Check pattern
        pattern = validation_config.get('pattern')
        if pattern and not re.match(pattern, value_str):
            return False
        
        return True
    
    def _validate_timestamp(self, value: Any, validation_config: Dict) -> bool:
        """Validate timestamp value"""
        if value is None:
            return True
        
        if not isinstance(value, (datetime, date)):
            return False
        
        # Check date range
        min_date = validation_config.get('min_date')
        max_date = validation_config.get('max_date')
        
        if min_date and value < datetime.fromisoformat(min_date):
            return False
        if max_date and value > datetime.fromisoformat(max_date):
            return False
        
        return True
    
    def _validate_binary(self, value: Any, validation_config: Dict) -> bool:
        """Validate binary value"""
        if value is None:
            return True
        return isinstance(value, (bytes, bytearray))
    
    def _validate_email(self, value: Any, validation_config: Dict) -> bool:
        """Validate email format"""
        if value is None:
            return True
        
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return bool(re.match(email_pattern, str(value)))
    
    def _validate_phone(self, value: Any, validation_config: Dict) -> bool:
        """Validate phone number format"""
        if value is None:
            return True
        
        # Remove all non-digit characters
        digits = re.sub(r'\D', '', str(value))
        
        # Check length (typically 10-15 digits)
        min_length = validation_config.get('min_length', 10)
        max_length = validation_config.get('max_length', 15)
        
        return min_length <= len(digits) <= max_length
    
    def _validate_url(self, value: Any, validation_config: Dict) -> bool:
        """Validate URL format"""
        if value is None:
            return True
        
        url_pattern = r'^https?://[^\s/$.?#].[^\s]*$'
        return bool(re.match(url_pattern, str(value), re.IGNORECASE))
    
    def _validate_range(self, value: Any, validation_config: Dict) -> bool:
        """Validate value is within range"""
        if value is None:
            return True
        
        try:
            numeric_value = float(value)
            min_val = validation_config.get('min')
            max_val = validation_config.get('max')
            
            if min_val is not None and numeric_value < min_val:
                return False
            if max_val is not None and numeric_value > max_val:
                return False
            
            return True
        except (ValueError, TypeError):
            return False
    
    # ==================== MAIN MAPPING FUNCTIONS ====================
    
    def transform_value(self, value: Any, col_config: Dict) -> Any:
        """Transform a single value based on column configuration"""
        transformation = col_config.get('transformation', 'pass_through')
        
        if transformation not in self.transformation_registry:
            print(f"⚠️  Unknown transformation: {transformation}, using pass_through")
            transformation = 'pass_through'
        
        transform_func = self.transformation_registry[transformation]
        transformed_value = transform_func(value, col_config)
        
        if transformed_value is not None:
            self.stats['transformations_applied'] += 1
        
        return transformed_value
    
    def validate_value(self, value: Any, col_config: Dict) -> bool:
        """Validate a single value based on column configuration"""
        validation_config = col_config.get('validation', {})
        
        if not validation_config:
            return True
        
        validation_type = validation_config.get('type', 'string')
        
        if validation_type not in self.validation_registry:
            print(f"⚠️  Unknown validation type: {validation_type}")
            return True
        
        validate_func = self.validation_registry[validation_type]
        is_valid = validate_func(value, validation_config)
        
        if is_valid:
            self.stats['validations_passed'] += 1
        else:
            self.stats['validations_failed'] += 1
        
        return is_valid
    
    def map_row(self, row: Dict, table_name: str, validate: bool = True) -> Optional[Dict]:
        """
        Map a single row from Oracle format to DB2 format
        
        Args:
            row: Source row data
            table_name: Name of the table
            validate: Whether to validate values
        
        Returns:
            Mapped row or None if validation fails
        """
        self.stats['total_rows'] += 1
        
        table_config = self.config.get('tables', {}).get(table_name)
        if not table_config:
            print(f"❌ Table configuration not found: {table_name}")
            self.stats['failed_rows'] += 1
            return None
        
        columns = table_config.get('columns', {})
        mapped_row = {}
        
        for col_name, col_config in columns.items():
            # Get source value
            source_value = row.get(col_name)
            
            # Transform value
            transformed_value = self.transform_value(source_value, col_config)
            
            # Check nullable constraint first
            nullable = col_config.get('nullable', True)
            if not nullable and transformed_value is None:
                print(f"⚠️  Validation failed for {table_name}.{col_name}: NULL not allowed")
                self.stats['failed_rows'] += 1
                return None
            
            # Validate if required
            if validate and not self.validate_value(transformed_value, col_config):
                print(f"⚠️  Validation failed for {table_name}.{col_name}: Invalid value")
                self.stats['failed_rows'] += 1
                return None
            
            mapped_row[col_name] = transformed_value
        
        self.stats['successful_rows'] += 1
        return mapped_row
    
    def map_table_data(self, rows: List[Dict], table_name: str, validate: bool = True) -> List[Dict]:
        """
        Map multiple rows for a table
        
        Args:
            rows: List of source rows
            table_name: Name of the table
            validate: Whether to validate values
        
        Returns:
            List of mapped rows
        """
        mapped_rows = []
        
        for row in rows:
            mapped_row = self.map_row(row, table_name, validate)
            if mapped_row is not None:
                mapped_rows.append(mapped_row)
        
        return mapped_rows
    
    def get_table_schema(self, table_name: str) -> Optional[Dict]:
        """Get schema configuration for a table"""
        return self.config.get('tables', {}).get(table_name)
    
    def get_column_config(self, table_name: str, column_name: str) -> Optional[Dict]:
        """Get configuration for a specific column"""
        table_config = self.get_table_schema(table_name)
        if table_config:
            return table_config.get('columns', {}).get(column_name)
        return None
    
    def get_statistics(self) -> Dict:
        """Get mapping statistics"""
        return self.stats.copy()
    
    def reset_statistics(self):
        """Reset mapping statistics"""
        self.stats = {
            'total_rows': 0,
            'successful_rows': 0,
            'failed_rows': 0,
            'transformations_applied': 0,
            'validations_passed': 0,
            'validations_failed': 0
        }
    
    def print_statistics(self):
        """Print mapping statistics"""
        print("\n" + "=" * 60)
        print("DATA MAPPER STATISTICS")
        print("=" * 60)
        print(f"Total Rows Processed:      {self.stats['total_rows']}")
        print(f"Successful Rows:           {self.stats['successful_rows']}")
        print(f"Failed Rows:               {self.stats['failed_rows']}")
        print(f"Transformations Applied:   {self.stats['transformations_applied']}")
        print(f"Validations Passed:        {self.stats['validations_passed']}")
        print(f"Validations Failed:        {self.stats['validations_failed']}")
        
        if self.stats['total_rows'] > 0:
            success_rate = (self.stats['successful_rows'] / self.stats['total_rows']) * 100
            print(f"Success Rate:              {success_rate:.2f}%")
        
        print("=" * 60)


def main():
    """Example usage of DataMapper"""
    print("=" * 60)
    print("Data Mapper Utility - Example Usage")
    print("=" * 60)
    
    # Initialize mapper
    mapper = DataMapper()
    
    # Example: Map sample data
    sample_data = {
        "PRODUCT_ID": "1001",
        "NAME": "  Test Product  ",
        "PRICE": "99.99"
    }
    
    print("\n📋 Original Data:")
    print(json.dumps(sample_data, indent=2))
    
    # Map the row
    mapped_data = mapper.map_row(sample_data, "PRODUCTS")
    
    print("\n✨ Mapped Data:")
    print(json.dumps(mapped_data, indent=2, default=str))
    
    # Print statistics
    mapper.print_statistics()
    
    print("\n✅ Data Mapper utility is ready to use!")
    print("Import this module in your migration scripts:")
    print("  from data_mapper import DataMapper")


if __name__ == "__main__":
    main()

# Made with Bob

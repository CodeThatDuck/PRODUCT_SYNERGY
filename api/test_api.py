#!/usr/bin/env python3
"""
Test script for Oracle to DB2 Migration API
Tests all endpoints to ensure they work correctly
"""

import requests
import json
from pathlib import Path

# API Configuration
API_BASE_URL = "http://localhost:8000"
PROJECT_ROOT = Path(__file__).parent.parent
TEST_SQL_FILE = PROJECT_ROOT / "database" / "schemas" / "oracle_source_schema.sql"


def print_section(title):
    """Print formatted section header"""
    print("\n" + "=" * 70)
    print(f"  {title}")
    print("=" * 70)


def test_health_check():
    """Test 1: Health Check Endpoint"""
    print_section("TEST 1: Health Check")
    
    try:
        response = requests.get(f"{API_BASE_URL}/api/health")
        print(f"Status Code: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        
        if response.status_code == 200:
            print("✅ Health check passed")
            return True
        else:
            print("❌ Health check failed")
            return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


def test_upload_file():
    """Test 2: Upload Oracle SQL File"""
    print_section("TEST 2: Upload Oracle SQL File")
    
    if not TEST_SQL_FILE.exists():
        print(f"❌ Test file not found: {TEST_SQL_FILE}")
        return False, None
    
    try:
        with open(TEST_SQL_FILE, 'rb') as f:
            files = {'file': (TEST_SQL_FILE.name, f, 'application/sql')}
            response = requests.post(f"{API_BASE_URL}/api/upload", files=files)
        
        print(f"Status Code: {response.status_code}")
        result = response.json()
        print(f"Response: {json.dumps(result, indent=2)}")
        
        if response.status_code == 200:
            print("✅ File upload passed")
            uploaded_filename = result['file_info']['saved_as']
            return True, uploaded_filename
        else:
            print("❌ File upload failed")
            return False, None
    except Exception as e:
        print(f"❌ Error: {e}")
        return False, None


def test_convert(filename):
    """Test 3: Convert Oracle SQL to DB2"""
    print_section("TEST 3: Convert Oracle SQL to DB2 (3-Part Process)")
    
    if not filename:
        print("❌ No filename provided (upload test must pass first)")
        return False
    
    try:
        response = requests.post(
            f"{API_BASE_URL}/api/convert",
            params={"filename": filename}
        )
        
        print(f"Status Code: {response.status_code}")
        result = response.json()
        
        # Print summary
        print("\n📊 Conversion Summary:")
        print(f"   Filename: {result.get('filename')}")
        print(f"   Overall Status: {result.get('summary', {}).get('overall_status')}")
        print(f"   Completed Parts: {result.get('summary', {}).get('completed_parts')}/3")
        
        # Print each part
        parts = result.get('parts', {})
        
        print("\n📋 Part A: Parse to JSON")
        part_a = parts.get('part_a_parse_to_json', {})
        print(f"   Status: {part_a.get('status')}")
        print(f"   Tables Found: {part_a.get('tables_found')}")
        print(f"   Output File: {part_a.get('output_file')}")
        
        print("\n📋 Part B: Clone Schema")
        part_b = parts.get('part_b_clone_schema', {})
        print(f"   Status: {part_b.get('status')}")
        stats = part_b.get('statistics', {})
        print(f"   Tables Created: {stats.get('tables_created')}")
        print(f"   Foreign Keys: {stats.get('foreign_keys')}")
        print(f"   Indexes: {stats.get('indexes')}")
        print(f"   Output File: {part_b.get('output_file')}")
        
        print("\n📋 Part C: Migrate Data")
        part_c = parts.get('part_c_migrate_data', {})
        print(f"   Status: {part_c.get('status')}")
        stats = part_c.get('statistics', {})
        print(f"   Rows Processed: {stats.get('total_rows_processed')}")
        print(f"   Success Rate: {stats.get('success_rate')}")
        print(f"   Output File: {part_c.get('output_file')}")
        
        if response.status_code == 200 and result.get('summary', {}).get('completed_parts') == 3:
            print("\n✅ Conversion test passed - All 3 parts completed!")
            return True
        else:
            print("\n⚠️  Conversion completed with partial success")
            return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


def main():
    """Run all API tests"""
    print("=" * 70)
    print("  Oracle to DB2 Migration API - Test Suite")
    print("=" * 70)
    print(f"\nAPI Base URL: {API_BASE_URL}")
    print(f"Test SQL File: {TEST_SQL_FILE}")
    
    # Check if API is running
    try:
        requests.get(API_BASE_URL, timeout=2)
    except:
        print("\n❌ ERROR: API is not running!")
        print("\nPlease start the API first:")
        print("  uvicorn api.main:app --reload")
        return
    
    # Run tests
    results = []
    
    # Test 1: Health Check
    results.append(test_health_check())
    
    # Test 2: Upload File
    upload_success, uploaded_filename = test_upload_file()
    results.append(upload_success)
    
    # Test 3: Convert (only if upload succeeded)
    if upload_success:
        results.append(test_convert(uploaded_filename))
    else:
        print_section("TEST 3: SKIPPED (Upload failed)")
        results.append(False)
    
    # Final Summary
    print_section("FINAL SUMMARY")
    passed = sum(results)
    total = len(results)
    
    print(f"\nTests Passed: {passed}/{total}")
    
    if passed == total:
        print("\n✅ ALL TESTS PASSED!")
        print("\nThe API is working correctly and ready to use.")
    else:
        print("\n❌ SOME TESTS FAILED!")
        print("\nPlease check the errors above and fix them.")
    
    print("\n" + "=" * 70)


if __name__ == "__main__":
    main()

# Made with Bob
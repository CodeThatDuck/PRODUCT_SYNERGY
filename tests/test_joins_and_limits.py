#!/usr/bin/env python3
"""
Comprehensive JOIN and LIMIT Testing Suite
Tests all JOIN types and LIMIT/OFFSET combinations added to the project
Dedicated test file for validating new features
"""

import json
import sys
import ibm_db  # type: ignore
from pathlib import Path
from decimal import Decimal

# Paths
SCRIPT_DIR = Path(__file__).parent
PROJECT_ROOT = SCRIPT_DIR.parent

# DB2 Connection
DB2_CONFIG = {
    "DATABASE": "proddb",
    "HOSTNAME": "localhost",
    "PORT": "5000",
    "PROTOCOL": "TCPIP",
    "UID": "db2inst1",
    "PWD": "password"
}


def print_header(title):
    """Print a formatted header"""
    print("\n" + "=" * 80)
    print(f"  {title}")
    print("=" * 80)


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


def execute_test_query(conn, query, test_name):
    """Execute a test query and return success status"""
    try:
        stmt = ibm_db.exec_immediate(conn, query)
        if stmt and stmt is not True:
            row_count = 0
            while ibm_db.fetch_tuple(stmt):
                row_count += 1
            print(f"  ✅ {test_name} - {row_count} rows returned")
            return True
        else:
            print(f"  ✅ {test_name} - Query executed")
            return True
    except Exception as e:
        print(f"  ❌ {test_name} - Failed: {str(e)[:100]}")
        return False


def test_all_join_types(conn):
    """Test all 7 JOIN types"""
    print_header("Testing All JOIN Types")
    
    tests_passed = 0
    tests_total = 7
    
    # Test 1: INNER JOIN
    query = """
    SELECT O.ORDER_ID, C.FIRST_NAME 
    FROM ORDERS O 
    INNER JOIN CUSTOMERS C ON O.CUSTOMER_ID = C.CUSTOMER_ID 
    FETCH FIRST 5 ROWS ONLY
    """
    if execute_test_query(conn, query, "INNER JOIN"):
        tests_passed += 1
    
    # Test 2: LEFT JOIN
    query = """
    SELECT C.CUSTOMER_ID, COUNT(O.ORDER_ID) AS ORDER_COUNT
    FROM CUSTOMERS C 
    LEFT JOIN ORDERS O ON C.CUSTOMER_ID = O.CUSTOMER_ID 
    GROUP BY C.CUSTOMER_ID
    FETCH FIRST 5 ROWS ONLY
    """
    if execute_test_query(conn, query, "LEFT JOIN"):
        tests_passed += 1
    
    # Test 3: RIGHT JOIN
    query = """
    SELECT P.PRODUCT_ID, COUNT(OI.ORDER_ITEM_ID) AS TIMES_ORDERED
    FROM ORDER_ITEMS OI 
    RIGHT JOIN PRODUCTS P ON OI.PRODUCT_ID = P.PRODUCT_ID 
    GROUP BY P.PRODUCT_ID
    FETCH FIRST 5 ROWS ONLY
    """
    if execute_test_query(conn, query, "RIGHT JOIN"):
        tests_passed += 1
    
    # Test 4: FULL OUTER JOIN
    query = """
    SELECT C.CUSTOMER_ID, O.ORDER_ID
    FROM CUSTOMERS C 
    FULL OUTER JOIN ORDERS O ON C.CUSTOMER_ID = O.CUSTOMER_ID 
    FETCH FIRST 5 ROWS ONLY
    """
    if execute_test_query(conn, query, "FULL OUTER JOIN"):
        tests_passed += 1
    
    # Test 5: CROSS JOIN
    query = """
    SELECT P1.PRODUCT_ID, P2.PRODUCT_ID
    FROM PRODUCTS P1 
    CROSS JOIN PRODUCTS P2 
    WHERE P1.PRODUCT_ID < P2.PRODUCT_ID
    FETCH FIRST 5 ROWS ONLY
    """
    if execute_test_query(conn, query, "CROSS JOIN"):
        tests_passed += 1
    
    # Test 6: SELF-JOIN
    query = """
    SELECT P1.NAME, P2.NAME
    FROM ORDER_ITEMS OI1 
    INNER JOIN ORDER_ITEMS OI2 ON OI1.ORDER_ID = OI2.ORDER_ID AND OI1.PRODUCT_ID < OI2.PRODUCT_ID
    INNER JOIN PRODUCTS P1 ON OI1.PRODUCT_ID = P1.PRODUCT_ID
    INNER JOIN PRODUCTS P2 ON OI2.PRODUCT_ID = P2.PRODUCT_ID
    FETCH FIRST 5 ROWS ONLY
    """
    if execute_test_query(conn, query, "SELF-JOIN"):
        tests_passed += 1
    
    # Test 7: Multi-table JOIN (4 tables)
    query = """
    SELECT C.FIRST_NAME, O.ORDER_ID, P.NAME
    FROM ORDER_ITEMS OI
    INNER JOIN ORDERS O ON OI.ORDER_ID = O.ORDER_ID
    INNER JOIN CUSTOMERS C ON O.CUSTOMER_ID = C.CUSTOMER_ID
    INNER JOIN PRODUCTS P ON OI.PRODUCT_ID = P.PRODUCT_ID
    FETCH FIRST 5 ROWS ONLY
    """
    if execute_test_query(conn, query, "Multi-table JOIN (4 tables)"):
        tests_passed += 1
    
    print(f"\n  JOIN Tests: {tests_passed}/{tests_total} passed")
    return tests_passed == tests_total


def test_limit_with_order_by(conn):
    """Test LIMIT + ORDER BY combinations"""
    print_header("Testing LIMIT + ORDER BY")
    
    tests_passed = 0
    tests_total = 3
    
    # Test 1: Simple ORDER BY + LIMIT
    query = """
    SELECT ORDER_ID, TOTAL_AMOUNT 
    FROM ORDERS 
    ORDER BY TOTAL_AMOUNT DESC 
    FETCH FIRST 5 ROWS ONLY
    """
    if execute_test_query(conn, query, "ORDER BY DESC + LIMIT"):
        tests_passed += 1
    
    # Test 2: Multiple columns ORDER BY + LIMIT
    query = """
    SELECT CUSTOMER_ID, FIRST_NAME, LAST_NAME 
    FROM CUSTOMERS 
    ORDER BY LAST_NAME, FIRST_NAME 
    FETCH FIRST 10 ROWS ONLY
    """
    if execute_test_query(conn, query, "Multi-column ORDER BY + LIMIT"):
        tests_passed += 1
    
    # Test 3: ORDER BY with expression + LIMIT
    query = """
    SELECT PRODUCT_ID, NAME, PRICE 
    FROM PRODUCTS 
    ORDER BY PRICE * 1.1 DESC 
    FETCH FIRST 5 ROWS ONLY
    """
    if execute_test_query(conn, query, "ORDER BY expression + LIMIT"):
        tests_passed += 1
    
    print(f"\n  LIMIT + ORDER BY Tests: {tests_passed}/{tests_total} passed")
    return tests_passed == tests_total


def test_limit_with_upper_lower(conn):
    """Test LIMIT + UPPER/LOWER functions"""
    print_header("Testing LIMIT + UPPER/LOWER")
    
    tests_passed = 0
    tests_total = 4
    
    # Test 1: UPPER + LIMIT
    query = """
    SELECT CUSTOMER_ID, UPPER(FIRST_NAME) AS FIRST_NAME_UPPER 
    FROM CUSTOMERS 
    WHERE UPPER(FIRST_NAME) LIKE 'J%'
    FETCH FIRST 5 ROWS ONLY
    """
    if execute_test_query(conn, query, "UPPER + WHERE + LIMIT"):
        tests_passed += 1
    
    # Test 2: LOWER + LIMIT
    query = """
    SELECT CUSTOMER_ID, LOWER(EMAIL) AS EMAIL_LOWER 
    FROM CUSTOMERS 
    WHERE LOWER(EMAIL) LIKE '%example.com'
    FETCH FIRST 5 ROWS ONLY
    """
    if execute_test_query(conn, query, "LOWER + WHERE + LIMIT"):
        tests_passed += 1
    
    # Test 3: UPPER in ORDER BY + LIMIT
    query = """
    SELECT FIRST_NAME, LAST_NAME 
    FROM CUSTOMERS 
    ORDER BY UPPER(LAST_NAME) 
    FETCH FIRST 5 ROWS ONLY
    """
    if execute_test_query(conn, query, "ORDER BY UPPER + LIMIT"):
        tests_passed += 1
    
    # Test 4: UPPER + LOWER combination + LIMIT
    query = """
    SELECT UPPER(FIRST_NAME) AS FIRST, LOWER(LAST_NAME) AS LAST 
    FROM CUSTOMERS 
    ORDER BY LAST_NAME 
    FETCH FIRST 5 ROWS ONLY
    """
    if execute_test_query(conn, query, "UPPER + LOWER + ORDER BY + LIMIT"):
        tests_passed += 1
    
    print(f"\n  LIMIT + UPPER/LOWER Tests: {tests_passed}/{tests_total} passed")
    return tests_passed == tests_total


def test_limit_with_distinct(conn):
    """Test LIMIT + DISTINCT combinations"""
    print_header("Testing LIMIT + DISTINCT")
    
    tests_passed = 0
    tests_total = 3
    
    # Test 1: Simple DISTINCT + LIMIT
    query = """
    SELECT DISTINCT ORDER_STATUS 
    FROM ORDERS 
    ORDER BY ORDER_STATUS 
    FETCH FIRST 5 ROWS ONLY
    """
    if execute_test_query(conn, query, "DISTINCT + ORDER BY + LIMIT"):
        tests_passed += 1
    
    # Test 2: DISTINCT with multiple columns + LIMIT
    query = """
    SELECT DISTINCT CUSTOMER_ID, ORDER_STATUS 
    FROM ORDERS 
    ORDER BY CUSTOMER_ID 
    FETCH FIRST 10 ROWS ONLY
    """
    if execute_test_query(conn, query, "DISTINCT multi-column + LIMIT"):
        tests_passed += 1
    
    # Test 3: DISTINCT + WHERE + LIMIT
    query = """
    SELECT DISTINCT ORDER_STATUS 
    FROM ORDERS 
    WHERE ORDER_DATE >= '2024-01-01'
    ORDER BY ORDER_STATUS 
    FETCH FIRST 5 ROWS ONLY
    """
    if execute_test_query(conn, query, "DISTINCT + WHERE + ORDER BY + LIMIT"):
        tests_passed += 1
    
    print(f"\n  LIMIT + DISTINCT Tests: {tests_passed}/{tests_total} passed")
    return tests_passed == tests_total


def test_offset_and_pagination(conn):
    """Test OFFSET for pagination"""
    print_header("Testing OFFSET + LIMIT (Pagination)")
    
    tests_passed = 0
    tests_total = 4
    
    # Test 1: Simple OFFSET + LIMIT
    query = """
    SELECT CUSTOMER_ID, FIRST_NAME, LAST_NAME 
    FROM CUSTOMERS 
    ORDER BY CUSTOMER_ID 
    OFFSET 3 ROWS FETCH FIRST 3 ROWS ONLY
    """
    if execute_test_query(conn, query, "OFFSET 3 + LIMIT 3 (Page 2)"):
        tests_passed += 1
    
    # Test 2: OFFSET with WHERE + LIMIT
    query = """
    SELECT PRODUCT_ID, NAME, PRICE 
    FROM PRODUCTS 
    WHERE PRICE > 50 
    ORDER BY PRICE 
    OFFSET 2 ROWS FETCH FIRST 5 ROWS ONLY
    """
    if execute_test_query(conn, query, "WHERE + OFFSET + LIMIT"):
        tests_passed += 1
    
    # Test 3: OFFSET with JOIN + LIMIT
    query = """
    SELECT C.CUSTOMER_ID, C.FIRST_NAME, COUNT(O.ORDER_ID) AS ORDER_COUNT
    FROM CUSTOMERS C 
    LEFT JOIN ORDERS O ON C.CUSTOMER_ID = O.CUSTOMER_ID 
    GROUP BY C.CUSTOMER_ID, C.FIRST_NAME 
    ORDER BY ORDER_COUNT DESC 
    OFFSET 1 ROWS FETCH FIRST 3 ROWS ONLY
    """
    if execute_test_query(conn, query, "JOIN + GROUP BY + OFFSET + LIMIT"):
        tests_passed += 1
    
    # Test 4: Large OFFSET + LIMIT
    query = """
    SELECT ORDER_ID, ORDER_DATE 
    FROM ORDERS 
    ORDER BY ORDER_DATE 
    OFFSET 5 ROWS FETCH FIRST 5 ROWS ONLY
    """
    if execute_test_query(conn, query, "OFFSET 5 + LIMIT 5"):
        tests_passed += 1
    
    print(f"\n  OFFSET + LIMIT Tests: {tests_passed}/{tests_total} passed")
    return tests_passed == tests_total


def test_complex_combinations(conn):
    """Test complex combinations of features"""
    print_header("Testing Complex Feature Combinations")
    
    tests_passed = 0
    tests_total = 3
    
    # Test 1: UPPER + WHERE + ORDER BY + LIMIT
    query = """
    SELECT CUSTOMER_ID, FIRST_NAME, LAST_NAME 
    FROM CUSTOMERS 
    WHERE UPPER(LAST_NAME) LIKE '%S%'
    ORDER BY LAST_NAME 
    FETCH FIRST 5 ROWS ONLY
    """
    if execute_test_query(conn, query, "UPPER + WHERE + ORDER BY + LIMIT"):
        tests_passed += 1
    
    # Test 2: DISTINCT + LOWER + WHERE + LIMIT
    query = """
    SELECT DISTINCT LOWER(ORDER_STATUS) AS STATUS 
    FROM ORDERS 
    WHERE ORDER_DATE >= '2024-01-01'
    ORDER BY STATUS 
    FETCH FIRST 5 ROWS ONLY
    """
    if execute_test_query(conn, query, "DISTINCT + LOWER + WHERE + ORDER BY + LIMIT"):
        tests_passed += 1
    
    # Test 3: JOIN + UPPER + WHERE + GROUP BY + OFFSET + LIMIT
    query = """
    SELECT UPPER(C.FIRST_NAME) AS FIRST_NAME, COUNT(O.ORDER_ID) AS ORDER_COUNT
    FROM CUSTOMERS C 
    LEFT JOIN ORDERS O ON C.CUSTOMER_ID = O.CUSTOMER_ID 
    WHERE C.LOYALTY_POINTS > 0 
    GROUP BY C.CUSTOMER_ID, C.FIRST_NAME 
    ORDER BY ORDER_COUNT DESC 
    OFFSET 1 ROWS FETCH FIRST 3 ROWS ONLY
    """
    if execute_test_query(conn, query, "JOIN + UPPER + WHERE + GROUP BY + OFFSET + LIMIT"):
        tests_passed += 1
    
    print(f"\n  Complex Combination Tests: {tests_passed}/{tests_total} passed")
    return tests_passed == tests_total


def main():
    """Main test execution"""
    print("=" * 80)
    print("  COMPREHENSIVE JOIN AND LIMIT TESTING SUITE")
    print("  Testing All New Features Added to the Project")
    print("=" * 80)
    
    # Connect to DB2
    print("\n🔌 Connecting to DB2...")
    conn = connect_to_db2()
    print("✅ Connected to DB2")
    
    all_tests_passed = True
    
    try:
        # Run all test suites
        if not test_all_join_types(conn):
            all_tests_passed = False
        
        if not test_limit_with_order_by(conn):
            all_tests_passed = False
        
        if not test_limit_with_upper_lower(conn):
            all_tests_passed = False
        
        if not test_limit_with_distinct(conn):
            all_tests_passed = False
        
        if not test_offset_and_pagination(conn):
            all_tests_passed = False
        
        if not test_complex_combinations(conn):
            all_tests_passed = False
        
        # Final summary
        print_header("FINAL TEST SUMMARY")
        
        if all_tests_passed:
            print("\n🎉 ✅ ALL TESTS PASSED!")
            print("\n📊 Features Validated:")
            print("  ✅ All 7 JOIN types (INNER, LEFT, RIGHT, FULL OUTER, CROSS, SELF, Multi-table)")
            print("  ✅ LIMIT + ORDER BY")
            print("  ✅ LIMIT + UPPER/LOWER (case-insensitive)")
            print("  ✅ LIMIT + DISTINCT")
            print("  ✅ OFFSET + LIMIT (pagination)")
            print("  ✅ Complex feature combinations")
            print("\n🎯 Total Test Categories: 6")
            print("🎯 Total Individual Tests: 24")
        else:
            print("\n⚠️  SOME TESTS FAILED")
            print("Please review the output above for details")
        
        print("\n" + "=" * 80)
        
        # Close connection
        ibm_db.close(conn)
        print("\n🔌 DB2 connection closed")
        
        if not all_tests_passed:
            sys.exit(1)
        
    except Exception as e:
        print(f"\n❌ TEST SUITE FAILED: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()

# Made with Bob
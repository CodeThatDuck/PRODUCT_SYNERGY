#!/usr/bin/env python3
"""
Complex Query Testing Script
Tests JOIN queries, aggregates, subqueries, and complex WHERE clauses
Demonstrates real-world SQL query patterns for Oracle to DB2 migration
"""

import json
import sys
import ibm_db  # type: ignore
from pathlib import Path
from decimal import Decimal

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


def print_section(title):
    """Print a formatted section header"""
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


def execute_query(conn, query, description):
    """Execute a query and display results"""
    print(f"\n{'='*80}")
    print(f"QUERY: {description}")
    print(f"{'='*80}")
    print(f"\nSQL:")
    print("-" * 80)
    # Pretty print SQL
    for line in query.strip().split('\n'):
        print(f"  {line.strip()}")
    print("-" * 80)
    
    try:
        stmt = ibm_db.exec_immediate(conn, query)
        if stmt and stmt is not True:
            print(f"\nRESULTS:")
            print("-" * 80)
            row_count = 0
            while True:
                row = ibm_db.fetch_tuple(stmt)
                if not row:
                    break
                row_count += 1
                # Format row for display
                formatted_row = []
                for val in row:
                    if val is None:
                        formatted_row.append("NULL")
                    elif isinstance(val, (int, Decimal)):
                        formatted_row.append(str(val))
                    else:
                        formatted_row.append(str(val).strip())
                print(f"  Row {row_count}: {tuple(formatted_row)}")
            
            if row_count == 0:
                print("  (No results)")
            else:
                print(f"\n  Total rows: {row_count}")
            print("-" * 80)
            print("✅ Query executed successfully")
            return True
    except Exception as e:
        print(f"\n❌ Query failed: {e}")
        print("-" * 80)
        return False


def test_simple_joins(conn):
    """Test basic JOIN queries"""
    print_section("TEST 1: Simple JOIN Queries")
    
    # Test 1.1: INNER JOIN - Orders with Customer Names
    query1 = """
    SELECT 
        O.ORDER_ID,
        C.FIRST_NAME,
        C.LAST_NAME,
        O.ORDER_DATE,
        O.TOTAL_AMOUNT,
        O.ORDER_STATUS
    FROM ORDERS O
    INNER JOIN CUSTOMERS C ON O.CUSTOMER_ID = C.CUSTOMER_ID
    ORDER BY O.ORDER_DATE DESC
    FETCH FIRST 5 ROWS ONLY
    """
    execute_query(conn, query1, "Orders with Customer Names (INNER JOIN)")
    
    # Test 1.2: LEFT JOIN - All Customers with Order Count
    query2 = """
    SELECT 
        C.CUSTOMER_ID,
        C.FIRST_NAME,
        C.LAST_NAME,
        COUNT(O.ORDER_ID) AS ORDER_COUNT
    FROM CUSTOMERS C
    LEFT JOIN ORDERS O ON C.CUSTOMER_ID = O.CUSTOMER_ID
    GROUP BY C.CUSTOMER_ID, C.FIRST_NAME, C.LAST_NAME
    ORDER BY ORDER_COUNT DESC
    """
    execute_query(conn, query2, "All Customers with Order Count (LEFT JOIN + GROUP BY)")


def test_multi_table_joins(conn):
    """Test complex multi-table JOINs"""
    print_section("TEST 2: Multi-Table JOIN Queries")
    
    # Test 2.1: 3-Table JOIN - Order Details with Customer and Product Info
    query1 = """
    SELECT 
        C.FIRST_NAME || ' ' || C.LAST_NAME AS CUSTOMER_NAME,
        O.ORDER_ID,
        O.ORDER_DATE,
        P.NAME AS PRODUCT_NAME,
        OI.QUANTITY,
        OI.UNIT_PRICE,
        OI.LINE_TOTAL
    FROM ORDER_ITEMS OI
    INNER JOIN ORDERS O ON OI.ORDER_ID = O.ORDER_ID
    INNER JOIN CUSTOMERS C ON O.CUSTOMER_ID = C.CUSTOMER_ID
    INNER JOIN PRODUCTS P ON OI.PRODUCT_ID = P.PRODUCT_ID
    ORDER BY O.ORDER_DATE DESC, O.ORDER_ID, OI.ORDER_ITEM_ID
    FETCH FIRST 10 ROWS ONLY
    """
    execute_query(conn, query1, "Order Details with Customer and Product (3-Table JOIN)")
    
    # Test 2.2: 4-Table JOIN - Products with Synergies and Order History
    query2 = """
    SELECT 
        P1.NAME AS PRODUCT_1,
        P2.NAME AS PRODUCT_2,
        S.SYNERGY_SCORE,
        COUNT(DISTINCT OI.ORDER_ID) AS TIMES_ORDERED_TOGETHER
    FROM SYNERGIES S
    INNER JOIN PRODUCTS P1 ON S.PRODUCT_ID_1 = P1.PRODUCT_ID
    INNER JOIN PRODUCTS P2 ON S.PRODUCT_ID_2 = P2.PRODUCT_ID
    LEFT JOIN ORDER_ITEMS OI ON OI.PRODUCT_ID = P1.PRODUCT_ID
    GROUP BY P1.NAME, P2.NAME, S.SYNERGY_SCORE
    ORDER BY S.SYNERGY_SCORE DESC
    FETCH FIRST 5 ROWS ONLY
    """
    execute_query(conn, query2, "Products with Synergies and Order History (4-Table JOIN)")


def test_aggregate_queries(conn):
    """Test aggregate functions"""
    print_section("TEST 3: Aggregate Queries (COUNT, SUM, AVG, MIN, MAX)")
    
    # Test 3.1: Customer Purchase Statistics
    query1 = """
    SELECT 
        C.CUSTOMER_ID,
        C.FIRST_NAME || ' ' || C.LAST_NAME AS CUSTOMER_NAME,
        COUNT(O.ORDER_ID) AS TOTAL_ORDERS,
        SUM(O.TOTAL_AMOUNT) AS TOTAL_SPENT,
        AVG(O.TOTAL_AMOUNT) AS AVG_ORDER_VALUE,
        MIN(O.TOTAL_AMOUNT) AS MIN_ORDER,
        MAX(O.TOTAL_AMOUNT) AS MAX_ORDER
    FROM CUSTOMERS C
    LEFT JOIN ORDERS O ON C.CUSTOMER_ID = O.CUSTOMER_ID
    GROUP BY C.CUSTOMER_ID, C.FIRST_NAME, C.LAST_NAME
    HAVING COUNT(O.ORDER_ID) > 0
    ORDER BY TOTAL_SPENT DESC
    """
    execute_query(conn, query1, "Customer Purchase Statistics")
    
    # Test 3.2: Product Sales Summary
    query2 = """
    SELECT 
        P.PRODUCT_ID,
        P.NAME AS PRODUCT_NAME,
        P.PRICE AS CURRENT_PRICE,
        COUNT(OI.ORDER_ITEM_ID) AS TIMES_SOLD,
        SUM(OI.QUANTITY) AS TOTAL_QUANTITY_SOLD,
        SUM(OI.LINE_TOTAL) AS TOTAL_REVENUE,
        AVG(OI.UNIT_PRICE) AS AVG_SELLING_PRICE
    FROM PRODUCTS P
    LEFT JOIN ORDER_ITEMS OI ON P.PRODUCT_ID = OI.PRODUCT_ID
    GROUP BY P.PRODUCT_ID, P.NAME, P.PRICE
    ORDER BY TOTAL_REVENUE DESC
    """
    execute_query(conn, query2, "Product Sales Summary")
    
    # Test 3.3: Order Status Distribution
    query3 = """
    SELECT 
        ORDER_STATUS,
        COUNT(*) AS ORDER_COUNT,
        SUM(TOTAL_AMOUNT) AS TOTAL_VALUE,
        AVG(TOTAL_AMOUNT) AS AVG_VALUE
    FROM ORDERS
    GROUP BY ORDER_STATUS
    ORDER BY ORDER_COUNT DESC
    """
    execute_query(conn, query3, "Order Status Distribution")


def test_subqueries(conn):
    """Test subqueries"""
    print_section("TEST 4: Subqueries")
    
    # Test 4.1: Customers with Above-Average Spending
    query1 = """
    SELECT 
        C.CUSTOMER_ID,
        C.FIRST_NAME || ' ' || C.LAST_NAME AS CUSTOMER_NAME,
        SUM(O.TOTAL_AMOUNT) AS TOTAL_SPENT
    FROM CUSTOMERS C
    INNER JOIN ORDERS O ON C.CUSTOMER_ID = O.CUSTOMER_ID
    GROUP BY C.CUSTOMER_ID, C.FIRST_NAME, C.LAST_NAME
    HAVING SUM(O.TOTAL_AMOUNT) > (
        SELECT AVG(TOTAL_AMOUNT) 
        FROM ORDERS
    )
    ORDER BY TOTAL_SPENT DESC
    """
    execute_query(conn, query1, "Customers with Above-Average Spending (Subquery in HAVING)")
    
    # Test 4.2: Products Never Ordered
    query2 = """
    SELECT 
        P.PRODUCT_ID,
        P.NAME,
        P.PRICE
    FROM PRODUCTS P
    WHERE P.PRODUCT_ID NOT IN (
        SELECT DISTINCT PRODUCT_ID 
        FROM ORDER_ITEMS
    )
    ORDER BY P.PRICE DESC
    """
    execute_query(conn, query2, "Products Never Ordered (Subquery with NOT IN)")
    
    # Test 4.3: Top 3 Products by Revenue (Correlated Subquery)
    query3 = """
    SELECT 
        P.PRODUCT_ID,
        P.NAME,
        (SELECT SUM(OI.LINE_TOTAL) 
         FROM ORDER_ITEMS OI 
         WHERE OI.PRODUCT_ID = P.PRODUCT_ID) AS TOTAL_REVENUE
    FROM PRODUCTS P
    WHERE (SELECT SUM(OI.LINE_TOTAL) 
           FROM ORDER_ITEMS OI 
           WHERE OI.PRODUCT_ID = P.PRODUCT_ID) IS NOT NULL
    ORDER BY TOTAL_REVENUE DESC
    FETCH FIRST 3 ROWS ONLY
    """
    execute_query(conn, query3, "Top 3 Products by Revenue (Correlated Subquery)")


def test_complex_where_clauses(conn):
    """Test complex WHERE clauses"""
    print_section("TEST 5: Complex WHERE Clauses")
    
    # Test 5.1: Multiple Conditions with AND/OR
    query1 = """
    SELECT 
        O.ORDER_ID,
        C.FIRST_NAME || ' ' || C.LAST_NAME AS CUSTOMER_NAME,
        O.ORDER_DATE,
        O.TOTAL_AMOUNT,
        O.ORDER_STATUS
    FROM ORDERS O
    INNER JOIN CUSTOMERS C ON O.CUSTOMER_ID = C.CUSTOMER_ID
    WHERE (O.ORDER_STATUS = 'DELIVERED' OR O.ORDER_STATUS = 'SHIPPED')
      AND O.TOTAL_AMOUNT > 500
      AND O.ORDER_DATE >= '2024-02-01'
    ORDER BY O.TOTAL_AMOUNT DESC
    """
    execute_query(conn, query1, "Orders: Delivered/Shipped, >$500, After Feb 2024")
    
    # Test 5.2: BETWEEN and IN Operators
    query2 = """
    SELECT 
        P.PRODUCT_ID,
        P.NAME,
        P.PRICE
    FROM PRODUCTS P
    WHERE P.PRICE BETWEEN 50 AND 200
      AND P.PRODUCT_ID IN (
          SELECT DISTINCT PRODUCT_ID 
          FROM ORDER_ITEMS
      )
    ORDER BY P.PRICE
    """
    execute_query(conn, query2, "Products: Price $50-$200 and Have Orders (BETWEEN + IN)")
    
    # Test 5.3: LIKE Pattern Matching
    query3 = """
    SELECT 
        CUSTOMER_ID,
        FIRST_NAME,
        LAST_NAME,
        EMAIL
    FROM CUSTOMERS
    WHERE EMAIL LIKE '%example.com'
      AND (FIRST_NAME LIKE 'J%' OR LAST_NAME LIKE 'J%')
    ORDER BY LAST_NAME, FIRST_NAME
    """
    execute_query(conn, query3, "Customers: Email @example.com, Name starts with J (LIKE)")


def test_advanced_analytics(conn):
    """Test advanced analytical queries"""
    print_section("TEST 6: Advanced Analytics")
    
    # Test 6.1: Customer Lifetime Value with Ranking
    query1 = """
    SELECT 
        C.CUSTOMER_ID,
        C.FIRST_NAME || ' ' || C.LAST_NAME AS CUSTOMER_NAME,
        C.LOYALTY_POINTS,
        COUNT(O.ORDER_ID) AS ORDER_COUNT,
        SUM(O.TOTAL_AMOUNT) AS LIFETIME_VALUE,
        CASE 
            WHEN SUM(O.TOTAL_AMOUNT) > 2000 THEN 'VIP'
            WHEN SUM(O.TOTAL_AMOUNT) > 1000 THEN 'GOLD'
            WHEN SUM(O.TOTAL_AMOUNT) > 500 THEN 'SILVER'
            ELSE 'BRONZE'
        END AS CUSTOMER_TIER
    FROM CUSTOMERS C
    LEFT JOIN ORDERS O ON C.CUSTOMER_ID = O.CUSTOMER_ID
    GROUP BY C.CUSTOMER_ID, C.FIRST_NAME, C.LAST_NAME, C.LOYALTY_POINTS
    ORDER BY LIFETIME_VALUE DESC
    """
    execute_query(conn, query1, "Customer Lifetime Value with Tier Classification (CASE)")
    
    # Test 6.2: Product Performance with Discount Analysis
    query2 = """
    SELECT 
        P.NAME AS PRODUCT_NAME,
        COUNT(OI.ORDER_ITEM_ID) AS TIMES_SOLD,
        SUM(OI.QUANTITY) AS TOTAL_UNITS,
        AVG(OI.DISCOUNT_PERCENT) AS AVG_DISCOUNT,
        SUM(CASE WHEN OI.DISCOUNT_PERCENT > 0 THEN 1 ELSE 0 END) AS DISCOUNTED_SALES,
        SUM(OI.LINE_TOTAL) AS TOTAL_REVENUE
    FROM PRODUCTS P
    INNER JOIN ORDER_ITEMS OI ON P.PRODUCT_ID = OI.PRODUCT_ID
    GROUP BY P.NAME
    HAVING COUNT(OI.ORDER_ITEM_ID) > 0
    ORDER BY TOTAL_REVENUE DESC
    """
    execute_query(conn, query2, "Product Performance with Discount Analysis")
    
    # Test 6.3: Monthly Order Trends
    query3 = """
    SELECT 
        YEAR(ORDER_DATE) AS ORDER_YEAR,
        MONTH(ORDER_DATE) AS ORDER_MONTH,
        COUNT(*) AS ORDER_COUNT,
        SUM(TOTAL_AMOUNT) AS MONTHLY_REVENUE,
        AVG(TOTAL_AMOUNT) AS AVG_ORDER_VALUE
    FROM ORDERS
    GROUP BY YEAR(ORDER_DATE), MONTH(ORDER_DATE)
    ORDER BY ORDER_YEAR DESC, ORDER_MONTH DESC
    """
    execute_query(conn, query3, "Monthly Order Trends (Date Functions + GROUP BY)")


def test_cross_table_analytics(conn):
    """Test cross-table analytical queries"""
    print_section("TEST 7: Cross-Table Analytics")
    
    # Test 7.1: Product Bundle Analysis (Products Bought Together)
    query1 = """
    SELECT 
        P1.NAME AS PRODUCT_1,
        P2.NAME AS PRODUCT_2,
        COUNT(*) AS TIMES_BOUGHT_TOGETHER
    FROM ORDER_ITEMS OI1
    INNER JOIN ORDER_ITEMS OI2 
        ON OI1.ORDER_ID = OI2.ORDER_ID 
        AND OI1.PRODUCT_ID < OI2.PRODUCT_ID
    INNER JOIN PRODUCTS P1 ON OI1.PRODUCT_ID = P1.PRODUCT_ID
    INNER JOIN PRODUCTS P2 ON OI2.PRODUCT_ID = P2.PRODUCT_ID
    GROUP BY P1.NAME, P2.NAME
    HAVING COUNT(*) > 0
    ORDER BY TIMES_BOUGHT_TOGETHER DESC
    FETCH FIRST 5 ROWS ONLY
    """
    execute_query(conn, query1, "Product Bundle Analysis (Self-JOIN)")
    
    # Test 7.2: Customer Segmentation by Purchase Behavior
    query2 = """
    SELECT 
        CASE 
            WHEN ORDER_COUNT >= 3 THEN 'FREQUENT'
            WHEN ORDER_COUNT = 2 THEN 'REGULAR'
            ELSE 'OCCASIONAL'
        END AS CUSTOMER_SEGMENT,
        COUNT(*) AS CUSTOMER_COUNT,
        AVG(TOTAL_SPENT) AS AVG_SPENDING,
        SUM(TOTAL_SPENT) AS SEGMENT_REVENUE
    FROM (
        SELECT 
            C.CUSTOMER_ID,
            COUNT(O.ORDER_ID) AS ORDER_COUNT,
            COALESCE(SUM(O.TOTAL_AMOUNT), 0) AS TOTAL_SPENT
        FROM CUSTOMERS C
        LEFT JOIN ORDERS O ON C.CUSTOMER_ID = O.CUSTOMER_ID
        GROUP BY C.CUSTOMER_ID
    ) AS CUSTOMER_STATS
    GROUP BY 
        CASE 
            WHEN ORDER_COUNT >= 3 THEN 'FREQUENT'
            WHEN ORDER_COUNT = 2 THEN 'REGULAR'
            ELSE 'OCCASIONAL'
        END
    ORDER BY SEGMENT_REVENUE DESC
    """
    execute_query(conn, query2, "Customer Segmentation by Purchase Behavior (Nested Query)")


def main():
    """Main test execution"""
    print("=" * 80)
    print("  COMPLEX QUERY TESTING SUITE")
    print("  Testing JOINs, Aggregates, Subqueries, and Advanced SQL")
    print("=" * 80)
    
    # Connect to DB2
    print("\n🔌 Connecting to DB2...")
    conn = connect_to_db2()
    print("✅ Connected to DB2")
    
    try:
        # Run all test suites
        test_simple_joins(conn)
        test_multi_table_joins(conn)
        test_aggregate_queries(conn)
        test_subqueries(conn)
        test_complex_where_clauses(conn)
        test_advanced_analytics(conn)
        test_cross_table_analytics(conn)
        
        # Final summary
        print_section("FINAL SUMMARY")
        print("\n✅ All complex query tests completed!")
        print("\n📊 Query Types Tested:")
        print("  ✅ Simple JOINs (INNER, LEFT)")
        print("  ✅ Multi-table JOINs (3-4 tables)")
        print("  ✅ Aggregate functions (COUNT, SUM, AVG, MIN, MAX)")
        print("  ✅ GROUP BY with HAVING")
        print("  ✅ Subqueries (IN, NOT IN, Correlated)")
        print("  ✅ Complex WHERE clauses (AND, OR, BETWEEN, LIKE)")
        print("  ✅ CASE statements")
        print("  ✅ Date functions")
        print("  ✅ Self-JOINs")
        print("  ✅ Nested queries")
        print("\n" + "=" * 80)
        
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
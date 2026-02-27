# DB2 Quick Start Guide

## Connect to DB2 and Run Queries

### Step 1: Connect to Container
```bash
podman exec -it product-synergy-db2 su - db2inst1
```

### Step 2: Connect to Database (IMPORTANT!)
```bash
db2 connect to proddb
```

You should see:
```
   Database Connection Information

 Database server        = DB2/LINUXX8664 11.5.8.0
 SQL authorization ID   = DB2INST1
 Local database alias   = PRODDB
```

### Step 3: Run Queries
```bash
# View all products
db2 "SELECT * FROM PRODUCTS"

# View all customers
db2 "SELECT * FROM CUSTOMERS"

# Count orders
db2 "SELECT COUNT(*) FROM ORDERS"

# Complex query - Products with order counts
db2 "SELECT P.NAME, COUNT(OI.ORDER_ITEM_ID) AS ORDER_COUNT FROM PRODUCTS P LEFT JOIN ORDER_ITEMS OI ON P.PRODUCT_ID = OI.PRODUCT_ID GROUP BY P.NAME ORDER BY ORDER_COUNT DESC"
```

### Step 4: Disconnect When Done
```bash
db2 connect reset
exit
```

---

## Complete Example Session

```bash
# 1. Enter container
podman exec -it product-synergy-db2 su - db2inst1

# 2. Connect to database
db2 connect to proddb

# 3. Run queries
db2 "SELECT * FROM PRODUCTS"
db2 "SELECT * FROM CUSTOMERS"
db2 "SELECT * FROM ORDERS"

# 4. Disconnect
db2 connect reset
exit
```

---

## Common Queries

### View All Tables
```bash
db2 "SELECT TABNAME FROM SYSCAT.TABLES WHERE TABSCHEMA = CURRENT SCHEMA ORDER BY TABNAME"
```

### Count Records in Each Table
```bash
db2 "SELECT COUNT(*) FROM PRODUCTS"
db2 "SELECT COUNT(*) FROM CUSTOMERS"
db2 "SELECT COUNT(*) FROM ORDERS"
db2 "SELECT COUNT(*) FROM ORDER_ITEMS"
db2 "SELECT COUNT(*) FROM SYNERGIES"
```

### View Table Structure
```bash
db2 "DESCRIBE TABLE PRODUCTS"
```

### Complex Queries

#### Products with Total Revenue
```bash
db2 "SELECT P.NAME, SUM(OI.LINE_TOTAL) AS TOTAL_REVENUE FROM PRODUCTS P LEFT JOIN ORDER_ITEMS OI ON P.PRODUCT_ID = OI.PRODUCT_ID GROUP BY P.NAME ORDER BY TOTAL_REVENUE DESC"
```

#### Customers with Order Count
```bash
db2 "SELECT C.FIRST_NAME, C.LAST_NAME, COUNT(O.ORDER_ID) AS ORDER_COUNT FROM CUSTOMERS C LEFT JOIN ORDERS O ON C.CUSTOMER_ID = O.CUSTOMER_ID GROUP BY C.FIRST_NAME, C.LAST_NAME ORDER BY ORDER_COUNT DESC"
```

#### Top Product Synergies
```bash
db2 "SELECT P1.NAME AS PRODUCT_1, P2.NAME AS PRODUCT_2, S.SYNERGY_SCORE FROM SYNERGIES S JOIN PRODUCTS P1 ON S.PRODUCT_ID_1 = P1.PRODUCT_ID JOIN PRODUCTS P2 ON S.PRODUCT_ID_2 = P2.PRODUCT_ID ORDER BY S.SYNERGY_SCORE DESC"
```

---

## Troubleshooting

### Error: "SQL1024N A database connection does not exist"
**Solution**: You forgot to run `db2 connect to proddb`

```bash
# Always connect first!
db2 connect to proddb
```

### Error: "SQL0204N name is an undefined name"
**Solution**: Table doesn't exist or wrong name

```bash
# Check available tables
db2 "SELECT TABNAME FROM SYSCAT.TABLES WHERE TABSCHEMA = CURRENT SCHEMA"
```

### Check Connection Status
```bash
db2 list active databases
```

---

## Python Connection Example

```python
import ibm_db

# Connection string
dsn = "DATABASE=proddb;HOSTNAME=localhost;PORT=5001;PROTOCOL=TCPIP;UID=db2inst1;PWD=password"

# Connect
conn = ibm_db.connect(dsn, "", "")
print("✅ Connected to DB2!")

# Query
sql = "SELECT * FROM PRODUCTS"
stmt = ibm_db.exec_immediate(conn, sql)

# Fetch results
print("\nProducts:")
while ibm_db.fetch_row(stmt):
    product_id = ibm_db.result(stmt, 0)
    name = ibm_db.result(stmt, 1)
    price = ibm_db.result(stmt, 2)
    print(f"  {product_id}: {name} - ${price}")

# Close
ibm_db.close(conn)
```

---

## Quick Reference

| Command | Description |
|---------|-------------|
| `db2 connect to proddb` | Connect to database |
| `db2 "SELECT * FROM table"` | Query table |
| `db2 list tables` | List all tables |
| `db2 connect reset` | Disconnect |
| `db2 terminate` | End DB2 session |

---

## Your Data Summary

- **PRODUCTS**: 5 records
- **CUSTOMERS**: 5 records
- **ORDERS**: 7 records
- **ORDER_ITEMS**: 13 records
- **SYNERGIES**: 5 records
- **DATATYPE_TEST**: 2 records
- **ORACLE_DATATYPE_COMPREHENSIVE**: 2 records

**Total**: 39 records across 7 tables
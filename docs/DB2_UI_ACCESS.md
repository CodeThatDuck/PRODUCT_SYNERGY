# DB2 Database - UI Access Guide

## ✅ CONFIRMED: Data is in DB2

### Current Data in DB2:
```
Database: proddb
Port: 5001
Tables: 7 tables
Records: 35 records

PRODUCTS: 5 records
CUSTOMERS: 5 records
ORDERS: 7 records
ORDER_ITEMS: 13 records
SYNERGIES: 5 records
```

### Sample Data Verification:
```
PRODUCT_ID | NAME                    | PRICE
-----------|-------------------------|--------
1001       | Gaming Laptop Pro       | 1299.99
1002       | Wireless Mouse Elite    | 49.95
1003       | Mechanical Keyboard RGB | 129.00
1004       | 4K Monitor Ultra        | 599.99
1005       | USB-C Hub               | 79.99
```

---

## Option 1: DBeaver (Recommended - Free & Easy) ⭐

### DB2 Version Information:
```
Database: DB2 for LUW (Linux, UNIX, and Windows)
Version: DB2 v11.5.8.0
Platform: 64-bit AMD64
```

### Install DBeaver:
```bash
# macOS
brew install --cask dbeaver-community

# Or download from: https://dbeaver.io/download/
```

### Connect to DB2:
1. Open DBeaver
2. Click **Database** → **New Database Connection**
3. Select **IBM DB2 for LUW** (DB2 for Linux, UNIX, and Windows)
4. Enter connection details:
   ```
   Host: localhost
   Port: 5001
   Database: proddb
   Username: db2inst1
   Password: password
   ```
5. Click **Test Connection**
6. Click **Finish**

### Browse Data:
- Expand **proddb** → **DB2INST1** → **Tables**
- Double-click any table to view data
- Right-click table → **View Data** for full view

---

## Option 2: IBM Data Studio (Official IBM Tool)

### Download:
https://www.ibm.com/products/data-studio

### Connect:
1. Open IBM Data Studio
2. Right-click **Database Connections** → **New**
3. Select **IBM DB2 for Linux, UNIX, and Windows**
4. Enter:
   ```
   Host: localhost
   Port: 5001
   Database: proddb
   User ID: db2inst1
   Password: password
   ```
5. Click **Test Connection**
6. Click **Finish**

---

## Option 3: VS Code Extension

### Install Extension:
1. Open VS Code
2. Go to Extensions (Cmd+Shift+X)
3. Search for **"SQLTools"**
4. Install **SQLTools** and **SQLTools DB2 Driver**

### Connect:
1. Click SQLTools icon in sidebar
2. Click **Add New Connection**
3. Select **DB2**
4. Enter:
   ```
   Connection Name: Product Synergy DB2
   Server: localhost
   Port: 5001
   Database: proddb
   Username: db2inst1
   Password: password
   ```
5. Click **Test Connection**
6. Click **Save Connection**

### Query Data:
- Click on connection
- Click **New SQL File**
- Write queries:
  ```sql
  SELECT * FROM PRODUCTS;
  SELECT * FROM CUSTOMERS;
  ```

---

## Option 4: Python Script with GUI Output

Create a simple Python script to view data:

```python
#!/usr/bin/env python3
"""
DB2 Data Viewer - Simple GUI
"""

import ibm_db
import pandas as pd

# Connect to DB2
dsn = "DATABASE=proddb;HOSTNAME=localhost;PORT=5001;PROTOCOL=TCPIP;UID=db2inst1;PWD=password"
conn = ibm_db.connect(dsn, "", "")

# Function to query and display
def view_table(table_name):
    sql = f"SELECT * FROM {table_name}"
    stmt = ibm_db.exec_immediate(conn, sql)
    
    # Fetch all rows
    rows = []
    result = ibm_db.fetch_tuple(stmt)
    while result:
        rows.append(result)
        result = ibm_db.fetch_tuple(stmt)
    
    # Create DataFrame
    df = pd.DataFrame(rows)
    print(f"\n{'='*60}")
    print(f"Table: {table_name}")
    print(f"{'='*60}")
    print(df.to_string(index=False))
    print(f"\nTotal Records: {len(rows)}")

# View all tables
tables = ['PRODUCTS', 'CUSTOMERS', 'ORDERS', 'ORDER_ITEMS', 'SYNERGIES']
for table in tables:
    view_table(table)

ibm_db.close(conn)
```

Run it:
```bash
pip install pandas
python3 view_db2_data.py
```

---

## Option 5: Web-Based UI (Adminer)

### Run Adminer in Docker:
```bash
# Start Adminer
podman run -d \
  --name adminer \
  -p 8080:8080 \
  adminer

# Access at: http://localhost:8080
```

### Login:
```
System: DB2
Server: host.docker.internal:5001
Username: db2inst1
Password: password
Database: proddb
```

**Note**: Adminer may have limited DB2 support. DBeaver is recommended.

---

## Option 6: Command Line (Already Working)

### Quick View:
```bash
# Connect
podman exec -it product-synergy-db2 su - db2inst1

# Connect to database
db2 connect to proddb

# View data
db2 "SELECT * FROM PRODUCTS"
db2 "SELECT * FROM CUSTOMERS"
db2 "SELECT * FROM ORDERS"

# Disconnect
db2 connect reset
exit
```

---

## Recommended Setup for You

### Best Option: **DBeaver** ⭐

**Why?**
- ✅ Free and open source
- ✅ Easy to install on Mac
- ✅ Great UI for browsing data
- ✅ Supports all SQL operations
- ✅ Can export data to CSV, Excel, etc.

### Installation:
```bash
brew install --cask dbeaver-community
```

### Connection Details:
```
Host: localhost
Port: 5001
Database: proddb
Username: db2inst1
Password: password
```

---

## Verify Your Data

### Quick Verification Queries:

```sql
-- Count all records
SELECT 'PRODUCTS' AS TABLE_NAME, COUNT(*) AS RECORDS FROM PRODUCTS
UNION ALL
SELECT 'CUSTOMERS', COUNT(*) FROM CUSTOMERS
UNION ALL
SELECT 'ORDERS', COUNT(*) FROM ORDERS
UNION ALL
SELECT 'ORDER_ITEMS', COUNT(*) FROM ORDER_ITEMS
UNION ALL
SELECT 'SYNERGIES', COUNT(*) FROM SYNERGIES;

-- View products with revenue
SELECT 
    P.NAME,
    COUNT(OI.ORDER_ITEM_ID) AS ORDERS,
    SUM(OI.LINE_TOTAL) AS REVENUE
FROM PRODUCTS P
LEFT JOIN ORDER_ITEMS OI ON P.PRODUCT_ID = OI.PRODUCT_ID
GROUP BY P.NAME
ORDER BY REVENUE DESC;

-- View customers with order counts
SELECT 
    C.FIRST_NAME,
    C.LAST_NAME,
    COUNT(O.ORDER_ID) AS TOTAL_ORDERS
FROM CUSTOMERS C
LEFT JOIN ORDERS O ON C.CUSTOMER_ID = O.CUSTOMER_ID
GROUP BY C.FIRST_NAME, C.LAST_NAME
ORDER BY TOTAL_ORDERS DESC;
```

---

## Summary

✅ **Data is confirmed in DB2 database**
- 5 Products
- 5 Customers
- 7 Orders
- 13 Order Items
- 5 Synergies

✅ **Best UI Tool: DBeaver**
- Install: `brew install --cask dbeaver-community`
- Connect to: localhost:5001
- Database: proddb

✅ **Alternative: VS Code SQLTools Extension**
- Good for quick queries
- Integrated with your editor

**Your data is safely stored in DB2 and ready to view!** 🎉
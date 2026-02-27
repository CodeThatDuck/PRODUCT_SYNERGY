# DB2 Database Access via DBeaver - Complete Guide

## ✅ Verified Setup - Working Configuration

This guide documents the **working setup** for accessing the Product Synergy DB2 database using DBeaver Community Edition.

---

## Database Information

### DB2 Server Details:
```
Database Type: DB2 for LUW (Linux, UNIX, and Windows)
Version: DB2 v11.5.8.0
Container: product-synergy-db2
Database Name: proddb
Host: localhost
Port: 5001
Username: db2inst1
Password: password
```

### Data Summary:
```
Total Tables: 7
Total Records: 35

PRODUCTS: 5 records
CUSTOMERS: 5 records  
ORDERS: 7 records
ORDER_ITEMS: 13 records
SYNERGIES: 5 records
DATATYPE_TEST: 2 records
ORACLE_DATATYPE_COMPREHENSIVE: 2 records
```

---

## Step 1: Install DBeaver Community Edition

### For macOS:
```bash
# Using Homebrew (Recommended)
brew install --cask dbeaver-community

# Or download manually from:
# https://dbeaver.io/download/
```

### For Windows:
1. Download from: https://dbeaver.io/download/
2. Run the installer
3. Follow installation wizard

### For Linux:
```bash
# Ubuntu/Debian
sudo snap install dbeaver-ce

# Or download .deb/.rpm from:
# https://dbeaver.io/download/
```

---

## Step 2: Launch DBeaver

1. Open **DBeaver Community** application
2. Wait for the application to fully load
3. You'll see the main DBeaver window

---

## Step 3: Create New Database Connection

### 3.1 Start Connection Wizard:
1. Click **Database** menu (top menu bar)
2. Select **New Database Connection**
3. Or use shortcut: **Cmd+N** (Mac) / **Ctrl+N** (Windows/Linux)

### 3.2 Select Database Type:
1. In the connection wizard, search for **"DB2"**
2. You'll see multiple DB2 options:
   - **IBM DB2 for LUW** ⭐ **← SELECT THIS ONE**
   - IBM DB2 for i (iSeries)
   - IBM DB2 for z/OS (Mainframe)
3. Select **"IBM DB2 for LUW"** (DB2 for Linux, UNIX, and Windows)
4. Click **Next**

**Important for macOS users:**
- ✅ Choose: **IBM DB2 for LUW**
- ❌ Don't choose: DB2 for i or DB2 for z/OS
- LUW = Linux, UNIX, Windows (includes macOS)

---

## Step 4: Configure Connection Settings

### 4.1 Main Tab:
Enter the following details:

```
Host: localhost
Port: 5001
Database: proddb
Authentication: Database Native
Username: db2inst1
Password: password
```

**Detailed Steps:**
1. **Host**: Enter `localhost`
2. **Port**: Enter `5001`
3. **Database**: Enter `proddb`
4. **Authentication**: Select "Database Native" from dropdown
5. **Username**: Enter `db2inst1`
6. **Password**: Enter `password`
7. ✅ Check **"Save password"** (optional, for convenience)

### 4.2 Driver Settings (If Prompted):
- DBeaver will automatically download the DB2 JDBC driver
- Click **Download** if prompted
- Wait for driver download to complete
- Click **OK** when download finishes

---

## Step 5: Test Connection

### 5.1 Test the Connection:
1. Click **Test Connection** button (bottom left)
2. Wait for connection test to complete
3. You should see: ✅ **"Connected"** message

### 5.2 If Connection Fails:
Check the following:
- ✅ DB2 container is running: `podman ps | grep db2`
- ✅ Port 5001 is accessible: `lsof -i :5001`
- ✅ Credentials are correct (db2inst1/password)
- ✅ Database name is correct (proddb)

---

## Step 6: Finish Setup

1. Click **Finish** button
2. Connection will be created and saved
3. You'll see the connection in the **Database Navigator** panel (left side)

---

## Step 7: Browse Database

### 7.1 Expand Connection:
1. In **Database Navigator**, expand your connection
2. Expand **proddb** database
3. Expand **DB2INST1** schema
4. Expand **Tables** folder

### 7.2 View Tables:
You should see 7 tables:
- CUSTOMERS
- DATATYPE_TEST
- ORACLE_DATATYPE_COMPREHENSIVE
- ORDERS
- ORDER_ITEMS
- PRODUCTS
- SYNERGIES

---

## Step 8: View Data

### Method 1: Quick View
1. **Right-click** on any table (e.g., PRODUCTS)
2. Select **View Data**
3. Data will appear in the main panel

### Method 2: Double-Click
1. **Double-click** on any table
2. Click the **Data** tab in the main panel
3. Browse through the records

### Method 3: SQL Query
1. Click **SQL Editor** button (or press **Cmd+]** / **Ctrl+]**)
2. Write your query:
   ```sql
   SELECT * FROM PRODUCTS;
   ```
3. Press **Cmd+Enter** (Mac) or **Ctrl+Enter** (Windows/Linux) to execute
4. Results appear below

---

## Step 9: Useful Queries

### View All Products:
```sql
SELECT * FROM PRODUCTS;
```

### View Customers:
```sql
SELECT * FROM CUSTOMERS;
```

### View Orders with Customer Names:
```sql
SELECT 
    O.ORDER_ID,
    C.FIRST_NAME || ' ' || C.LAST_NAME AS CUSTOMER_NAME,
    O.ORDER_DATE,
    O.ORDER_STATUS,
    O.TOTAL_AMOUNT
FROM ORDERS O
JOIN CUSTOMERS C ON O.CUSTOMER_ID = C.CUSTOMER_ID
ORDER BY O.ORDER_DATE DESC;
```

### Products with Revenue:
```sql
SELECT 
    P.NAME AS PRODUCT_NAME,
    COUNT(OI.ORDER_ITEM_ID) AS TIMES_ORDERED,
    SUM(OI.LINE_TOTAL) AS TOTAL_REVENUE
FROM PRODUCTS P
LEFT JOIN ORDER_ITEMS OI ON P.PRODUCT_ID = OI.PRODUCT_ID
GROUP BY P.NAME
ORDER BY TOTAL_REVENUE DESC;
```

### Top Customers by Orders:
```sql
SELECT 
    C.FIRST_NAME,
    C.LAST_NAME,
    C.EMAIL,
    COUNT(O.ORDER_ID) AS TOTAL_ORDERS,
    SUM(O.TOTAL_AMOUNT) AS TOTAL_SPENT
FROM CUSTOMERS C
LEFT JOIN ORDERS O ON C.CUSTOMER_ID = O.CUSTOMER_ID
GROUP BY C.FIRST_NAME, C.LAST_NAME, C.EMAIL
ORDER BY TOTAL_ORDERS DESC;
```

---

## Step 10: Export Data (Optional)

### Export to CSV:
1. Right-click on a table
2. Select **Export Data**
3. Choose **CSV** format
4. Select destination folder
5. Click **Proceed**

### Export to Excel:
1. Right-click on a table
2. Select **Export Data**
3. Choose **Excel** format
4. Select destination folder
5. Click **Proceed**

---

## Troubleshooting

### Issue 1: "Cannot connect to database"
**Solution:**
```bash
# Check if DB2 container is running
podman ps | grep db2

# If not running, start it
podman start product-synergy-db2

# Wait 30 seconds, then try connecting again
```

### Issue 2: "Driver not found"
**Solution:**
1. Go to **Database** → **Driver Manager**
2. Find **IBM DB2 for LUW**
3. Click **Download/Update**
4. Wait for download to complete
5. Try connecting again

### Issue 3: "Authentication failed"
**Solution:**
- Verify username: `db2inst1`
- Verify password: `password`
- Verify database: `proddb`

### Issue 4: "Port already in use"
**Solution:**
```bash
# Check what's using port 5001
lsof -i :5001

# If it's not DB2, change the port in podman-compose.yml
```

---

## DBeaver Tips & Tricks

### Keyboard Shortcuts:
- **Cmd/Ctrl + Enter**: Execute SQL query
- **Cmd/Ctrl + N**: New connection
- **Cmd/Ctrl + ]**: Open SQL Editor
- **Cmd/Ctrl + Shift + F**: Format SQL
- **F5**: Refresh

### Useful Features:
1. **Auto-complete**: Start typing SQL and press **Ctrl+Space**
2. **ER Diagram**: Right-click database → **View Diagram**
3. **Data Export**: Right-click table → **Export Data**
4. **SQL History**: View → SQL History
5. **Dark Theme**: Window → Preferences → Appearance → Theme

---

## Verification Checklist

After setup, verify everything is working:

- [ ] DBeaver installed successfully
- [ ] Connection created to localhost:5001
- [ ] Connection test passed
- [ ] Can see 7 tables in DB2INST1 schema
- [ ] Can view PRODUCTS table (5 records)
- [ ] Can view CUSTOMERS table (5 records)
- [ ] Can view ORDERS table (7 records)
- [ ] Can run SQL queries successfully
- [ ] Can export data to CSV/Excel

---

## Summary

✅ **DBeaver Community Edition** is now connected to your DB2 database!

**Connection Details:**
```
Host: localhost:5001
Database: proddb
Schema: DB2INST1
Tables: 7 tables with 35 records
```

**What You Can Do:**
- ✅ Browse all tables and data
- ✅ Run SQL queries
- ✅ Export data to CSV/Excel
- ✅ View table relationships
- ✅ Create ER diagrams
- ✅ Analyze data

**Next Steps:**
1. Explore the data in each table
2. Try the sample queries provided
3. Create your own queries
4. Export data as needed

---

## Support

### Documentation:
- DBeaver: https://dbeaver.io/docs/
- DB2: https://www.ibm.com/docs/en/db2/11.5

### Project Files:
- `MIGRATION_SUMMARY.md` - Complete migration details
- `docs/DB2_QUICK_START.md` - Command-line access
- `docs/DB2_UI_ACCESS.md` - Alternative UI tools

---

**Your DB2 database is ready to use with DBeaver!** 🎉
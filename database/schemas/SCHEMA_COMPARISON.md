# Oracle vs DB2 Schema Comparison

## Understanding Your Database Files

### 📁 File Structure
```
database/schemas/
├── oracle_source_schema.sql    ← ORIGINAL Oracle schema (what you HAD)
├── db2_target_schema.sql       ← CONVERTED DB2 schema (what you HAVE NOW)
└── product_synergy_schema.sql  ← LEGACY file (same as db2_target_schema.sql)
```

## Answer to Your Questions

### 1️⃣ Where are the Oracle and DB2 Files?

**Oracle File (Source):**
- 📄 `database/schemas/oracle_source_schema.sql`
- This represents your ORIGINAL Oracle database
- Uses Oracle-specific syntax (NUMBER, VARCHAR2)

**DB2 File (Target):**
- 📄 `database/schemas/db2_target_schema.sql`
- This represents your CURRENT DB2 database
- Uses DB2-native syntax (DECIMAL, VARCHAR)

**Yes, both use `.sql` extension!**
- Both Oracle and DB2 use SQL (Structured Query Language)
- The syntax is 95% the same
- Only data types differ slightly

### 2️⃣ Oracle File is NOT Overridden!

✅ **Your Oracle file is SAFE!**
- Oracle file: `oracle_source_schema.sql` (preserved)
- DB2 file: `db2_target_schema.sql` (separate file)
- They are TWO DIFFERENT FILES
- Neither overwrites the other

### 3️⃣ Understanding Your SQL Structure

## Your Database Structure Explained

### 📊 Table 1: PRODUCTS
**Purpose:** Stores information about products

| Column | Type | Description | Example |
|--------|------|-------------|---------|
| PRODUCT_ID | Number (10 digits) | Unique ID for each product | 1, 2, 3... |
| NAME | Text (up to 255 chars) | Product name | "Laptop", "Mouse" |
| PRICE | Decimal (10 digits, 2 decimal places) | Product price | 999.99, 29.99 |

**Constraints:**
- ✅ PRODUCT_ID is PRIMARY KEY (must be unique, cannot be null)
- ✅ NAME cannot be null (must have a name)
- ✅ PRICE cannot be null (must have a price)

**Current Data (24 products):**
```
ID  | NAME                    | PRICE
----|-------------------------|--------
1   | Laptop                  | 999.99
2   | Mouse                   | 29.99
3   | Keyboard                | 79.99
4   | Monitor                 | 299.99
5   | Headphones              | 149.99
... | (19 more products)      | ...
```

### 📊 Table 2: SYNERGIES
**Purpose:** Stores relationships between products (which products work well together)

| Column | Type | Description | Example |
|--------|------|-------------|---------|
| SYNERGY_ID | Number (10 digits) | Unique ID for each relationship | 1, 2, 3... |
| PRODUCT_ID_1 | Number (10 digits) | First product in the pair | 1 (Laptop) |
| PRODUCT_ID_2 | Number (10 digits) | Second product in the pair | 2 (Mouse) |
| SYNERGY_SCORE | Decimal (5 digits, 2 decimal) | How well they work together (0-100) | 85.50 |

**Constraints:**
- ✅ SYNERGY_ID is PRIMARY KEY (must be unique)
- ✅ PRODUCT_ID_1 is FOREIGN KEY → links to PRODUCTS table
- ✅ PRODUCT_ID_2 is FOREIGN KEY → links to PRODUCTS table
- ✅ PRODUCT_ID_1 and PRODUCT_ID_2 must be DIFFERENT (can't link product to itself)
- ✅ SYNERGY_SCORE must be between 0 and 100

**Current Data (10 synergies):**
```
ID | PRODUCT_1 | PRODUCT_2 | SCORE | Meaning
---|-----------|-----------|-------|---------------------------
1  | Laptop    | Mouse     | 85.50 | Laptop + Mouse work well together
2  | Laptop    | Keyboard  | 90.00 | Laptop + Keyboard work very well
3  | Laptop    | Monitor   | 95.00 | Laptop + Monitor work excellently
4  | Mouse     | Keyboard  | 75.00 | Mouse + Keyboard work okay
5  | Laptop    | Headphones| 80.00 | Laptop + Headphones work well
... (5 more synergies)
```

## Visual Relationship

```
┌─────────────────┐
│    PRODUCTS     │
├─────────────────┤
│ PRODUCT_ID (PK) │◄─────┐
│ NAME            │      │
│ PRICE           │      │
└─────────────────┘      │
                         │
                         │ FOREIGN KEY
                         │ (links tables)
                         │
┌─────────────────┐      │
│   SYNERGIES     │      │
├─────────────────┤      │
│ SYNERGY_ID (PK) │      │
│ PRODUCT_ID_1    │──────┘
│ PRODUCT_ID_2    │──────┐
│ SYNERGY_SCORE   │      │
└─────────────────┘      │
                         │
                         └─────► Links back to PRODUCTS
```

## Key Differences: Oracle vs DB2

### Side-by-Side Comparison

| Feature | Oracle Syntax | DB2 Syntax | Same? |
|---------|---------------|------------|-------|
| **Data Types** | | | |
| Integer | `NUMBER(10)` | `DECIMAL(10,0)` | ❌ Different |
| Decimal | `NUMBER(10,2)` | `DECIMAL(10,2)` | ❌ Different |
| Text | `VARCHAR2(255)` | `VARCHAR(255)` | ❌ Different |
| **Operators** | | | |
| Not Equal | `!=` | `<>` | ❌ Different (both work in DB2) |
| **Everything Else** | | | |
| CREATE TABLE | Same | Same | ✅ Same |
| PRIMARY KEY | Same | Same | ✅ Same |
| FOREIGN KEY | Same | Same | ✅ Same |
| CHECK | Same | Same | ✅ Same |
| INDEX | Same | Same | ✅ Same |
| INSERT | Same | Same | ✅ Same |
| COMMENT | Same | Same | ✅ Same |

### Example: Same Table, Different Syntax

**Oracle:**
```sql
CREATE TABLE PRODUCTS (
    PRODUCT_ID NUMBER(10) NOT NULL,      ← Oracle type
    NAME VARCHAR2(255) NOT NULL,         ← Oracle type
    PRICE NUMBER(10,2) NOT NULL
);
```

**DB2:**
```sql
CREATE TABLE PRODUCTS (
    PRODUCT_ID DECIMAL(10,0) NOT NULL,   ← DB2 type
    NAME VARCHAR(255) NOT NULL,          ← DB2 type
    PRICE DECIMAL(10,2) NOT NULL
);
```

**Result:** EXACTLY THE SAME TABLE! Just different type names.

## Summary

### Your Database Has:
- ✅ 2 main tables (PRODUCTS, SYNERGIES)
- ✅ 3 columns in PRODUCTS table
- ✅ 4 columns in SYNERGIES table
- ✅ 1 Primary Key per table
- ✅ 2 Foreign Keys in SYNERGIES (linking to PRODUCTS)
- ✅ 2 Check Constraints (data validation rules)
- ✅ 2 Indexes (for faster queries)

### Files You Have:
1. **`oracle_source_schema.sql`** - Original Oracle version (preserved)
2. **`db2_target_schema.sql`** - Converted DB2 version (active)
3. **`product_synergy_schema.sql`** - Legacy file (can be deleted)

### The Migration:
- ✅ Oracle schema → DB2 schema (CONVERTED)
- ✅ Oracle data → DB2 data (MIGRATED)
- ✅ Both files preserved (NO OVERRIDE)
- ✅ Structure identical (SAME TABLES)
- ✅ Only data types changed (NUMBER → DECIMAL, VARCHAR2 → VARCHAR)

**Your Oracle database has been successfully converted to DB2!** 🎉
#!/bin/bash
# Script to create DB2 schemas from the generated SQL file
# This script will execute the DB2 schema SQL in the running DB2 container

set -e  # Exit on error

echo "================================================"
echo "DB2 Schema Setup Script"
echo "================================================"

# Configuration
CONTAINER_NAME="product-synergy-db2"
DB_NAME="proddb"
DB_USER="db2inst1"
SCHEMA_FILE="../database/schemas/db2_generated_schema.sql"

# Check if container is running
echo "Checking if DB2 container is running..."
if ! podman ps | grep -q "$CONTAINER_NAME"; then
    echo "❌ Error: DB2 container '$CONTAINER_NAME' is not running"
    echo "Please start the container first using: podman-compose up -d"
    exit 1
fi

echo "✓ DB2 container is running"

# Wait for DB2 to be ready
echo ""
echo "Waiting for DB2 to be ready..."
MAX_ATTEMPTS=30
ATTEMPT=0

while [ $ATTEMPT -lt $MAX_ATTEMPTS ]; do
    if podman exec $CONTAINER_NAME su - $DB_USER -c "db2 connect to $DB_NAME" 2>/dev/null; then
        echo "✓ DB2 is ready!"
        podman exec $CONTAINER_NAME su - $DB_USER -c "db2 connect reset" 2>/dev/null
        break
    fi
    ATTEMPT=$((ATTEMPT + 1))
    echo "Attempt $ATTEMPT/$MAX_ATTEMPTS - DB2 not ready yet, waiting 10 seconds..."
    sleep 10
done

if [ $ATTEMPT -eq $MAX_ATTEMPTS ]; then
    echo "❌ Error: DB2 did not become ready in time"
    exit 1
fi

# Copy schema file to container
echo ""
echo "Copying schema file to container..."
podman cp "$SCHEMA_FILE" "$CONTAINER_NAME:/tmp/db2_schema.sql"
echo "✓ Schema file copied"

# Execute schema creation
echo ""
echo "Creating DB2 schemas..."
echo "================================================"

podman exec $CONTAINER_NAME su - $DB_USER -c "
db2 connect to $DB_NAME
db2 -tvf /tmp/db2_schema.sql
db2 connect reset
"

if [ $? -eq 0 ]; then
    echo ""
    echo "================================================"
    echo "✓ DB2 schemas created successfully!"
    echo "================================================"
    
    # List created tables
    echo ""
    echo "Listing created tables..."
    podman exec $CONTAINER_NAME su - $DB_USER -c "
    db2 connect to $DB_NAME
    db2 'SELECT TABNAME FROM SYSCAT.TABLES WHERE TABSCHEMA = CURRENT SCHEMA ORDER BY TABNAME'
    db2 connect reset
    "
else
    echo ""
    echo "================================================"
    echo "❌ Error: Failed to create DB2 schemas"
    echo "================================================"
    exit 1
fi

echo ""
echo "Schema setup complete!"

# Made with Bob

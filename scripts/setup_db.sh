#!/bin/bash
# Script to set up the SYNERGY_LOG table in DB2

echo "Waiting for DB2 to be ready..."
until podman exec product-synergy-db2 su - db2inst1 -c "db2 connect to proddb" 2>/dev/null; do
    echo "DB2 not ready yet, waiting 10 seconds..."
    sleep 10
done

echo "DB2 is ready! Creating table..."
podman exec product-synergy-db2 su - db2inst1 -c "
db2 connect to proddb
db2 'CREATE TABLE SYNERGY_LOG (EVENT_NAME VARCHAR(100), STATUS VARCHAR(50))'
db2 \"INSERT INTO SYNERGY_LOG VALUES ('Phase 0 Handshake', 'ACTIVE')\"
db2 'SELECT * FROM SYNERGY_LOG'
db2 connect reset
"

echo "Table created successfully!"

# Made with Bob

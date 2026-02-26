import ibm_db  # type: ignore
import sys

# Connection string using the new 'proddb' name with connection timeout
dsn = (
    "DATABASE=proddb;"
    "HOSTNAME=localhost;"
    "PORT=5001;"  # Changed from 5000 to 5001 (host port mapping)
    "PROTOCOL=TCPIP;"
    "UID=db2inst1;"
    "PWD=password;"
    "CONNECTTIMEOUT=30;"  # Add connection timeout of 30 seconds
)

def run_phase_0_validation():
    """
    Phase 0 validation test - verifies DB2 connection and SYNERGY_LOG table.
    
    This test ensures:
    1. DB2 container is running and accessible
    2. Database 'proddb' exists and is active
    3. SYNERGY_LOG table exists and contains expected data
    """
    print("=" * 60)
    print("PHASE 0: DATABASE CONNECTION VALIDATION")
    print("=" * 60)
    print("\nInitiating Phase 0 Handshake...")
    print("Target: DB2 at localhost:5001, Database: proddb")
    print("-" * 60)
    
    conn = None
    try:
        # Establish connection
        print("\n[1/3] Attempting database connection...")
        conn = ibm_db.connect(dsn, "", "")
        print("✅ Connection Established Successfully")

        # Query the log table we created in the bash step
        print("\n[2/3] Querying SYNERGY_LOG table...")
        sql = "SELECT EVENT_NAME, STATUS FROM SYNERGY_LOG"
        stmt = ibm_db.exec_immediate(conn, sql)  # type: ignore
        row = ibm_db.fetch_both(stmt)  # type: ignore

        print("\n[3/3] Validating data...")
        if row:
            print(f"✅ Database Data Verified")
            print(f"   Event: {row['EVENT_NAME']}")  # type: ignore
            print(f"   Status: {row['STATUS']}")  # type: ignore
            print("\n" + "=" * 60)
            print("✅ PHASE 0 COMPLETE: SYSTEM IS READY FOR SYNERGY")
            print("=" * 60)
            return True
        else:
            print("⚠️  SYNERGY_LOG table exists but contains no data")
            print("\nTroubleshooting: Run setup_db.sh to initialize the database")
            return False
        
    except Exception as e:
        error_msg = str(e)
        if "SQL0204N" in error_msg or "undefined name" in error_msg:
            print(f"\n⚠️  SYNERGY_LOG table does not exist yet")
            print(f"   This is expected for a fresh database")
            print("\nTroubleshooting: Run setup_db.sh to initialize the database")
            return False
        print(f"\n❌ DB2 Connection Error:")
        print(f"   {error_msg}")
        print("\nTroubleshooting steps:")
        print("1. Verify container is running:")
        print("   podman ps | grep db2")
        print("2. Check DB2 instance status:")
        print("   podman exec product-synergy-db2 su - db2inst1 -c 'db2pd -'")
        print("3. Verify database exists:")
        print("   podman exec product-synergy-db2 su - db2inst1 -c 'db2 list db directory'")
        print("4. Check if DB2 is fully initialized (may take 2-3 minutes after container start)")
        return False
        
    finally:
        # Always close the connection if it was opened
        if conn:
            try:
                ibm_db.close(conn)
                print("\n[INFO] Database connection closed")
            except:
                pass

if __name__ == "__main__":
    success = run_phase_0_validation()
    sys.exit(0 if success else 1)

# Made with Bob

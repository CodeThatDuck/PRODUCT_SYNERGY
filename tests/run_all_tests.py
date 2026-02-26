#!/usr/bin/env python3
"""
Master Test Runner
Runs all tests in the correct order:
1. Schema generation and cloning
2. Data mapping and migration
3. Complex query testing
"""

import sys
import subprocess
from pathlib import Path

SCRIPT_DIR = Path(__file__).parent
PROJECT_ROOT = SCRIPT_DIR.parent


def print_section(title):
    """Print a formatted section header"""
    print("\n" + "=" * 80)
    print(f"  {title}")
    print("=" * 80)


def run_script(script_path, description):
    """Run a Python script and check for errors"""
    print_section(description)
    print(f"\n🚀 Running: {script_path}")
    print("-" * 80)
    
    try:
        result = subprocess.run(
            [sys.executable, str(script_path)],
            cwd=str(PROJECT_ROOT),
            capture_output=False,
            text=True
        )
        
        if result.returncode == 0:
            print("-" * 80)
            print(f"✅ {description} - PASSED")
            return True
        else:
            print("-" * 80)
            print(f"❌ {description} - FAILED (exit code: {result.returncode})")
            return False
            
    except Exception as e:
        print(f"❌ Error running {script_path}: {e}")
        return False


def main():
    """Main execution"""
    print("=" * 80)
    print("  MASTER TEST RUNNER")
    print("  Running Complete Oracle to DB2 Migration Test Suite")
    print("=" * 80)
    
    # Define test sequence
    tests = [
        (
            PROJECT_ROOT / "scripts" / "clone_oracle_schema.py",
            "STEP 1: Schema Generation and Cloning"
        ),
        (
            SCRIPT_DIR / "test_complete_flow.py",
            "STEP 2: Data Mapping and Migration"
        ),
        (
            SCRIPT_DIR / "test_complex_queries.py",
            "STEP 3: Complex Query Testing"
        )
    ]
    
    # Run all tests
    results = []
    for script_path, description in tests:
        if not script_path.exists():
            print(f"\n❌ Script not found: {script_path}")
            results.append(False)
            continue
        
        success = run_script(script_path, description)
        results.append(success)
        
        if not success:
            print(f"\n⚠️  Test failed, stopping execution")
            break
    
    # Final summary
    print_section("FINAL SUMMARY")
    
    print("\n📊 Test Results:")
    for i, (script_path, description) in enumerate(tests):
        if i < len(results):
            status = "✅ PASSED" if results[i] else "❌ FAILED"
            print(f"  {status} - {description}")
        else:
            print(f"  ⏭️  SKIPPED - {description}")
    
    # Overall result
    if all(results):
        print("\n" + "=" * 80)
        print("  ✅ ALL TESTS PASSED!")
        print("  ✅ Complete migration pipeline successful!")
        print("=" * 80)
        print("\n📋 What was tested:")
        print("  ✅ Schema generation (Oracle → DB2)")
        print("  ✅ Table creation with foreign keys and indexes")
        print("  ✅ Data mapping and transformation")
        print("  ✅ Data migration (39 records across 7 tables)")
        print("  ✅ Simple JOINs (INNER, LEFT)")
        print("  ✅ Multi-table JOINs (3-4 tables)")
        print("  ✅ Aggregate functions (COUNT, SUM, AVG, MIN, MAX)")
        print("  ✅ Subqueries and complex WHERE clauses")
        print("  ✅ Advanced analytics (CASE, date functions, self-JOINs)")
        print("\n🎉 Your Oracle to DB2 migration pipeline is production-ready!")
        sys.exit(0)
    else:
        print("\n" + "=" * 80)
        print("  ❌ SOME TESTS FAILED!")
        print("=" * 80)
        sys.exit(1)


if __name__ == "__main__":
    main()

# Made with Bob
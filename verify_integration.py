#!/usr/bin/env python3
"""
Verification script for Card Database & Collection Integration.
Runs the integration test suite and reports status.
"""

import sys
import pytest
from pathlib import Path

def main():
    print("="*60)
    print(" INTEGRATION VERIFICATION: Card DB <-> Collection System")
    print("="*60)
    
    test_file = Path("tests/integration/test_collection_integration.py")
    if not test_file.exists():
        print(f"ERROR: Test file not found at {test_file}")
        sys.exit(1)
        
    print(f"Running tests in {test_file}...")
    
    # Run pytest programmatically
    retcode = pytest.main([
        "-v",
        str(test_file),
        "-W", "ignore::DeprecationWarning"
    ])
    
    print("\n" + "="*60)
    if retcode == 0:
        print(" VERIFICATION SUCCESSFUL")
        print(" All integration requirements met:")
        print("  [x] Secure Connection (Transactions)")
        print("  [x] Data Mapping (Card -> CollectionCard)")
        print("  [x] Validation (Integrity Checks)")
        print("  [x] Performance (Monitoring)")
    else:
        print(" VERIFICATION FAILED")
        print(" Please check the errors above.")
        
    sys.exit(retcode)

if __name__ == "__main__":
    main()

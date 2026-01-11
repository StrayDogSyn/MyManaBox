#!/usr/bin/env python3
"""
Integration Test Runner for PROMPT 1.5
=======================================

Runs comprehensive tests on CSV import/export workflow with real data.
"""

import asyncio
import logging
import sys
import time
from pathlib import Path
from typing import Dict, List

import pytest

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
)
logger = logging.getLogger(__name__)


class TestRunner:
    """Runs PROMPT 1.5 integration tests."""
    
    def __init__(self):
        self.results = {}
        self.start_time = None
        self.end_time = None
    
    def print_header(self, title: str):
        """Print formatted section header."""
        print("\n" + "="*70)
        print(f"  {title}")
        print("="*70 + "\n")
    
    def print_subheader(self, title: str):
        """Print formatted subsection header."""
        print(f"\n{'-'*70}")
        print(f"  {title}")
        print(f"{'-'*70}\n")
    
    def run_pytest(self, path: str, verbose: bool = True) -> int:
        """Run pytest on a specific path."""
        args = [path]
        if verbose:
            args.append("-v")
        args.extend(["--tb=short", "-ra"])
        
        return pytest.main(args)
    
    def run_unit_tests(self) -> bool:
        """Run unit tests."""
        self.print_subheader("Phase 1: Unit Tests")
        
        logger.info("Running database unit tests...")
        result = self.run_pytest("tests/unit/test_database.py")
        
        self.results["unit_tests"] = {
            "status": "PASSED" if result == 0 else "FAILED",
            "exit_code": result,
        }
        
        return result == 0
    
    def run_csv_importer_tests(self) -> bool:
        """Run CSV importer integration tests."""
        self.print_subheader("Phase 2a: CSV Importer Tests")
        
        logger.info("Running CSV importer integration tests...")
        result = self.run_pytest(
            "tests/integration/test_import_workflow.py::TestCSVImporter"
        )
        
        self.results["csv_importer"] = {
            "status": "PASSED" if result == 0 else "FAILED",
            "exit_code": result,
        }
        
        return result == 0
    
    def run_backup_tests(self) -> bool:
        """Run backup manager tests."""
        self.print_subheader("Phase 2b: Backup Manager Tests")
        
        logger.info("Running backup manager tests...")
        result = self.run_pytest(
            "tests/integration/test_import_workflow.py::TestBackupManager"
        )
        
        self.results["backup_manager"] = {
            "status": "PASSED" if result == 0 else "FAILED",
            "exit_code": result,
        }
        
        return result == 0
    
    def run_migration_tests(self) -> bool:
        """Run migration manager tests."""
        self.print_subheader("Phase 2c: Migration Manager Tests")
        
        logger.info("Running migration manager tests...")
        result = self.run_pytest(
            "tests/integration/test_import_workflow.py::TestMigrationManager"
        )
        
        self.results["migration_manager"] = {
            "status": "PASSED" if result == 0 else "FAILED",
            "exit_code": result,
        }
        
        return result == 0
    
    def run_batch_insert_tests(self) -> bool:
        """Run batch insert service tests."""
        self.print_subheader("Phase 2d: Batch Insert Tests")
        
        logger.info("Running batch insert service tests...")
        result = self.run_pytest(
            "tests/integration/test_import_workflow.py::TestBatchInsertService"
        )
        
        self.results["batch_insert"] = {
            "status": "PASSED" if result == 0 else "FAILED",
            "exit_code": result,
        }
        
        return result == 0
    
    def run_end_to_end_tests(self) -> bool:
        """Run end-to-end workflow tests."""
        self.print_subheader("Phase 2e: End-to-End Workflow Tests")
        
        logger.info("Running end-to-end workflow tests...")
        result = self.run_pytest(
            "tests/integration/test_import_workflow.py::TestEndToEndWorkflow"
        )
        
        self.results["end_to_end"] = {
            "status": "PASSED" if result == 0 else "FAILED",
            "exit_code": result,
        }
        
        return result == 0
    
    def check_real_data(self) -> bool:
        """Check for real data file."""
        self.print_subheader("Phase 3: Real Data Validation Setup")
        
        csv_path = Path("data/imports/ManaBox_Collection_Bulk.csv")
        
        if csv_path.exists():
            size_mb = csv_path.stat().st_size / (1024 * 1024)
            logger.info(f"✓ Found real data file: {csv_path}")
            logger.info(f"  File size: {size_mb:.2f} MB")
            
            # Count lines
            with open(csv_path) as f:
                lines = sum(1 for _ in f) - 1  # Subtract header
            logger.info(f"  Cards: {lines:,}")
            
            self.results["real_data"] = {
                "status": "AVAILABLE",
                "path": str(csv_path),
                "size_mb": size_mb,
                "cards": lines,
            }
            
            return True
        else:
            logger.warning(f"✗ Real data file not found: {csv_path}")
            logger.warning("  Skipping real data tests (optional for full suite)")
            
            self.results["real_data"] = {
                "status": "NOT_FOUND",
                "path": str(csv_path),
            }
            
            return False
    
    def print_summary(self):
        """Print test results summary."""
        self.print_header("Test Results Summary")
        
        passed = sum(1 for r in self.results.values() 
                    if isinstance(r, dict) and r.get("status") == "PASSED")
        failed = sum(1 for r in self.results.values() 
                    if isinstance(r, dict) and r.get("status") == "FAILED")
        
        print(f"Tests Passed: {passed}")
        print(f"Tests Failed: {failed}")
        print(f"Total Suites: {len(self.results)}")
        
        if self.start_time and self.end_time:
            duration = self.end_time - self.start_time
            print(f"Duration: {duration:.1f} seconds")
        
        print("\nDetailed Results:")
        for name, result in self.results.items():
            if isinstance(result, dict):
                status = result.get("status", "UNKNOWN")
                symbol = "✓" if status == "PASSED" else "✗" if status == "FAILED" else "?"
                print(f"  {symbol} {name}: {status}")
        
        print("\n" + "="*70)
        
        if failed == 0:
            print("  ✓ ALL TESTS PASSED")
        else:
            print(f"  ✗ {failed} TEST SUITE(S) FAILED")
        
        print("="*70 + "\n")
        
        return failed == 0
    
    def run_all(self) -> int:
        """Run all test phases."""
        self.print_header("PROMPT 1.5 Integration Test Suite")
        logger.info("Starting comprehensive integration tests...")
        
        self.start_time = time.time()
        
        try:
            # Phase 1: Unit tests
            logger.info("Phase 1: Running unit tests...")
            unit_pass = self.run_unit_tests()
            
            # Phase 2: Integration tests
            logger.info("Phase 2: Running integration tests...")
            csv_pass = self.run_csv_importer_tests()
            backup_pass = self.run_backup_tests()
            migration_pass = self.run_migration_tests()
            batch_pass = self.run_batch_insert_tests()
            e2e_pass = self.run_end_to_end_tests()
            
            # Phase 3: Real data check
            logger.info("Phase 3: Checking real data...")
            real_data_available = self.check_real_data()
            
            self.end_time = time.time()
            
            # Print summary
            all_passed = (
                unit_pass and csv_pass and backup_pass and 
                migration_pass and batch_pass and e2e_pass
            )
            
            self.print_summary()
            
            if all_passed:
                logger.info("✓ All tests PASSED! Ready for real data validation.")
                if real_data_available:
                    logger.info("✓ Real data file available. Ready to import 3,830 cards.")
                return 0
            else:
                logger.error("✗ Some tests FAILED. Fix issues before proceeding.")
                return 1
        
        except Exception as e:
            logger.error(f"Test runner error: {e}", exc_info=True)
            return 2


def main():
    """Main entry point."""
    runner = TestRunner()
    exit_code = runner.run_all()
    sys.exit(exit_code)


if __name__ == "__main__":
    main()

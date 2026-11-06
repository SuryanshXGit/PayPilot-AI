"""
test_runner.py - Consolidated Test Suite Runner
Owned by Akashdeep (Product Data, Comparison & Testing Lead)

Executes all test suites:
1. test_bundle_scenarios.py
2. test_emergency_expense_scenarios.py
3. test_checkout_scenarios.py
4. test_data_integrity.py
"""

import unittest
import sys
import os

# Add project root to sys.path
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)


def run_all_tests():
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()

    test_dir = os.path.join(BASE_DIR, "tests")
    discovered = loader.discover(start_dir=test_dir, pattern="test_*.py")
    suite.addTests(discovered)

    print("======================================================================")
    print(" PAYPILOT AI 2.0 - AUTOMATED HACKATHON TEST SUITE (AKASHDEEP'S MODULE)")
    print("======================================================================")
    print(f"Running scenario and data integrity tests from: {test_dir}\n")

    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    print("\n======================================================================")
    print(f"TEST RUN SUMMARY: Total={result.testsRun}, Errors={len(result.errors)}, Failures={len(result.failures)}")
    print("======================================================================")

    return 0 if result.wasSuccessful() else 1


if __name__ == "__main__":
    sys.exit(run_all_tests())

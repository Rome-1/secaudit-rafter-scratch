#!/usr/bin/env python3
"""
Test script to verify the segment deletion behavior.
This script will be used to verify that:
1. Segments can be deleted when they have no references
2. Segments cannot be deleted when referenced by rules or rollouts
3. Error messages are correct
"""

import subprocess
import sys

def run_go_test(test_name):
    """Run a specific Go test and return the result."""
    cmd = [
        "go", "test", 
        "-v",
        "-run", test_name,
        "./internal/storage/sql/..."
    ]
    
    print(f"Running: {' '.join(cmd)}")
    result = subprocess.run(cmd, capture_output=True, text=True, cwd="/app")
    
    print("STDOUT:")
    print(result.stdout)
    print("\nSTDERR:")
    print(result.stderr)
    print(f"\nReturn code: {result.returncode}")
    
    return result.returncode == 0

def main():
    """Run tests to verify segment deletion behavior."""
    
    print("=" * 80)
    print("Testing Segment Deletion Behavior")
    print("=" * 80)
    
    # Test that basic deletion works
    print("\n\n1. Testing basic segment deletion (should pass):")
    print("-" * 80)
    success1 = run_go_test("TestDeleteSegment$")
    
    # Test deletion with existing rule (currently skipped, but should fail after implementation)
    print("\n\n2. Testing segment deletion with existing rule (currently skipped):")
    print("-" * 80)
    success2 = run_go_test("TestDeleteSegment_ExistingRule")
    
    print("\n\n" + "=" * 80)
    print("Summary:")
    print(f"  Basic deletion: {'PASS' if success1 else 'FAIL'}")
    print(f"  Deletion with rule: {'PASS (or SKIPPED)' if success2 else 'FAIL'}")
    print("=" * 80)

if __name__ == "__main__":
    main()

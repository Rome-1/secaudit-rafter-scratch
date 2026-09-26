#!/usr/bin/env python3

import subprocess
import sys
import os

def run_go_test(test_pattern):
    """Run Go tests and return result"""
    try:
        cmd = ['go', 'test', '-v', '-run', test_pattern, './internal/server/auth/']
        result = subprocess.run(cmd, cwd='/app', capture_output=True, text=True, timeout=30)
        return result.returncode == 0, result.stdout, result.stderr
    except Exception as e:
        return False, "", str(e)

def main():
    print("Testing current authentication middleware behavior...")
    
    # Run existing tests to verify current behavior works
    success, stdout, stderr = run_go_test("TestUnaryInterceptor")
    
    print("\n=== Current Test Results ===")
    print("Exit code:", "PASS" if success else "FAIL")
    print("\nStdout:")
    print(stdout)
    print("\nStderr:")
    print(stderr)
    
    # Try to compile the current middleware to identify what's missing
    print("\n=== Testing compilation ===")
    try:
        cmd = ['go', 'build', './internal/server/auth/']
        result = subprocess.run(cmd, cwd='/app', capture_output=True, text=True)
        print("Compilation:", "SUCCESS" if result.returncode == 0 else "FAILED")
        if result.returncode != 0:
            print("Compile errors:")
            print(result.stderr)
    except Exception as e:
        print("Compilation error:", e)

if __name__ == "__main__":
    main()
#!/usr/bin/env python3

"""
Test script to reproduce the issue and test GCP service account integration.
This will fail until we implement the GCP integration.
"""

import subprocess
import os
import sys

def run_go_test():
    """Run a simple Go test to check if GCP fields are properly serialized/deserialized"""
    
    # Let's try to build the test first to see what errors we get
    cmd = ["go", "test", "-v", "./lib/tlsca", "-run", "TestGCPExtensions"]
    
    # Set working directory to the app directory
    os.chdir('/app')
    
    print("Running go test to check for GCP integration...")
    print(f"Command: {' '.join(cmd)}")
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        print("STDOUT:")
        print(result.stdout)
        print("STDERR:")
        print(result.stderr)
        print(f"Return code: {result.returncode}")
        return result.returncode == 0
    except subprocess.TimeoutExpired:
        print("Test timed out")
        return False
    except Exception as e:
        print(f"Error running test: {e}")
        return False

if __name__ == "__main__":
    success = run_go_test()
    if success:
        print("✅ Tests passed! GCP integration is working.")
    else:
        print("❌ Tests failed. GCP integration needs to be implemented.")
    sys.exit(0 if success else 1)
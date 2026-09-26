#!/usr/bin/env python3

"""
Test script to verify that the changes compile correctly
"""

import subprocess
import sys

def test_compilation():
    """Test that the changes compile without errors"""
    print("Testing compilation of modified packages...")
    
    packages = [
        "github.com/gravitational/teleport/lib/auth/native",
        "github.com/gravitational/teleport/lib/auth",
        "github.com/gravitational/teleport/lib/reversetunnel",
        "github.com/gravitational/teleport/lib/service",
    ]
    
    all_passed = True
    
    for package in packages:
        print(f"\nTesting compilation of {package}...")
        
        try:
            result = subprocess.run(['go', 'build', package], 
                                  cwd='/app', 
                                  capture_output=True, 
                                  text=True, 
                                  timeout=30)
            
            if result.returncode == 0:
                print(f"✓ {package} compiles successfully")
            else:
                print(f"✗ {package} failed to compile")
                print(f"Error: {result.stderr}")
                all_passed = False
                
        except subprocess.TimeoutExpired:
            print(f"✗ {package} compilation timed out")
            all_passed = False
    
    return all_passed

def test_precompute_function():
    """Simple test to verify PrecomputeKeys function works"""
    print("\nTesting PrecomputeKeys function...")
    
    code = '''
package main

import (
    "fmt"
    "github.com/gravitational/teleport/lib/auth/native"
)

func main() {
    fmt.Println("Testing PrecomputeKeys...")
    native.PrecomputeKeys()
    fmt.Println("PrecomputeKeys completed successfully")
}
'''
    
    with open('/tmp/test_simple.go', 'w') as f:
        f.write(code)
    
    try:
        result = subprocess.run(['go', 'run', '/tmp/test_simple.go'], 
                              cwd='/app', 
                              capture_output=True, 
                              text=True, 
                              timeout=15)
        
        print(f"Return code: {result.returncode}")
        print(f"Stdout: {result.stdout}")
        if result.stderr:
            print(f"Stderr: {result.stderr}")
        
        return result.returncode == 0
        
    except subprocess.TimeoutExpired:
        print("Test timed out")
        return False

if __name__ == "__main__":
    print("=== Testing Compilation and Basic Functionality ===")
    
    compilation_ok = test_compilation()
    function_ok = test_precompute_function()
    
    print(f"\n{'='*60}")
    print("Results:")
    print(f"  Compilation: {'✓ PASS' if compilation_ok else '✗ FAIL'}")
    print(f"  Function Test: {'✓ PASS' if function_ok else '✗ FAIL'}")
    print('='*60)
    
    if compilation_ok and function_ok:
        print("🎉 All tests passed!")
        sys.exit(0)
    else:
        print("❌ Some tests failed!")
        sys.exit(1)
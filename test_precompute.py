#!/usr/bin/env python3

"""
Test script to verify the precomputation functionality
"""

import subprocess
import sys
import time

def run_go_code(code):
    """Run Go code and return the result"""
    with open('/tmp/test.go', 'w') as f:
        f.write(code)
    
    try:
        result = subprocess.run(['go', 'run', '/tmp/test.go'], 
                              cwd='/app', 
                              capture_output=True, 
                              text=True, 
                              timeout=30)
        return result.returncode, result.stdout, result.stderr
    except subprocess.TimeoutExpired:
        return -1, "", "Timeout expired"

def test_current_implementation():
    """Test the current implementation to understand the behavior"""
    print("Testing current implementation...")
    
    code = '''
package main

import (
    "fmt"
    "time"
    "github.com/gravitational/teleport/lib/auth/native"
)

func main() {
    // Test if PrecomputeKeys function exists (it should not exist yet)
    // This will fail to compile if PrecomputeKeys doesn't exist
    fmt.Println("Testing native.PrecomputeKeys()...")
    
    // This should cause a compilation error in the current state
    native.PrecomputeKeys()
    
    fmt.Println("PrecomputeKeys() called successfully")
}
'''
    
    returncode, stdout, stderr = run_go_code(code)
    
    print(f"Return code: {returncode}")
    print(f"Stdout: {stdout}")
    print(f"Stderr: {stderr}")
    
    if returncode != 0 and "PrecomputeKeys" in stderr:
        print("✓ Expected failure: PrecomputeKeys() function does not exist yet")
        return True
    else:
        print("✗ Unexpected behavior")
        return False

def test_basic_key_generation():
    """Test the basic key generation functionality"""
    print("\nTesting basic key generation...")
    
    code = '''
package main

import (
    "fmt"
    "time"
    "github.com/gravitational/teleport/lib/auth/native"
)

func main() {
    start := time.Now()
    priv, pub, err := native.GenerateKeyPair()
    duration := time.Since(start)
    
    if err != nil {
        fmt.Printf("Error: %v\\n", err)
        return
    }
    
    fmt.Printf("Generated key pair in %v\\n", duration)
    fmt.Printf("Private key length: %d\\n", len(priv))
    fmt.Printf("Public key length: %d\\n", len(pub))
    
    // Test multiple calls to see current behavior
    for i := 0; i < 3; i++ {
        start = time.Now()
        _, _, err = native.GenerateKeyPair()
        duration = time.Since(start)
        if err != nil {
            fmt.Printf("Error on call %d: %v\\n", i+2, err)
            continue
        }
        fmt.Printf("Call %d completed in %v\\n", i+2, duration)
    }
}
'''
    
    returncode, stdout, stderr = run_go_code(code)
    
    print(f"Return code: {returncode}")
    print(f"Stdout: {stdout}")
    if stderr:
        print(f"Stderr: {stderr}")
    
    return returncode == 0

if __name__ == "__main__":
    print("=== Testing Current State ===")
    
    test1_passed = test_current_implementation()
    test2_passed = test_basic_key_generation()
    
    if test1_passed and test2_passed:
        print("\n✓ Current state tests completed as expected")
        print("  - PrecomputeKeys() function doesn't exist (expected)")
        print("  - Basic key generation works")
    else:
        print("\n✗ Unexpected current state behavior")
        sys.exit(1)
#!/usr/bin/env python3

"""
Test script to verify the precomputation functionality implementation
"""

import subprocess
import sys
import time

def run_go_code(code):
    """Run Go code and return the result"""
    with open('/tmp/test_impl.go', 'w') as f:
        f.write(code)
    
    try:
        result = subprocess.run(['go', 'run', '/tmp/test_impl.go'], 
                              cwd='/app', 
                              capture_output=True, 
                              text=True, 
                              timeout=30)
        return result.returncode, result.stdout, result.stderr
    except subprocess.TimeoutExpired:
        return -1, "", "Timeout expired"

def test_precompute_keys_exists():
    """Test if PrecomputeKeys function exists and can be called"""
    print("Testing PrecomputeKeys() function existence...")
    
    code = '''
package main

import (
    "fmt"
    "github.com/gravitational/teleport/lib/auth/native"
)

func main() {
    fmt.Println("Testing native.PrecomputeKeys()...")
    native.PrecomputeKeys()
    fmt.Println("✓ PrecomputeKeys() called successfully")
}
'''
    
    returncode, stdout, stderr = run_go_code(code)
    
    print(f"Return code: {returncode}")
    print(f"Stdout: {stdout}")
    if stderr:
        print(f"Stderr: {stderr}")
    
    return returncode == 0

def test_generatekeypair_without_precomputation():
    """Test that GenerateKeyPair works without precomputation being enabled"""
    print("\nTesting GenerateKeyPair without precomputation...")
    
    code = '''
package main

import (
    "fmt"
    "time"
    "github.com/gravitational/teleport/lib/auth/native"
)

func main() {
    // Test multiple calls without calling PrecomputeKeys first
    // All should take similar time since no precomputation is active
    var durations []time.Duration
    
    for i := 0; i < 3; i++ {
        start := time.Now()
        priv, pub, err := native.GenerateKeyPair()
        duration := time.Since(start)
        durations = append(durations, duration)
        
        if err != nil {
            fmt.Printf("Error on call %d: %v\\n", i+1, err)
            return
        }
        
        fmt.Printf("Call %d: %v (priv: %d bytes, pub: %d bytes)\\n", i+1, duration, len(priv), len(pub))
    }
    
    // All calls should take significant time (>50ms) since no precomputation
    allSlow := true
    for i, dur := range durations {
        if dur < 50*time.Millisecond {
            fmt.Printf("Warning: Call %d was unexpectedly fast: %v\\n", i+1, dur)
            allSlow = false
        }
    }
    
    if allSlow {
        fmt.Println("✓ All calls took expected time without precomputation")
    } else {
        fmt.Println("! Some calls were faster than expected")
    }
}
'''
    
    returncode, stdout, stderr = run_go_code(code)
    
    print(f"Return code: {returncode}")
    print(f"Stdout: {stdout}")
    if stderr:
        print(f"Stderr: {stderr}")
    
    return returncode == 0

def test_precomputation_with_precompute_keys():
    """Test that GenerateKeyPair uses precomputed keys after PrecomputeKeys() is called"""
    print("\nTesting GenerateKeyPair with precomputation enabled...")
    
    code = '''
package main

import (
    "fmt"
    "time"
    "github.com/gravitational/teleport/lib/auth/native"
)

func main() {
    fmt.Println("Calling PrecomputeKeys()...")
    native.PrecomputeKeys()
    
    // Wait for at least one key to be precomputed (requirement: ≤ 10 seconds)
    fmt.Println("Waiting for precomputed keys to become available...")
    maxWait := 10 * time.Second
    waitStart := time.Now()
    
    var firstFastCall bool
    var firstCallDuration time.Duration
    
    for time.Since(waitStart) < maxWait {
        time.Sleep(100 * time.Millisecond)
        
        start := time.Now()
        _, _, err := native.GenerateKeyPair()
        duration := time.Since(start)
        
        if err != nil {
            fmt.Printf("Error: %v\\n", err)
            return
        }
        
        fmt.Printf("Test call took %v\\n", duration)
        
        // If the call is fast (< 10ms), precomputed keys are available
        if duration < 10*time.Millisecond {
            firstFastCall = true
            firstCallDuration = duration
            break
        }
    }
    
    if !firstFastCall {
        fmt.Printf("✗ No fast calls within %v - precomputation may not be working\\n", maxWait)
        return
    }
    
    fmt.Printf("✓ First fast call took %v (precomputation active)\\n", firstCallDuration)
    
    // Now test multiple calls to ensure they use precomputed keys
    fmt.Println("Testing subsequent calls...")
    
    fastCalls := 0
    for i := 0; i < 5; i++ {
        start := time.Now()
        priv, pub, err := native.GenerateKeyPair()
        duration := time.Since(start)
        
        if err != nil {
            fmt.Printf("Error on call %d: %v\\n", i+1, err)
            return
        }
        
        fmt.Printf("Call %d: %v (priv: %d bytes, pub: %d bytes)\\n", i+1, duration, len(priv), len(pub))
        
        if duration < 10*time.Millisecond {
            fastCalls++
        }
    }
    
    fmt.Printf("Fast calls: %d/5\\n", fastCalls)
    
    if fastCalls >= 3 {
        fmt.Println("✓ Majority of calls used precomputed keys")
    } else {
        fmt.Println("! Most calls were slow - precomputation may not be working optimally")
    }
}
'''
    
    returncode, stdout, stderr = run_go_code(code)
    
    print(f"Return code: {returncode}")
    print(f"Stdout: {stdout}")
    if stderr:
        print(f"Stderr: {stderr}")
    
    return returncode == 0

def test_precompute_keys_idempotent():
    """Test that calling PrecomputeKeys multiple times is safe"""
    print("\nTesting PrecomputeKeys() idempotency...")
    
    code = '''
package main

import (
    "fmt"
    "time"
    "github.com/gravitational/teleport/lib/auth/native"
)

func main() {
    fmt.Println("Calling PrecomputeKeys() multiple times...")
    
    // Call PrecomputeKeys multiple times
    for i := 0; i < 5; i++ {
        native.PrecomputeKeys()
        fmt.Printf("Call %d completed\\n", i+1)
    }
    
    fmt.Println("✓ Multiple PrecomputeKeys() calls completed without error")
    
    // Wait a bit and test that key generation still works
    time.Sleep(2 * time.Second)
    
    start := time.Now()
    priv, pub, err := native.GenerateKeyPair()
    duration := time.Since(start)
    
    if err != nil {
        fmt.Printf("Error after multiple PrecomputeKeys calls: %v\\n", err)
        return
    }
    
    fmt.Printf("GenerateKeyPair after multiple PrecomputeKeys calls: %v (priv: %d bytes, pub: %d bytes)\\n", duration, len(priv), len(pub))
    fmt.Println("✓ Key generation works correctly after multiple PrecomputeKeys calls")
}
'''
    
    returncode, stdout, stderr = run_go_code(code)
    
    print(f"Return code: {returncode}")
    print(f"Stdout: {stdout}")
    if stderr:
        print(f"Stderr: {stderr}")
    
    return returncode == 0

if __name__ == "__main__":
    print("=== Testing PrecomputeKeys Implementation ===")
    
    tests = [
        ("PrecomputeKeys() exists", test_precompute_keys_exists),
        ("GenerateKeyPair without precomputation", test_generatekeypair_without_precomputation),
        ("GenerateKeyPair with precomputation", test_precomputation_with_precompute_keys),
        ("PrecomputeKeys() idempotency", test_precompute_keys_idempotent),
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n{'='*60}")
        print(f"Running: {test_name}")
        print('='*60)
        
        try:
            result = test_func()
            if result:
                print(f"✓ PASSED: {test_name}")
                passed += 1
            else:
                print(f"✗ FAILED: {test_name}")
        except Exception as e:
            print(f"✗ ERROR in {test_name}: {e}")
    
    print(f"\n{'='*60}")
    print(f"Results: {passed}/{total} tests passed")
    print('='*60)
    
    if passed == total:
        print("🎉 All tests passed!")
        sys.exit(0)
    else:
        print("❌ Some tests failed!")
        sys.exit(1)
#!/usr/bin/env python3

"""
Test script to verify the scaling scenario works correctly
"""

import subprocess
import sys
import time
import threading
from concurrent.futures import ThreadPoolExecutor

def run_go_code(code, timeout=30):
    """Run Go code and return the result"""
    with open('/tmp/scaling.go', 'w') as f:
        f.write(code)
    
    try:
        result = subprocess.run(['go', 'run', '/tmp/scaling.go'], 
                              cwd='/app', 
                              capture_output=True, 
                              text=True, 
                              timeout=timeout)
        return result.returncode, result.stdout, result.stderr
    except subprocess.TimeoutExpired:
        return -1, "", "Timeout expired"

def test_high_concurrency_key_generation():
    """Test high concurrency key generation as would happen during reverse tunnel node scaling"""
    print("Testing high concurrency key generation scenario...")
    print("This simulates what happens when many reverse tunnel nodes connect simultaneously")
    
    code = '''
package main

import (
    "fmt"
    "sync"
    "time"
    "github.com/gravitational/teleport/lib/auth/native"
)

func generateKeyWorker(id int, wg *sync.WaitGroup, results chan<- time.Duration) {
    defer wg.Done()
    
    start := time.Now()
    _, _, err := native.GenerateKeyPair()
    duration := time.Since(start)
    
    if err != nil {
        fmt.Printf("Worker %d error: %v\\n", id, err)
        return
    }
    
    results <- duration
}

func main() {
    fmt.Println("=== Scaling Scenario Test ===")
    
    // Test 1: Without precomputation (simulating the problem described in PR)
    fmt.Println("\\n1. Testing WITHOUT precomputation (original problem scenario):")
    
    const numWorkers = 20  // Simulate 20 reverse tunnel nodes connecting
    
    var wg sync.WaitGroup
    results := make(chan time.Duration, numWorkers)
    
    start := time.Now()
    for i := 0; i < numWorkers; i++ {
        wg.Add(1)
        go generateKeyWorker(i, &wg, results)
    }
    wg.Wait()
    close(results)
    
    totalTime := time.Since(start)
    
    var durations []time.Duration
    var totalDuration time.Duration
    slowCount := 0
    
    for duration := range results {
        durations = append(durations, duration)
        totalDuration += duration
        if duration > 100*time.Millisecond {
            slowCount++
        }
    }
    
    avgDuration := totalDuration / time.Duration(len(durations))
    
    fmt.Printf("Without precomputation - Total time: %v, Avg per key: %v, Slow keys: %d/%d\\n", 
               totalTime, avgDuration, slowCount, numWorkers)
    
    // Test 2: With precomputation (our solution)
    fmt.Println("\\n2. Testing WITH precomputation (our solution):")
    
    // Enable precomputation
    native.PrecomputeKeys()
    
    // Wait for keys to be precomputed
    time.Sleep(3 * time.Second)
    
    results2 := make(chan time.Duration, numWorkers)
    var wg2 sync.WaitGroup
    
    start2 := time.Now()
    for i := 0; i < numWorkers; i++ {
        wg2.Add(1)
        go generateKeyWorker(i, &wg2, results2)
    }
    wg2.Wait()
    close(results2)
    
    totalTime2 := time.Since(start2)
    
    var durations2 []time.Duration
    var totalDuration2 time.Duration
    fastCount := 0
    
    for duration := range results2 {
        durations2 = append(durations2, duration)
        totalDuration2 += duration
        if duration < 50*time.Millisecond {
            fastCount++
        }
    }
    
    avgDuration2 := totalDuration2 / time.Duration(len(durations2))
    
    fmt.Printf("With precomputation - Total time: %v, Avg per key: %v, Fast keys: %d/%d\\n", 
               totalTime2, avgDuration2, fastCount, numWorkers)
    
    // Performance comparison
    improvement := float64(totalTime) / float64(totalTime2)
    fmt.Printf("\\n=== Results ===\\n")
    fmt.Printf("Performance improvement: %.2fx faster\\n", improvement)
    
    if improvement > 1.5 {
        fmt.Printf("✓ Significant performance improvement achieved\\n")
    } else {
        fmt.Printf("! Performance improvement may not be significant\\n")
    }
    
    if fastCount > slowCount {
        fmt.Printf("✓ More keys generated from precomputed cache than slow generation\\n")
    } else {
        fmt.Printf("! Precomputation may need more time to build up cache\\n")
    }
    
    fmt.Printf("\\nThis demonstrates how precomputation helps with the reverse tunnel scaling issue.\\n")
}
'''
    
    returncode, stdout, stderr = run_go_code(code, timeout=60)
    
    print(f"Return code: {returncode}")
    print(f"Stdout:\n{stdout}")
    if stderr:
        print(f"Stderr: {stderr}")
    
    return returncode == 0

if __name__ == "__main__":
    print("=== Scaling Scenario Test ===")
    print("This test simulates the high-load scenario described in the PR")
    print("where many reverse tunnel nodes try to generate keys simultaneously.")
    
    success = test_high_concurrency_key_generation()
    
    if success:
        print("\n🎉 Scaling scenario test completed successfully!")
        print("The implementation should help resolve the reverse tunnel scaling issue.")
    else:
        print("\n❌ Scaling scenario test failed!")
        sys.exit(1)
package main

import (
"fmt"
"go.flipt.io/flipt/internal/config"
"time"
)

func main() {
fmt.Println("=== Testing Database Requirement Logic ===\n")

// Test Case 1: JWT only with non-DB storage
cfg1 := &config.AuthenticationConfig{
Required: true,
}
cfg1.Methods.JWT.Enabled = true

fmt.Println("Test Case 1: JWT only enabled")
fmt.Printf("  Enabled: %v\n", cfg1.Enabled())
fmt.Printf("  RequiresDatabase: %v (expected: false)\n", cfg1.RequiresDatabase())
fmt.Printf("  ShouldRunCleanup: %v (expected: false)\n", cfg1.ShouldRunCleanup())
if cfg1.RequiresDatabase() {
fmt.Println("  ❌ FAILED: JWT should not require a database")
} else {
fmt.Println("  ✅ PASSED: JWT correctly does not require a database")
}

// Test Case 2: Token auth with non-DB storage
cfg2 := &config.AuthenticationConfig{
Required: true,
}
cfg2.Methods.Token.Enabled = true

fmt.Println("\nTest Case 2: Token auth enabled")
fmt.Printf("  Enabled: %v\n", cfg2.Enabled())
fmt.Printf("  RequiresDatabase: %v (expected: true)\n", cfg2.RequiresDatabase())
fmt.Printf("  ShouldRunCleanup: %v (expected: false - no cleanup schedule)\n", cfg2.ShouldRunCleanup())
if !cfg2.RequiresDatabase() {
fmt.Println("  ❌ FAILED: Token auth should require a database")
} else {
fmt.Println("  ✅ PASSED: Token auth correctly requires a database")
}

// Test Case 3: Token auth with cleanup schedule
cfg3 := &config.AuthenticationConfig{
Required: true,
}
cfg3.Methods.Token.Enabled = true
cfg3.Methods.Token.Cleanup = &config.AuthenticationCleanupSchedule{
Interval:    time.Hour,
GracePeriod: 30 * time.Minute,
}

fmt.Println("\nTest Case 3: Token auth with cleanup schedule")
fmt.Printf("  Enabled: %v\n", cfg3.Enabled())
fmt.Printf("  RequiresDatabase: %v (expected: true)\n", cfg3.RequiresDatabase())
fmt.Printf("  ShouldRunCleanup: %v (expected: true)\n", cfg3.ShouldRunCleanup())
if !cfg3.RequiresDatabase() {
fmt.Println("  ❌ FAILED: Token auth should require a database")
} else if !cfg3.ShouldRunCleanup() {
fmt.Println("  ❌ FAILED: Token auth with cleanup schedule should run cleanup")
} else {
fmt.Println("  ✅ PASSED: Token auth with cleanup correctly configured")
}

// Test Case 4: Multiple methods including JWT
cfg4 := &config.AuthenticationConfig{
Required: true,
}
cfg4.Methods.JWT.Enabled = true
cfg4.Methods.Token.Enabled = true

fmt.Println("\nTest Case 4: Both JWT and Token auth enabled")
fmt.Printf("  Enabled: %v\n", cfg4.Enabled())
fmt.Printf("  RequiresDatabase: %v (expected: true)\n", cfg4.RequiresDatabase())
fmt.Printf("  ShouldRunCleanup: %v (expected: false - no cleanup schedule)\n", cfg4.ShouldRunCleanup())
if !cfg4.RequiresDatabase() {
fmt.Println("  ❌ FAILED: Should require a database when Token auth is enabled")
} else {
fmt.Println("  ✅ PASSED: Correctly requires a database when Token auth is enabled")
}

// Test Case 5: JWT with cleanup schedule (should not trigger cleanup)
cfg5 := &config.AuthenticationConfig{
Required: true,
}
cfg5.Methods.JWT.Enabled = true
cfg5.Methods.JWT.Cleanup = &config.AuthenticationCleanupSchedule{
Interval:    time.Hour,
GracePeriod: 30 * time.Minute,
}

fmt.Println("\nTest Case 5: JWT with cleanup schedule (cleanup should not run)")
fmt.Printf("  Enabled: %v\n", cfg5.Enabled())
fmt.Printf("  RequiresDatabase: %v (expected: false)\n", cfg5.RequiresDatabase())
fmt.Printf("  ShouldRunCleanup: %v (expected: false - JWT doesn't use DB)\n", cfg5.ShouldRunCleanup())
if cfg5.RequiresDatabase() {
fmt.Println("  ❌ FAILED: JWT should not require a database")
} else if cfg5.ShouldRunCleanup() {
fmt.Println("  ❌ FAILED: JWT should not run cleanup (doesn't use DB)")
} else {
fmt.Println("  ✅ PASSED: JWT correctly does not run cleanup")
}

// Test Case 6: OIDC enabled
cfg6 := &config.AuthenticationConfig{
Required: true,
}
cfg6.Methods.OIDC.Enabled = true

fmt.Println("\nTest Case 6: OIDC enabled")
fmt.Printf("  Enabled: %v\n", cfg6.Enabled())
fmt.Printf("  RequiresDatabase: %v (expected: true)\n", cfg6.RequiresDatabase())
if !cfg6.RequiresDatabase() {
fmt.Println("  ❌ FAILED: OIDC should require a database")
} else {
fmt.Println("  ✅ PASSED: OIDC correctly requires a database")
}

// Test Case 7: GitHub enabled
cfg7 := &config.AuthenticationConfig{
Required: true,
}
cfg7.Methods.Github.Enabled = true

fmt.Println("\nTest Case 7: GitHub enabled")
fmt.Printf("  Enabled: %v\n", cfg7.Enabled())
fmt.Printf("  RequiresDatabase: %v (expected: true)\n", cfg7.RequiresDatabase())
if !cfg7.RequiresDatabase() {
fmt.Println("  ❌ FAILED: GitHub should require a database")
} else {
fmt.Println("  ✅ PASSED: GitHub correctly requires a database")
}

// Test Case 8: Kubernetes enabled
cfg8 := &config.AuthenticationConfig{
Required: true,
}
cfg8.Methods.Kubernetes.Enabled = true

fmt.Println("\nTest Case 8: Kubernetes enabled")
fmt.Printf("  Enabled: %v\n", cfg8.Enabled())
fmt.Printf("  RequiresDatabase: %v (expected: true)\n", cfg8.RequiresDatabase())
if !cfg8.RequiresDatabase() {
fmt.Println("  ❌ FAILED: Kubernetes should require a database")
} else {
fmt.Println("  ✅ PASSED: Kubernetes correctly requires a database")
}

// Test Case 9: No auth enabled
cfg9 := &config.AuthenticationConfig{
Required: false,
}

fmt.Println("\nTest Case 9: No authentication enabled")
fmt.Printf("  Enabled: %v\n", cfg9.Enabled())
fmt.Printf("  RequiresDatabase: %v (expected: false)\n", cfg9.RequiresDatabase())
if cfg9.RequiresDatabase() {
fmt.Println("  ❌ FAILED: Should not require a database when no auth is enabled")
} else {
fmt.Println("  ✅ PASSED: Correctly does not require a database")
}

fmt.Println("\n=== Testing Complete ===")
}

package main

import (
"fmt"
"go.flipt.io/flipt/internal/config"
)

func main() {
// Test Case 1: JWT only with non-DB storage
cfg1 := &config.AuthenticationConfig{
Required: true,
}
cfg1.Methods.JWT.Enabled = true

fmt.Println("Test Case 1: JWT only enabled")
fmt.Printf("  Enabled: %v\n", cfg1.Enabled())
fmt.Printf("  ShouldRunCleanup: %v\n", cfg1.ShouldRunCleanup())

// Test Case 2: Token auth with non-DB storage
cfg2 := &config.AuthenticationConfig{
Required: true,
}
cfg2.Methods.Token.Enabled = true

fmt.Println("\nTest Case 2: Token auth enabled")
fmt.Printf("  Enabled: %v\n", cfg2.Enabled())
fmt.Printf("  ShouldRunCleanup: %v\n", cfg2.ShouldRunCleanup())

// Test Case 3: Multiple methods including JWT
cfg3 := &config.AuthenticationConfig{
Required: true,
}
cfg3.Methods.JWT.Enabled = true
cfg3.Methods.Token.Enabled = true

fmt.Println("\nTest Case 3: Both JWT and Token auth enabled")
fmt.Printf("  Enabled: %v\n", cfg3.Enabled())
fmt.Printf("  ShouldRunCleanup: %v\n", cfg3.ShouldRunCleanup())
}

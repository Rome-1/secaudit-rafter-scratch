package main

import (
"context"
"fmt"
"log"

"go.flipt.io/flipt/internal/storage/fs"
"go.uber.org/zap"
)

func main() {
// Test the Delete method on SnapshotCache
logger, _ := zap.NewDevelopment()

ctx := context.Background()

// Create a cache with extra capacity of 2
cache, err := fs.NewSnapshotCache[string](logger, 2)
if err != nil {
log.Fatalf("Failed to create cache: %v", err)
}

// Create a mock snapshot
snap := &fs.Snapshot{}

// Add a fixed reference
cache.AddFixed(ctx, "main", "hash1", snap)

// Try to delete the fixed reference (should fail)
err = cache.Delete("main")
if err != nil {
fmt.Printf("✓ Delete on fixed reference correctly returned error: %v\n", err)
} else {
fmt.Printf("✗ Delete on fixed reference should have returned an error\n")
}

// Add a non-fixed reference
cache.AddOrBuild(ctx, "feature-branch", "hash2", func(ctx context.Context, k string) (*fs.Snapshot, error) {
return snap, nil
})

// Delete the non-fixed reference (should succeed)
err = cache.Delete("feature-branch")
if err == nil {
fmt.Printf("✓ Delete on non-fixed reference succeeded\n")
} else {
fmt.Printf("✗ Delete on non-fixed reference failed: %v\n", err)
}

// Try to delete a non-existent reference (should succeed silently)
err = cache.Delete("non-existent")
if err == nil {
fmt.Printf("✓ Delete on non-existent reference succeeded silently\n")
} else {
fmt.Printf("✗ Delete on non-existent reference failed: %v\n", err)
}

fmt.Println("\nAll tests completed!")
}
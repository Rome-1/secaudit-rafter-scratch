package main

import (
"context"
"fmt"
"log"

storagefs "go.flipt.io/flipt/internal/storage/fs"
"go.uber.org/zap"
)

func newMockSnapshot(key, name string) *storagefs.Snapshot {
n := &storagefs.Snapshot{}
return n
}

func testDeleteFunctionality() {
logger, _ := zap.NewDevelopment()

// Create a cache
cache, err := storagefs.NewSnapshotCache[string](logger, 2)
if err != nil {
log.Fatal("Failed to create cache:", err)
}

ctx := context.Background()

// Create some mock snapshots
snap1 := newMockSnapshot("key1", "Snapshot 1")
snap2 := newMockSnapshot("key2", "Snapshot 2")

// Add a fixed reference
cache.AddFixed(ctx, "main", "hash-main", snap1)

// Add a non-fixed reference
_, err = cache.AddOrBuild(ctx, "feature-branch", "hash-feature", func(ctx context.Context, key string) (*storagefs.Snapshot, error) {
return snap2, nil
})
if err != nil {
log.Fatal("Failed to add feature branch:", err)
}

fmt.Println("Initial references:", cache.References())

// Try to delete the fixed reference (should fail)
fmt.Println("Trying to delete fixed reference 'main'...")
err = cache.Delete("main")
if err != nil {
fmt.Println("✓ Expected error:", err)
} else {
fmt.Println("✗ Should have failed to delete fixed reference")
}

// Delete the non-fixed reference (should succeed)
fmt.Println("Deleting non-fixed reference 'feature-branch'...")
err = cache.Delete("feature-branch")
if err != nil {
fmt.Println("✗ Unexpected error:", err)
} else {
fmt.Println("✓ Successfully deleted feature-branch")
}

fmt.Println("References after deletion:", cache.References())

// Try to delete a non-existent reference (should succeed silently)
fmt.Println("Deleting non-existent reference 'non-existent'...")
err = cache.Delete("non-existent")
if err != nil {
fmt.Println("✗ Unexpected error:", err)
} else {
fmt.Println("✓ Successfully handled non-existent reference")
}

fmt.Println("Final references:", cache.References())
}

func main() {
fmt.Println("Testing Delete functionality...")
testDeleteFunctionality()
fmt.Println("Delete functionality test completed!")
}
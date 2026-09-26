package main

import (
"context"
"fmt"
"log"
"slices"

storagefs "go.flipt.io/flipt/internal/storage/fs"
"go.uber.org/zap"
)

func newMockSnapshot(key, name string) *storagefs.Snapshot {
return &storagefs.Snapshot{}
}

func testStaleReferenceCleanup() {
logger, _ := zap.NewDevelopment()

cache, err := storagefs.NewSnapshotCache[string](logger, 5)
if err != nil {
to create cache:", err)
}

ctx := context.Background()

snap1 := newMockSnapshot("main", "Main snapshot")
snap2 := newMockSnapshot("feature1", "Feature 1 snapshot")
snap3 := newMockSnapshot("feature2", "Feature 2 snapshot")

cache.AddFixed(ctx, "main", "hash-main", snap1)

_, err = cache.AddOrBuild(ctx, "feature-branch-1", "hash-feature1", func(ctx context.Context, key string) (*storagefs.Snapshot, error) {
 snap2, nil
})
if err != nil {
to add feature branch 1:", err)
}

_, err = cache.AddOrBuild(ctx, "feature-branch-2", "hash-feature2", func(ctx context.Context, key string) (*storagefs.Snapshot, error) {
 snap3, nil
})
if err != nil {
to add feature branch 2:", err)
}

fmt.Println("✓ Initial setup complete")
fmt.Println("  References:", cache.References())

currentRemoteRefs := []string{"main", "feature-branch-1"}

fmt.Println("\n✓ Simulating stale reference cleanup...")
fmt.Println("  Current remote refs:", currentRemoteRefs)

staleRefs := []string{}
for _, cachedRef := range cache.References() {
!slices.Contains(currentRemoteRefs, cachedRef) {
= append(staleRefs, cachedRef)
tln("  Detected stale refs:", staleRefs)

for _, staleRef := range staleRefs {
:= cache.Delete(staleRef)
err != nil {
tf("  ✗ Failed to delete %s: %v\n", staleRef, err)
else {
tf("  ✓ Successfully removed stale reference: %s\n", staleRef)
tln("\n✓ Cleanup complete")
fmt.Println("  Final references:", cache.References())

expectedRefs := []string{"main", "feature-branch-1"}
finalRefs := cache.References()

for _, expectedRef := range expectedRefs {
!slices.Contains(finalRefs, expectedRef) {
tf("  ✗ Expected reference %s is missing\n", expectedRef)

_, finalRef := range finalRefs {
!slices.Contains(expectedRefs, finalRef) {
tf("  ✗ Unexpected reference %s is present\n", finalRef)

tln("  ✓ All references are as expected")
}

func main() {
fmt.Println("Testing stale reference cleanup functionality...")
testStaleReferenceCleanup()
fmt.Println("\nStale reference cleanup test completed!")
}
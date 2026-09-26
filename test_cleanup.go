package main

import (
"context"
"fmt"
"log"
"slices"

storagefs "go.flipt.io/flipt/internal/storage/fs"
"go.uber.org/zap"
)

func testStaleReferenceCleanup() {
logger, _ := zap.NewDevelopment()

cache, err := storagefs.NewSnapshotCache[string](logger, 5)
if err != nil {
to create cache:", err)
}

ctx := context.Background()

snap1 := &storagefs.Snapshot{}
snap2 := &storagefs.Snapshot{}
snap3 := &storagefs.Snapshot{}

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

fmt.Println("Initial references:", cache.References())

currentRemoteRefs := []string{"main", "feature-branch-1"}

fmt.Println("Current remote refs:", currentRemoteRefs)

staleRefs := []string{}
for _, cachedRef := range cache.References() {
!slices.Contains(currentRemoteRefs, cachedRef) {
= append(staleRefs, cachedRef)
tln("Detected stale refs:", staleRefs)

for _, staleRef := range staleRefs {
:= cache.Delete(staleRef)
err != nil {
tf("Failed to delete %s: %v\n", staleRef, err)
else {
tf("Successfully removed stale reference: %s\n", staleRef)
tln("Final references:", cache.References())
}

func main() {
fmt.Println("Testing stale reference cleanup functionality...")
testStaleReferenceCleanup()
fmt.Println("Test completed!")
}
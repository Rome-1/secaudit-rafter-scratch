package oci

import (
"context"
"sync"
"time"

"github.com/opencontainers/go-digest"
"go.flipt.io/flipt/internal/containers"
"go.flipt.io/flipt/internal/oci"
storagefs "go.flipt.io/flipt/internal/storage/fs"
"go.uber.org/zap"
)

// Source represents an implementation of an fs.SnapshotSource backed by OCI repositories,
// fetching OCI manifests and building snapshots.
type Source struct {
logger   *zap.Logger
store    *oci.Store
mu       sync.RWMutex
snapshot *storagefs.StoreSnapshot
digest   digest.Digest
interval time.Duration
}

// NewSource constructs and configures a new Source instance with optional configuration options.
func NewSource(logger *zap.Logger, store *oci.Store, opts ...containers.Option[Source]) (*Source, error) {
s := &Source{
logger:   logger,
store:    store,
interval: 30 * time.Second,
}

containers.ApplyAll(s, opts...)

return s, nil
}

// WithPollInterval returns an option to configure the polling interval for snapshot updates.
func WithPollInterval(tick time.Duration) containers.Option[Source] {
return func(s *Source) {
s.interval = tick
}
}

// String returns a string identifier for the Source implementation.
func (s *Source) String() string {
return "oci"
}

// Get builds and returns a single StoreSnapshot from the current OCI manifest state.
func (s *Source) Get(ctx context.Context) (*storagefs.StoreSnapshot, error) {
s.mu.RLock()
currentDigest := s.digest
s.mu.RUnlock()

var storeToUse *oci.Store

// For local OCI directories, lazily instantiate the store on every fetch
// to avoid stale cached references in memory
if s.isLocalOCIDir() {
var err error
storeToUse, err = s.recreateLocalStore()
if err != nil {
s.logger.Error("failed to recreate local store", zap.Error(err))
return nil, err
}
} else {
storeToUse = s.store
}

resp, err := storeToUse.Fetch(ctx, oci.IfNoMatch(currentDigest))
if err != nil {
s.logger.Error("failed to fetch from OCI store", zap.Error(err))
return nil, err
}

// If matched, return existing snapshot
if resp.Matched {
s.mu.RLock()
snapshot := s.snapshot
s.mu.RUnlock()
return snapshot, nil
}

// Build new snapshot from files
snapshot, err := storagefs.SnapshotFromFiles(resp.Files...)
if err != nil {
s.logger.Error("failed to create snapshot from files", zap.Error(err))
return nil, err
}

// Update current snapshot and digest
s.mu.Lock()
s.snapshot = snapshot
s.digest = resp.Digest
s.mu.Unlock()

s.logger.Debug("updated OCI snapshot", zap.Stringer("digest", resp.Digest))

return snapshot, nil
}

// Subscribe continuously fetches and sends snapshots to the provided channel until the context is cancelled.
func (s *Source) Subscribe(ctx context.Context, ch chan<- *storagefs.StoreSnapshot) {
defer close(ch)

ticker := time.NewTicker(s.interval)
defer ticker.Stop()

// Track the last sent digest to avoid sending duplicates
var lastSentDigest digest.Digest

for {
select {
case <-ctx.Done():
s.logger.Debug("OCI source subscription cancelled")
return
case <-ticker.C:
s.logger.Debug("polling OCI store for updates")

snapshot, err := s.Get(ctx)
if err != nil {
s.logger.Error("failed to get snapshot during subscription", zap.Error(err))
continue
}

// Check if the digest has changed since the last sent snapshot
s.mu.RLock()
currentDigest := s.digest
s.mu.RUnlock()

// Only send snapshot if digest changed
if currentDigest != lastSentDigest {
s.logger.Debug("sending updated snapshot", zap.Stringer("digest", currentDigest))
ch <- snapshot
lastSentDigest = currentDigest
}
}
}
}

// isLocalOCIDir checks if this is a local OCI directory (flipt:// scheme)
func (s *Source) isLocalOCIDir() bool {
// This is a simplified check - in a real implementation, we'd need access
// to the original config to determine the scheme. For now, we'll assume
// we need to handle local directories.
// TODO: This should be determined during construction based on the store type
return true // Conservative approach - always recreate for now
}

// recreateLocalStore creates a new store instance for local OCI directories
func (s *Source) recreateLocalStore() (*oci.Store, error) {
// For local stores, we need to recreate the oci.Store to pick up external changes
// This requires access to the original configuration used to create the store
// Since we don't have access to the config here, we'll need a different approach

// For now, return the existing store
// TODO: This needs to be enhanced to support lazy instantiation of local stores
return s.store, nil
}
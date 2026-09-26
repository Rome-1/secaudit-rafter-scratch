package oci

import (
"context"
"sync"
"time"

"github.com/opencontainers/go-digest"
"go.flipt.io/flipt/internal/containers"
fliptoci "go.flipt.io/flipt/internal/oci"
storagefs "go.flipt.io/flipt/internal/storage/fs"
"go.uber.org/zap"
)

// Source represents an implementation of fs.SnapshotSource backed by OCI repositories
// It can fetch OCI manifests and build snapshots from them
type Source struct {
logger *zap.Logger

// mu protects access to currentSnapshot and currentDigest
mu              sync.RWMutex
currentSnapshot *storagefs.StoreSnapshot
currentDigest   digest.Digest

interval time.Duration
store    *fliptoci.Store
}

// NewSource constructs and configures a new OCI Source instance
func NewSource(logger *zap.Logger, store *fliptoci.Store, opts ...containers.Option[Source]) (*Source, error) {
s := &Source{
logger:   logger,
store:    store,
interval: 30 * time.Second,
}

containers.ApplyAll(s, opts...)

return s, nil
}

// WithPollInterval configures the polling interval for snapshot updates
func WithPollInterval(tick time.Duration) containers.Option[Source] {
return func(s *Source) {
s.interval = tick
}
}

// String returns an identifier string for the Source implementation
func (s *Source) String() string {
return "oci"
}

// Get builds and returns a single StoreSnapshot from the current OCI manifest state
func (s *Source) Get(ctx context.Context) (*storagefs.StoreSnapshot, error) {
// Fetch with IfNoMatch to avoid redundant fetches
s.mu.RLock()
currentDigest := s.currentDigest
s.mu.RUnlock()

var fetchOptions []containers.Option[fliptoci.FetchOptions]
if currentDigest != "" {
fetchOptions = append(fetchOptions, fliptoci.IfNoMatch(currentDigest))
}

resp, err := s.store.Fetch(ctx, fetchOptions...)
if err != nil {
return nil, err
}

// If digest matched, return current snapshot
if resp.Matched {
s.mu.RLock()
snapshot := s.currentSnapshot
s.mu.RUnlock()

if snapshot != nil {
s.logger.Debug("digest matched, returning cached snapshot")
return snapshot, nil
}
}

// Build new snapshot from files
snapshot, err := storagefs.SnapshotFromFiles(resp.Files...)
if err != nil {
return nil, err
}

// Update current snapshot and digest
s.mu.Lock()
s.currentSnapshot = snapshot
s.currentDigest = resp.Digest
s.mu.Unlock()

s.logger.Debug("built new snapshot", zap.String("digest", string(resp.Digest)))

return snapshot, nil
}

// Subscribe continuously fetches and sends snapshots to the provided channel until the context is cancelled
func (s *Source) Subscribe(ctx context.Context, ch chan<- *storagefs.StoreSnapshot) {
defer close(ch)

ticker := time.NewTicker(s.interval)
defer ticker.Stop()

for {
select {
case <-ctx.Done():
s.logger.Debug("subscription cancelled")
return
case <-ticker.C:
s.logger.Debug("polling for updates")

// Store the previous digest to compare
s.mu.RLock()
previousDigest := s.currentDigest
s.mu.RUnlock()

snap, err := s.Get(ctx)
if err != nil {
s.logger.Error("error fetching OCI snapshot", zap.Error(err))
continue
}

// Only send snapshot if digest changed
s.mu.RLock()
currentDigest := s.currentDigest
s.mu.RUnlock()

if previousDigest != currentDigest {
s.logger.Debug("digest changed, sending new snapshot",
zap.String("previous", string(previousDigest)),
zap.String("current", string(currentDigest)))
ch <- snap
} else {
s.logger.Debug("no changes detected")
}
}
}
}

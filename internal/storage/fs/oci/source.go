package oci

import (
    "context"
    "time"

    "github.com/opencontainers/go-digest"
    "go.flipt.io/flipt/internal/containers"
    ocistore "go.flipt.io/flipt/internal/oci"
    storagefs "go.flipt.io/flipt/internal/storage/fs"
    "go.uber.org/zap"
)

// Source implements fs.SnapshotSource backed by an OCI repository or local OCI directory.
// It fetches a manifest and associated feature files and builds storage snapshots.
type Source struct {
    logger *zap.Logger

    // store is the OCI store used to fetch manifests and files
    store *ocistore.Store

    // current holds the latest snapshot and digest we've observed
    current       *storagefs.StoreSnapshot
    currentDigest digest.Digest

    // interval controls Subscribe polling period
    interval time.Duration
}

// NewSource constructs and configures a new OCI Source instance.
func NewSource(logger *zap.Logger, store *ocistore.Store, opts ...containers.Option[Source]) (*Source, error) {
    s := &Source{
        logger:   logger,
        store:    store,
        interval: 30 * time.Second,
    }

    containers.ApplyAll(s, opts...)

    return s, nil
}

// WithPollInterval configures the polling interval used by Subscribe.
func WithPollInterval(tick time.Duration) containers.Option[Source] {
    return func(s *Source) {
        s.interval = tick
    }
}

// String returns an identifier for this source implementation.
func (s *Source) String() string { return "oci" }

// Get builds and returns a single StoreSnapshot from the current OCI manifest state.
func (s *Source) Get(ctx context.Context) (*storagefs.StoreSnapshot, error) { //nolint:revive,unused
    // attempt to use IfNoMatch to avoid unnecessary work
    resp, err := s.store.Fetch(ctx, ocistore.IfNoMatch(s.currentDigest))
    if err != nil {
        return nil, err
    }

    // if content unchanged, return existing snapshot
    if resp.Matched && s.current != nil {
        return s.current, nil
    }

    // build snapshot from returned files
    snap, err := storagefs.SnapshotFromFiles(resp.Files...)
    if err != nil {
        return nil, err
    }

    s.current = snap
    s.currentDigest = resp.Digest

    return snap, nil
}

// Subscribe continuously fetches and sends snapshots until the context is cancelled.
func (s *Source) Subscribe(ctx context.Context, ch chan<- *storagefs.StoreSnapshot) {
    defer close(ch)

    ticker := time.NewTicker(s.interval)
    defer ticker.Stop()

    // track last sent digest to only emit when changed
    lastSent := s.currentDigest

    for {
        select {
        case <-ctx.Done():
            return
        case <-ticker.C:
            snap, err := s.Get(ctx)
            if err != nil {
                s.logger.Error("failed to fetch OCI snapshot", zap.Error(err))
                continue
            }

            if s.currentDigest != lastSent {
                s.logger.Debug("sending updated oci snapshot", zap.String("digest", s.currentDigest.String()))
                ch <- snap
                lastSent = s.currentDigest
            } else {
                s.logger.Debug("oci snapshot unchanged")
            }
        }
    }
}

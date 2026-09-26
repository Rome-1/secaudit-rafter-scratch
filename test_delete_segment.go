// +build ignore

package main

import (
"context"
"database/sql"
"fmt"
"log"

sq "github.com/Masterminds/squirrel"
_ "github.com/mattn/go-sqlite3"
"go.flipt.io/flipt/internal/storage"
"go.flipt.io/flipt/internal/storage/sql/sqlite"
flipt "go.flipt.io/flipt/rpc/flipt"
"go.uber.org/zap"
)

func main() {
// Create an in-memory SQLite database
db, err := sql.Open("sqlite3", ":memory:")
if err != nil {
log.Fatal(err)
}
defer db.Close()

// Create the necessary tables
schema := `
CREATE TABLE namespaces (
key TEXT PRIMARY KEY,
name TEXT NOT NULL,
description TEXT,
state_modified_at TIMESTAMP,
created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE segments (
namespace_key TEXT NOT NULL,
key TEXT NOT NULL,
name TEXT NOT NULL,
description TEXT,
match_type INTEGER NOT NULL DEFAULT 0,
created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
PRIMARY KEY (namespace_key, key),
FOREIGN KEY (namespace_key) REFERENCES namespaces(key) ON DELETE CASCADE
);

CREATE TABLE flags (
namespace_key TEXT NOT NULL,
key TEXT NOT NULL,
name TEXT NOT NULL,
description TEXT,
enabled BOOLEAN NOT NULL DEFAULT FALSE,
type INTEGER NOT NULL DEFAULT 0,
default_variant_id TEXT,
created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
PRIMARY KEY (namespace_key, key),
FOREIGN KEY (namespace_key) REFERENCES namespaces(key) ON DELETE CASCADE
);

CREATE TABLE rules (
id TEXT PRIMARY KEY,
namespace_key TEXT NOT NULL,
flag_key TEXT NOT NULL,
rank INTEGER NOT NULL DEFAULT 0,
segment_operator INTEGER NOT NULL DEFAULT 0,
created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
FOREIGN KEY (namespace_key, flag_key) REFERENCES flags(namespace_key, key) ON DELETE CASCADE
);

CREATE TABLE rule_segments (
rule_id TEXT NOT NULL,
namespace_key TEXT NOT NULL,
segment_key TEXT NOT NULL,
UNIQUE (rule_id, namespace_key, segment_key),
FOREIGN KEY (rule_id) REFERENCES rules(id) ON DELETE CASCADE,
FOREIGN KEY (namespace_key, segment_key) REFERENCES segments(namespace_key, key) ON DELETE CASCADE
);

CREATE TABLE rollout_segments (
id TEXT PRIMARY KEY,
namespace_key TEXT NOT NULL,
flag_key TEXT NOT NULL,
rollout_type INTEGER NOT NULL,
rank INTEGER NOT NULL DEFAULT 0,
segment_operator INTEGER NOT NULL DEFAULT 0,
value BOOLEAN NOT NULL DEFAULT FALSE,
created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
FOREIGN KEY (namespace_key, flag_key) REFERENCES flags(namespace_key, key) ON DELETE CASCADE
);

CREATE TABLE rollout_segment_references (
rollout_segment_id TEXT NOT NULL,
namespace_key TEXT NOT NULL,
segment_key TEXT NOT NULL,
UNIQUE (rollout_segment_id, namespace_key, segment_key),
FOREIGN KEY (rollout_segment_id) REFERENCES rollout_segments(id) ON DELETE CASCADE,
FOREIGN KEY (namespace_key, segment_key) REFERENCES segments(namespace_key, key) ON DELETE CASCADE
);
`

if _, err := db.Exec(schema); err != nil {
log.Fatal("Failed to create schema:", err)
}

// Initialize the store
logger, _ := zap.NewDevelopment()
builder := sq.StatementBuilder
store := sqlite.NewStore(db, builder, logger)

ctx := context.Background()

// Create default namespace
_, err = db.Exec("INSERT INTO namespaces (key, name) VALUES ('default', 'Default')")
if err != nil {
log.Fatal("Failed to insert namespace:", err)
}

// Test 1: Create a segment and delete it (should succeed)
fmt.Println("Test 1: Delete segment with no references")
segment, err := store.CreateSegment(ctx, &flipt.CreateSegmentRequest{
NamespaceKey: storage.DefaultNamespace,
Key:          "test-segment",
Name:         "Test Segment",
MatchType:    flipt.MatchType_ALL_MATCH_TYPE,
})
if err != nil {
log.Fatal("Failed to create segment:", err)
}
fmt.Printf("  Created segment: %s/%s\n", segment.NamespaceKey, segment.Key)

err = store.DeleteSegment(ctx, &flipt.DeleteSegmentRequest{
NamespaceKey: storage.DefaultNamespace,
Key:          "test-segment",
})
if err != nil {
log.Fatal("  FAIL: Should be able to delete segment:", err)
}
fmt.Println("  PASS: Successfully deleted segment")

// Test 2: Create a segment with a rule reference (should fail to delete)
fmt.Println("\nTest 2: Try to delete segment referenced by a rule")

// Create flag
_, err = db.Exec("INSERT INTO flags (namespace_key, key, name, enabled, type) VALUES ('default', 'test-flag', 'Test Flag', 1, 0)")
if err != nil {
log.Fatal("Failed to insert flag:", err)
}

// Create segment
segment, err = store.CreateSegment(ctx, &flipt.CreateSegmentRequest{
NamespaceKey: storage.DefaultNamespace,
Key:          "segment-with-rule",
Name:         "Segment With Rule",
MatchType:    flipt.MatchType_ALL_MATCH_TYPE,
})
if err != nil {
log.Fatal("Failed to create segment:", err)
}
fmt.Printf("  Created segment: %s/%s\n", segment.NamespaceKey, segment.Key)

// Create rule
_, err = db.Exec("INSERT INTO rules (id, namespace_key, flag_key, rank) VALUES ('rule-1', 'default', 'test-flag', 1)")
if err != nil {
log.Fatal("Failed to insert rule:", err)
}

// Create rule_segment reference
_, err = db.Exec("INSERT INTO rule_segments (rule_id, namespace_key, segment_key) VALUES ('rule-1', 'default', 'segment-with-rule')")
if err != nil {
log.Fatal("Failed to insert rule_segment:", err)
}
fmt.Println("  Created rule referencing segment")

err = store.DeleteSegment(ctx, &flipt.DeleteSegmentRequest{
NamespaceKey: storage.DefaultNamespace,
Key:          "segment-with-rule",
})
if err == nil {
log.Fatal("  FAIL: Should not be able to delete segment in use")
}
expectedMsg := `segment "default/segment-with-rule" is in use`
if err.Error() != expectedMsg {
log.Fatalf("  FAIL: Wrong error message. Expected: %q, Got: %q", expectedMsg, err.Error())
}
fmt.Printf("  PASS: Got expected error: %s\n", err.Error())

// Test 3: Delete the rule and then delete the segment (should succeed)
fmt.Println("\nTest 3: Delete rule and then delete segment")
_, err = db.Exec("DELETE FROM rule_segments WHERE rule_id = 'rule-1'")
if err != nil {
log.Fatal("Failed to delete rule_segment:", err)
}
_, err = db.Exec("DELETE FROM rules WHERE id = 'rule-1'")
if err != nil {
log.Fatal("Failed to delete rule:", err)
}
fmt.Println("  Deleted rule")

err = store.DeleteSegment(ctx, &flipt.DeleteSegmentRequest{
NamespaceKey: storage.DefaultNamespace,
Key:          "segment-with-rule",
})
if err != nil {
log.Fatal("  FAIL: Should be able to delete segment after rule is removed:", err)
}
fmt.Println("  PASS: Successfully deleted segment")

// Test 4: Create a segment with a rollout reference (should fail to delete)
fmt.Println("\nTest 4: Try to delete segment referenced by a rollout")

// Create segment
segment, err = store.CreateSegment(ctx, &flipt.CreateSegmentRequest{
NamespaceKey: storage.DefaultNamespace,
Key:          "segment-with-rollout",
Name:         "Segment With Rollout",
MatchType:    flipt.MatchType_ALL_MATCH_TYPE,
})
if err != nil {
log.Fatal("Failed to create segment:", err)
}
fmt.Printf("  Created segment: %s/%s\n", segment.NamespaceKey, segment.Key)

// Create rollout_segment
_, err = db.Exec("INSERT INTO rollout_segments (id, namespace_key, flag_key, rollout_type, rank, value) VALUES ('rollout-1', 'default', 'test-flag', 0, 1, 1)")
if err != nil {
log.Fatal("Failed to insert rollout_segment:", err)
}

// Create rollout_segment_reference
_, err = db.Exec("INSERT INTO rollout_segment_references (rollout_segment_id, namespace_key, segment_key) VALUES ('rollout-1', 'default', 'segment-with-rollout')")
if err != nil {
log.Fatal("Failed to insert rollout_segment_reference:", err)
}
fmt.Println("  Created rollout referencing segment")

err = store.DeleteSegment(ctx, &flipt.DeleteSegmentRequest{
NamespaceKey: storage.DefaultNamespace,
Key:          "segment-with-rollout",
})
if err == nil {
log.Fatal("  FAIL: Should not be able to delete segment in use")
}
expectedMsg = `segment "default/segment-with-rollout" is in use`
if err.Error() != expectedMsg {
log.Fatalf("  FAIL: Wrong error message. Expected: %q, Got: %q", expectedMsg, err.Error())
}
fmt.Printf("  PASS: Got expected error: %s\n", err.Error())

fmt.Println("\n=== All tests passed! ===")
}

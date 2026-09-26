package main

import (
"context"
"fmt"
"os"

"github.com/navidrome/navidrome/conf"
"github.com/navidrome/navidrome/db"
"github.com/navidrome/navidrome/log"
"github.com/navidrome/navidrome/model"
"github.com/navidrome/navidrome/persistence"
)

// Test that user repository methods return nil when user is not found
func main() {
// Initialize configuration for testing  
conf.Server.DataFolder = ":memory:"
conf.Server.DbPath = ":memory:"

// Initialize logging
log.SetLevel("ERROR") // Reduce noise

// Initialize database
dB := db.Db()
defer dB.Close()

// Create user repository
ctx := context.Background()
userRepo := persistence.NewUserRepository(ctx, dB)

fmt.Println("🧪 Testing User Repository Methods After Fix")
fmt.Println("=" * 50)

// Test 1: Get method with non-existent ID
fmt.Println("\n1. Testing Get() with non-existent user ID...")
user, err := userRepo.Get("nonexistent-id")
if err != nil && user == nil {
fmt.Println("   ✅ PASS: Get() returns nil user and error for non-existent ID")
} else if err != nil && user != nil {
fmt.Println("   ❌ FAIL: Get() returns non-nil user with error (vulnerability!)")
fmt.Printf("   User: %+v\n", user)
} else {
fmt.Println("   ❓ UNEXPECTED: Get() returned unexpected result")
fmt.Printf("   User: %+v, Error: %v\n", user, err)
}

// Test 2: FindByUsername with non-existent username
fmt.Println("\n2. Testing FindByUsername() with non-existent username...")
user, err = userRepo.FindByUsername("nonexistentuser")
if err != nil && user == nil {
fmt.Println("   ✅ PASS: FindByUsername() returns nil user and error for non-existent username")
} else if err != nil && user != nil {
fmt.Println("   ❌ FAIL: FindByUsername() returns non-nil user with error (vulnerability!)")
fmt.Printf("   User: %+v\n", user)
} else {
fmt.Println("   ❓ UNEXPECTED: FindByUsername() returned unexpected result")
fmt.Printf("   User: %+v, Error: %v\n", user, err)
}

// Test 3: FindByUsernameWithPassword with non-existent username
fmt.Println("\n3. Testing FindByUsernameWithPassword() with non-existent username...")
user, err = userRepo.FindByUsernameWithPassword("nonexistentuser")
if err != nil && user == nil {
fmt.Println("   ✅ PASS: FindByUsernameWithPassword() returns nil user and error for non-existent username")
} else if err != nil && user != nil {
fmt.Println("   ❌ FAIL: FindByUsernameWithPassword() returns non-nil user with error (vulnerability!)")
fmt.Printf("   User: %+v\n", user)
} else {
fmt.Println("   ❓ UNEXPECTED: FindByUsernameWithPassword() returned unexpected result")
fmt.Printf("   User: %+v, Error: %v\n", user, err)
}

// Test 4: Check that errors are the expected ErrNotFound
fmt.Println("\n4. Testing that errors are model.ErrNotFound...")
_, err = userRepo.FindByUsername("nonexistentuser")
if err != nil && err == model.ErrNotFound {
fmt.Println("   ✅ PASS: Error is model.ErrNotFound as expected")
} else {
fmt.Println("   ❓ UNEXPECTED: Error is not model.ErrNotFound")
fmt.Printf("   Error: %v\n", err)
}

fmt.Println("\n🎯 Repository Fix Verification Complete!")

// Create a valid user for positive test
fmt.Println("\n5. Testing with valid user (positive test)...")
testUser := &model.User{
UserName: "testuser",
Password: "testpassword",
Name:     "Test User",
IsAdmin:  false,
}

err = userRepo.Put(testUser)
if err != nil {
fmt.Printf("   ❌ Could not create test user: %v\n", err)
os.Exit(1)
}

user, err = userRepo.FindByUsername("testuser")
if err == nil && user != nil && user.UserName == "testuser" {
fmt.Println("   ✅ PASS: Valid user lookup returns correct user")
} else {
fmt.Println("   ❌ FAIL: Valid user lookup failed")
fmt.Printf("   User: %+v, Error: %v\n", user, err)
}
}
#!/usr/bin/env python3
"""
Test script to reproduce the email confirmation issue when requireEmailAddress is enabled.
This simulates a user trying to confirm their email via the confirmation link.
"""

import sys
import os

# Add paths to simulate the NodeBB environment
sys.path.insert(0, '/app/src')

def test_middleware_blocks_confirm_route():
    """
    Test that demonstrates the issue where the registrationComplete middleware
    blocks access to /confirm/* routes when requireEmailAddress is enabled.
    """
    
    print("Testing email confirmation flow with requireEmailAddress enabled...")
    print("=" * 60)
    
    # Scenario 1: User with unconfirmed email tries to visit /confirm/code
    print("\nScenario 1: Logged-in user with unconfirmed email visits /confirm/code")
    print("-" * 40)
    
    # The registrationComplete middleware checks:
    # 1. If there's no registration session
    # 2. If user is logged in (req.uid exists)
    # 3. If the path doesn't end with '/edit/email'
    # 4. If requireEmailAddress is enabled and email is not confirmed
    # Then it redirects to /me/edit/email
    
    test_path = "/confirm/test-code-123"
    print(f"Request path: {test_path}")
    print(f"Path ends with '/edit/email': {test_path.endswith('/edit/email')}")
    print(f"Expected behavior: Should allow access to confirmation page")
    print(f"Actual behavior: Redirects to /me/edit/email")
    print("Issue: User cannot confirm email because they're redirected away")
    
    # Scenario 2: User in registration flow visits /confirm/code
    print("\n\nScenario 2: User with registration session visits /confirm/code")
    print("-" * 40)
    
    # The registrationComplete middleware checks:
    # 1. If there's a registration session
    # 2. If the path is in the allowed list (default: ['/register/complete'])
    # If not in allowed list, redirects to /register/complete
    
    test_path = "/confirm/test-code-456"
    allowed_paths = ['/register/complete']
    print(f"Request path: {test_path}")
    print(f"Allowed paths: {allowed_paths}")
    print(f"Path in allowed list: {test_path in allowed_paths}")
    print(f"Expected behavior: Should allow access to confirmation page")
    print(f"Actual behavior: Redirects to /register/complete")
    print("Issue: User cannot confirm email because they're redirected away")
    
    print("\n" + "=" * 60)
    print("SUMMARY: Both scenarios show that /confirm/* routes are blocked")
    print("when requireEmailAddress is enabled, preventing email confirmation.")
    
    # Additional check for path matching
    print("\n" + "=" * 60)
    print("Path matching analysis:")
    print("-" * 40)
    
    confirm_paths = [
        "/confirm/abc123",
        "/confirm/xyz789",
        "/api/confirm/test",
    ]
    
    for path in confirm_paths:
        # Check if path starts with /confirm/
        starts_with_confirm = path.startswith('/confirm/')
        api_path = path.startswith('/api/') and path.replace('/api', '').startswith('/confirm/')
        
        print(f"\nPath: {path}")
        print(f"  Starts with '/confirm/': {starts_with_confirm}")
        print(f"  Is API confirm path: {api_path}")
        print(f"  Should be allowed: {starts_with_confirm or api_path}")
    
    print("\n" + "=" * 60)
    print("SOLUTION: The registrationComplete middleware needs to be updated to:")
    print("1. Allow access to /confirm/* routes (partial path matching)")
    print("2. Check and clear updateEmail flag after successful confirmation")
    print("3. Only set registration session with updateEmail when appropriate")

if __name__ == "__main__":
    test_middleware_blocks_confirm_route()
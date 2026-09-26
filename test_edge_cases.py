#!/usr/bin/env python3

import os
import sys
import tempfile

# Add the library path to import Ansible modules
sys.path.insert(0, '/app/lib')

from ansible.plugins.lookup.password import _parse_content, _format_content

def test_parse_content_edge_cases():
    """Test edge cases for _parse_content function"""
    
    print("=== Testing _parse_content edge cases ===")
    
    # Test 1: Plain password without salt or ident
    print("\nTest 1: Plain password without salt or ident")
    content = "mypassword"
    password, salt, ident = _parse_content(content)
    print(f"Input: {repr(content)}")
    print(f"Output: password={repr(password)}, salt={repr(salt)}, ident={repr(ident)}")
    assert password == "mypassword"
    assert salt is None
    assert ident is None
    print("✓ PASSED")
    
    # Test 2: Password with salt but no ident
    print("\nTest 2: Password with salt but no ident")
    content = "mypassword salt=abcd1234"
    password, salt, ident = _parse_content(content)
    print(f"Input: {repr(content)}")
    print(f"Output: password={repr(password)}, salt={repr(salt)}, ident={repr(ident)}")
    assert password == "mypassword"
    assert salt == "abcd1234"
    assert ident is None
    print("✓ PASSED")
    
    # Test 3: Password with both salt and ident
    print("\nTest 3: Password with both salt and ident")
    content = "mypassword salt=abcd1234 ident=2b"
    password, salt, ident = _parse_content(content)
    print(f"Input: {repr(content)}")
    print(f"Output: password={repr(password)}, salt={repr(salt)}, ident={repr(ident)}")
    assert password == "mypassword"
    assert salt == "abcd1234"
    assert ident == "2b"
    print("✓ PASSED")
    
    # Test 4: Password containing "salt=" in the password part
    print("\nTest 4: Password containing 'salt=' in the password part")
    content = "my salt=fake password salt=abcd1234 ident=2b"
    password, salt, ident = _parse_content(content)
    print(f"Input: {repr(content)}")
    print(f"Output: password={repr(password)}, salt={repr(salt)}, ident={repr(ident)}")
    assert password == "my salt=fake password"
    assert salt == "abcd1234"
    assert ident == "2b"
    print("✓ PASSED")
    
    # Test 5: Password containing "ident=" in the password part
    print("\nTest 5: Password containing 'ident=' in the password part")
    content = "my ident=fake password salt=abcd1234 ident=2b"
    password, salt, ident = _parse_content(content)
    print(f"Input: {repr(content)}")
    print(f"Output: password={repr(password)}, salt={repr(salt)}, ident={repr(ident)}")
    assert password == "my ident=fake password"
    assert salt == "abcd1234"
    assert ident == "2b"
    print("✓ PASSED")
    
    # Test 6: Multiple ident values (should pick the last one - this tests the rindex behavior)
    print("\nTest 6: Multiple ident values in salt part")
    content = "password salt=abcd ident=2a ident=2b"
    password, salt, ident = _parse_content(content)
    print(f"Input: {repr(content)}")
    print(f"Output: password={repr(password)}, salt={repr(salt)}, ident={repr(ident)}")
    assert password == "password"
    assert salt == "abcd ident=2a"
    assert ident == "2b"
    print("✓ PASSED")
    
    # Test 7: Empty salt
    print("\nTest 7: Empty salt")
    content = "password salt= ident=2b"
    password, salt, ident = _parse_content(content)
    print(f"Input: {repr(content)}")
    print(f"Output: password={repr(password)}, salt={repr(salt)}, ident={repr(ident)}")
    assert password == "password"
    assert salt == ""
    assert ident == "2b"
    print("✓ PASSED")
    
    # Test 8: Empty ident
    print("\nTest 8: Empty ident")
    content = "password salt=abcd1234 ident="
    password, salt, ident = _parse_content(content)
    print(f"Input: {repr(content)}")
    print(f"Output: password={repr(password)}, salt={repr(salt)}, ident={repr(ident)}")
    assert password == "password"
    assert salt == "abcd1234"
    assert ident == ""
    print("✓ PASSED")
    
    print("\n=== All _parse_content tests passed! ===")

def test_format_content_edge_cases():
    """Test edge cases for _format_content function"""
    
    print("\n=== Testing _format_content edge cases ===")
    
    # Test 1: Plain password, no encryption
    print("\nTest 1: Plain password, no encryption")
    result = _format_content("mypassword", None)
    print(f"Result: {repr(result)}")
    assert result == "mypassword"
    print("✓ PASSED")
    
    # Test 2: Password with salt but no ident
    print("\nTest 2: Password with salt but no ident")
    result = _format_content("mypassword", "abcd1234", encrypt="sha256_crypt")
    print(f"Result: {repr(result)}")
    assert result == "mypassword salt=abcd1234"
    print("✓ PASSED")
    
    # Test 3: Password with salt and ident
    print("\nTest 3: Password with salt and ident")
    result = _format_content("mypassword", "abcd1234", encrypt="bcrypt", ident="2b")
    print(f"Result: {repr(result)}")
    assert result == "mypassword salt=abcd1234 ident=2b"
    print("✓ PASSED")
    
    # Test 4: Password with salt and empty ident
    print("\nTest 4: Password with salt and empty ident")
    result = _format_content("mypassword", "abcd1234", encrypt="bcrypt", ident="")
    print(f"Result: {repr(result)}")
    assert result == "mypassword salt=abcd1234"
    print("✓ PASSED")
    
    print("\n=== All _format_content tests passed! ===")

def test_round_trip():
    """Test that format->parse->format is stable"""
    
    print("\n=== Testing round-trip stability ===")
    
    test_cases = [
        ("password", "salt123", "2b"),
        ("complex password with spaces", "salt456", "2a"),
        ("password", "salt789", ""),
        ("password", "salt000", None),
    ]
    
    for i, (password, salt, ident) in enumerate(test_cases, 1):
        print(f"\nTest {i}: password={repr(password)}, salt={repr(salt)}, ident={repr(ident)}")
        
        # Format
        formatted = _format_content(password, salt, encrypt="bcrypt", ident=ident)
        print(f"Formatted: {repr(formatted)}")
        
        # Parse
        parsed_password, parsed_salt, parsed_ident = _parse_content(formatted)
        print(f"Parsed: password={repr(parsed_password)}, salt={repr(parsed_salt)}, ident={repr(parsed_ident)}")
        
        # Verify
        assert parsed_password == password
        assert parsed_salt == salt
        # Handle None vs empty string for ident
        expected_ident = ident if ident else None
        assert parsed_ident == expected_ident
        
        # Format again
        formatted2 = _format_content(parsed_password, parsed_salt, encrypt="bcrypt", ident=parsed_ident)
        print(f"Formatted again: {repr(formatted2)}")
        
        # Should be identical
        assert formatted == formatted2
        print("✓ PASSED")
    
    print("\n=== All round-trip tests passed! ===")

if __name__ == "__main__":
    test_parse_content_edge_cases()
    test_format_content_edge_cases()
    test_round_trip()
    print("\n🎉 ALL EDGE CASE TESTS PASSED! 🎉")
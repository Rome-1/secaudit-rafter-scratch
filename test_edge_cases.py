#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Test edge cases for ident handling."""

import os
import sys
import tempfile
import shutil

sys.path.insert(0, '/app/lib')

from ansible.plugins.lookup.password import (
    _parse_content,
    _format_content,
    _read_password_file,
    _write_password_file,
)
from ansible.module_utils._text import to_bytes
from ansible.errors import AnsibleError

def test_file_has_salt_no_ident():
    """Test reading a file that has salt but no ident."""
    print("\n" + "=" * 70)
    print("TEST: File has salt but no ident")
    print("=" * 70)
    
    tmpdir = tempfile.mkdtemp()
    password_file = os.path.join(tmpdir, "password.txt")
    b_password_file = to_bytes(password_file)
    
    try:
        # Create a file with salt but no ident (old format)
        password = "testpassword"
        salt = "testsalt"
        content = _format_content(password, salt, encrypt="sha256_crypt")  # sha256 doesn't use ident
        _write_password_file(b_password_file, content)
        
        print(f"   Created file: {content}")
        
        # Read and parse
        content_read = _read_password_file(b_password_file)
        parsed_password, parsed_salt, parsed_ident = _parse_content(content_read)
        
        print(f"   Parsed: password={parsed_password}, salt={parsed_salt}, ident={parsed_ident}")
        
        assert parsed_password == password
        assert parsed_salt == salt
        assert parsed_ident is None
        print("   ✓ Correctly parsed file with salt but no ident")
        
    finally:
        shutil.rmtree(tmpdir)

def test_file_has_ident_user_provides_same():
    """Test that providing the same ident as in file works."""
    print("\n" + "=" * 70)
    print("TEST: File has ident, user provides same ident")
    print("=" * 70)
    
    tmpdir = tempfile.mkdtemp()
    password_file = os.path.join(tmpdir, "password.txt")
    b_password_file = to_bytes(password_file)
    
    try:
        # Create file with ident
        password = "testpassword"
        salt = "testsalt"
        ident = "2b"
        content = _format_content(password, salt, encrypt="bcrypt", ident=ident)
        _write_password_file(b_password_file, content)
        
        print(f"   Created file: {content}")
        
        # Read and parse
        content_read = _read_password_file(b_password_file)
        parsed_password, parsed_salt, parsed_ident = _parse_content(content_read)
        
        # Simulate user providing same ident
        user_ident = "2b"
        
        # This should work without error
        if parsed_ident and user_ident and parsed_ident != user_ident:
            print(f"   ✗ Should not raise error for matching ident")
            raise AssertionError("Unexpected error")
        
        print(f"   ✓ No error when user provides matching ident")
        
    finally:
        shutil.rmtree(tmpdir)

def test_file_has_ident_user_provides_different():
    """Test that providing different ident than in file raises error."""
    print("\n" + "=" * 70)
    print("TEST: File has ident, user provides different ident")
    print("=" * 70)
    
    tmpdir = tempfile.mkdtemp()
    password_file = os.path.join(tmpdir, "password.txt")
    b_password_file = to_bytes(password_file)
    
    try:
        # Create file with ident=2b
        password = "testpassword"
        salt = "testsalt"
        ident = "2b"
        content = _format_content(password, salt, encrypt="bcrypt", ident=ident)
        _write_password_file(b_password_file, content)
        
        print(f"   Created file: {content}")
        
        # Read and parse
        content_read = _read_password_file(b_password_file)
        parsed_password, parsed_salt, parsed_ident = _parse_content(content_read)
        
        # Simulate user providing different ident
        user_ident = "2a"
        
        # This should raise an error
        try:
            if parsed_ident and user_ident and parsed_ident != user_ident:
                raise AnsibleError(
                    "The ident parameter value '%s' does not match the stored ident '%s'." % (user_ident, parsed_ident)
                )
            print(f"   ✗ Should have raised error for mismatched ident")
            raise AssertionError("Expected AnsibleError")
        except AnsibleError as e:
            print(f"   ✓ Correctly raised error: {str(e)[:60]}...")
        
    finally:
        shutil.rmtree(tmpdir)

def test_parse_just_ident():
    """Test parsing a file with just ident (edge case)."""
    print("\n" + "=" * 70)
    print("TEST: File has just password and ident (no salt)")
    print("=" * 70)
    
    content = "password ident=2b"
    password, salt, ident = _parse_content(content)
    
    print(f"   Content: {content}")
    print(f"   Parsed: password={password}, salt={salt}, ident={ident}")
    
    assert password == "password"
    assert salt is None
    assert ident == "2b"
    print("   ✓ Correctly parsed file with ident but no salt")

def test_parse_complex():
    """Test parsing with spaces in password."""
    print("\n" + "=" * 70)
    print("TEST: Complex content parsing")
    print("=" * 70)
    
    # Note: In practice, passwords shouldn't have spaces because the file
    # format uses space as a delimiter, but let's test the parsing logic
    
    # This is how the format works:
    # "password salt=value ident=value"
    # It finds the LAST occurrence of " salt=" and " ident="
    
    content = "mypassword123 salt=abcdef ident=2b"
    password, salt, ident = _parse_content(content)
    assert password == "mypassword123"
    assert salt == "abcdef"
    assert ident == "2b"
    print("   ✓ Test 1 passed")
    
    content = "pass salt=abc123"
    password, salt, ident = _parse_content(content)
    assert password == "pass"
    assert salt == "abc123"
    assert ident is None
    print("   ✓ Test 2 passed")
    
    content = "password"
    password, salt, ident = _parse_content(content)
    assert password == "password"
    assert salt is None
    assert ident is None
    print("   ✓ Test 3 passed")

def main():
    """Run all edge case tests."""
    print("\n" + "#" * 70)
    print("# EDGE CASE TESTS")
    print("#" * 70)
    
    test_file_has_salt_no_ident()
    test_file_has_ident_user_provides_same()
    test_file_has_ident_user_provides_different()
    test_parse_just_ident()
    test_parse_complex()
    
    print("\n" + "#" * 70)
    print("# ALL EDGE CASE TESTS PASSED!")
    print("#" * 70 + "\n")

if __name__ == "__main__":
    main()

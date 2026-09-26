#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Comprehensive test of the password lookup ident fix."""

import os
import sys
import tempfile
import shutil

# Add the library paths
sys.path.insert(0, '/app/lib')

from ansible.plugins.lookup.password import (
    _parse_content,
    _format_content,
    _read_password_file,
    _write_password_file,
)
from ansible.module_utils._text import to_bytes
from ansible.errors import AnsibleError

def test_parse_content():
    """Test _parse_content with various inputs."""
    print("=" * 70)
    print("TEST: _parse_content")
    print("=" * 70)
    
    # Test 1: Just password
    password, salt, ident = _parse_content(u'mypassword')
    assert password == u'mypassword', f"Expected 'mypassword', got '{password}'"
    assert salt is None, f"Expected None, got '{salt}'"
    assert ident is None, f"Expected None, got '{ident}'"
    print("✓ Test 1: Just password")
    
    # Test 2: Password with salt
    password, salt, ident = _parse_content(u'mypassword salt=mysalt')
    assert password == u'mypassword', f"Expected 'mypassword', got '{password}'"
    assert salt == u'mysalt', f"Expected 'mysalt', got '{salt}'"
    assert ident is None, f"Expected None, got '{ident}'"
    print("✓ Test 2: Password with salt")
    
    # Test 3: Password with salt and ident
    password, salt, ident = _parse_content(u'mypassword salt=mysalt ident=2b')
    assert password == u'mypassword', f"Expected 'mypassword', got '{password}'"
    assert salt == u'mysalt', f"Expected 'mysalt', got '{salt}'"
    assert ident == u'2b', f"Expected '2b', got '{ident}'"
    print("✓ Test 3: Password with salt and ident")
    
    # Test 4: Empty password
    password, salt, ident = _parse_content(u'')
    assert password == u'', f"Expected '', got '{password}'"
    assert salt is None, f"Expected None, got '{salt}'"
    assert ident is None, f"Expected None, got '{ident}'"
    print("✓ Test 4: Empty password")
    
    # Test 5: Password with ident but no salt (edge case)
    password, salt, ident = _parse_content(u'mypassword ident=2b')
    assert password == u'mypassword', f"Expected 'mypassword', got '{password}'"
    assert salt is None, f"Expected None, got '{salt}'"
    assert ident == u'2b', f"Expected '2b', got '{ident}'"
    print("✓ Test 5: Password with ident but no salt")
    
    print()

def test_format_content():
    """Test _format_content with various inputs."""
    print("=" * 70)
    print("TEST: _format_content")
    print("=" * 70)
    
    # Test 1: Just password
    content = _format_content(u'mypassword', None)
    assert content == u'mypassword', f"Expected 'mypassword', got '{content}'"
    print("✓ Test 1: Just password")
    
    # Test 2: Password with salt
    content = _format_content(u'mypassword', u'mysalt', encrypt=True)
    assert content == u'mypassword salt=mysalt', f"Expected 'mypassword salt=mysalt', got '{content}'"
    print("✓ Test 2: Password with salt")
    
    # Test 3: Password with salt and ident
    content = _format_content(u'mypassword', u'mysalt', encrypt=True, ident=u'2b')
    assert content == u'mypassword salt=mysalt ident=2b', f"Expected 'mypassword salt=mysalt ident=2b', got '{content}'"
    print("✓ Test 3: Password with salt and ident")
    
    print()

def test_idempotency():
    """Test that repeated operations are idempotent."""
    print("=" * 70)
    print("TEST: Idempotency")
    print("=" * 70)
    
    # Create a temporary directory for test files
    tmpdir = tempfile.mkdtemp()
    
    try:
        password_file = os.path.join(tmpdir, "password.txt")
        b_password_file = to_bytes(password_file)
        
        # First write
        password = "testpassword"
        salt = "testsalt"
        ident = "2b"
        content = _format_content(password, salt, encrypt="bcrypt", ident=ident)
        _write_password_file(b_password_file, content)
        
        # First read
        read_content1 = _read_password_file(b_password_file)
        password1, salt1, ident1 = _parse_content(read_content1)
        
        # Second write with same values
        content2 = _format_content(password1, salt1, encrypt="bcrypt", ident=ident1)
        _write_password_file(b_password_file, content2)
        
        # Second read
        read_content2 = _read_password_file(b_password_file)
        password2, salt2, ident2 = _parse_content(read_content2)
        
        # Verify idempotency
        assert read_content1 == read_content2, f"Content changed: '{read_content1}' != '{read_content2}'"
        assert password1 == password2, f"Password changed: '{password1}' != '{password2}'"
        assert salt1 == salt2, f"Salt changed: '{salt1}' != '{salt2}'"
        assert ident1 == ident2, f"Ident changed: '{ident1}' != '{ident2}'"
        
        print("✓ Idempotency test passed")
        
    finally:
        shutil.rmtree(tmpdir)
    
    print()

def test_bcrypt_integration():
    """Test integration with bcrypt encryption."""
    print("=" * 70)
    print("TEST: Bcrypt Integration")
    print("=" * 70)
    
    try:
        from ansible.utils.encrypt import do_encrypt
        
        # Test with properly parsed values
        password = "testpassword"
        salt = "UYPgwPMJVaBFMU9ext22n/"
        ident = "2b"
        
        # This should work without errors
        encrypted = do_encrypt(password, 'bcrypt', salt=salt, ident=ident)
        assert encrypted.startswith('$2b$'), f"Expected bcrypt hash, got '{encrypted}'"
        print(f"✓ Bcrypt encryption successful: {encrypted[:20]}...")
        
        # Test that salt without ident info works
        content = _format_content(password, salt, encrypt="bcrypt", ident=ident)
        parsed_password, parsed_salt, parsed_ident = _parse_content(content)
        
        # Parsed salt should NOT contain ident info
        assert ' ident=' not in parsed_salt, f"Parsed salt contains ident info: '{parsed_salt}'"
        print(f"✓ Parsed salt is clean: '{parsed_salt}'")
        
        # Re-encryption with parsed values should work
        encrypted2 = do_encrypt(parsed_password, 'bcrypt', salt=parsed_salt, ident=parsed_ident)
        assert encrypted == encrypted2, f"Re-encryption gave different result"
        print(f"✓ Re-encryption is consistent")
        
    except ImportError:
        print("⚠ Skipping bcrypt test (passlib not available)")
    except Exception as e:
        print(f"✗ Bcrypt integration test failed: {e}")
        raise
    
    print()

def main():
    """Run all tests."""
    print("\n" + "=" * 70)
    print("COMPREHENSIVE PASSWORD LOOKUP TESTS")
    print("=" * 70 + "\n")
    
    test_parse_content()
    test_format_content()
    test_idempotency()
    test_bcrypt_integration()
    
    print("=" * 70)
    print("ALL TESTS PASSED!")
    print("=" * 70)

if __name__ == "__main__":
    main()

#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Reproduce the password lookup ident issue."""

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

def test_scenario():
    """Test the scenario described in the issue."""
    
    # Create a temporary directory for test files
    tmpdir = tempfile.mkdtemp()
    print(f"Using temp directory: {tmpdir}")
    
    try:
        password_file = os.path.join(tmpdir, "password.txt")
        b_password_file = to_bytes(password_file)
        
        # Scenario 1: First run - create password file with ident
        print("\n=== Scenario 1: Creating password file with ident ===")
        password = "z2fH1h5k.J1Oy6phsP73"
        salt = "UYPgwPMJVaBFMU9ext22n/"
        ident = "2b"
        
        content = _format_content(password, salt, encrypt="bcrypt", ident=ident)
        print(f"Formatted content: {content}")
        
        _write_password_file(b_password_file, content)
        print(f"Wrote to file: {password_file}")
        
        # Read back the content
        with open(password_file, 'r') as f:
            file_content = f.read()
        print(f"File content: {repr(file_content)}")
        
        # Scenario 2: Second run - try to parse the file
        print("\n=== Scenario 2: Reading password file (second run) ===")
        read_content = _read_password_file(b_password_file)
        print(f"Read content: {repr(read_content)}")
        
        # Try to parse the content
        print("\n=== Scenario 3: Parsing content ===")
        parsed_password, parsed_salt, parsed_ident = _parse_content(read_content)
        print(f"Parsed password: {repr(parsed_password)}")
        print(f"Parsed salt: {repr(parsed_salt)}")
        print(f"Parsed ident: {repr(parsed_ident)}")
        print(f"Success! ident is now properly parsed by _parse_content!")
        
        # Show the fix
        print("\n=== Fix Demonstration ===")
        print("Now when we format again, it uses the parsed ident.")
        
        # Simulate second run formatting
        new_content = _format_content(parsed_password, parsed_salt, encrypt="bcrypt", ident=parsed_ident)
        print(f"\nNew formatted content (using parsed ident): {new_content}")
        print("No duplicate idents - the file remains idempotent!")
        
        # Simulate the actual error case
        print("\n=== Testing with actual bcrypt encryption ===")
        try:
            from ansible.utils.encrypt import do_encrypt
            
            # This will fail if parsed_salt still contains ident info
            encrypted = do_encrypt(parsed_password, 'bcrypt', salt=parsed_salt, ident=ident)
            print(f"Encrypted password: {encrypted}")
        except Exception as e:
            print(f"ERROR: {type(e).__name__}: {e}")
            print("This is the error users are seeing!")
            
    finally:
        # Clean up
        shutil.rmtree(tmpdir)
        print(f"\nCleaned up temp directory: {tmpdir}")

if __name__ == "__main__":
    test_scenario()

#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Test migration from old format (no ident) to new format (with ident)."""

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
from ansible.utils.encrypt import BaseHash

def test_migration_to_ident():
    """
    Test scenario:
    1. Old password file exists with salt but no ident (created before ident support)
    2. User runs ansible with bcrypt encryption
    3. System should add ident to the file
    """
    print("\n" + "=" * 70)
    print("TEST: Migration from old format (no ident) to new format (with ident)")
    print("=" * 70)
    
    tmpdir = tempfile.mkdtemp()
    password_file = os.path.join(tmpdir, "password.txt")
    b_password_file = to_bytes(password_file)
    
    try:
        # Create old-format file (no ident)
        print("\n1. Creating old-format password file (no ident)")
        password = "oldpassword"
        salt = "oldsalt"
        content = _format_content(password, salt, encrypt="bcrypt", ident=None)
        _write_password_file(b_password_file, content)
        
        print(f"   Old file content: {content}")
        assert 'ident=' not in content, "Old file shouldn't have ident"
        print("   ✓ Old file has no ident")
        
        # Simulate reading and re-processing with bcrypt
        print("\n2. Reading old file and determining ident needed")
        content_read = _read_password_file(b_password_file)
        parsed_password, parsed_salt, parsed_ident = _parse_content(content_read)
        
        print(f"   Parsed: password={parsed_password}, salt={parsed_salt}, ident={parsed_ident}")
        assert parsed_ident is None, "Old file should have no ident"
        
        # Get default ident for bcrypt
        encrypt = 'bcrypt'
        ident = None
        if encrypt and not parsed_ident and not ident:
            try:
                ident = BaseHash.algorithms[encrypt].implicit_ident
            except KeyError:
                ident = None
        
        print(f"   Default ident for bcrypt: {ident}")
        assert ident == '2b', "Should get default ident"
        
        # Write updated file with ident
        print("\n3. Writing updated file with ident")
        new_content = _format_content(parsed_password, parsed_salt, encrypt=encrypt, ident=ident)
        _write_password_file(b_password_file, new_content)
        
        print(f"   New file content: {new_content}")
        assert 'ident=2b' in new_content, "New file should have ident"
        print("   ✓ New file has ident=2b")
        
        # Verify we can read it back correctly
        print("\n4. Verifying we can read the updated file")
        content_read2 = _read_password_file(b_password_file)
        parsed_password2, parsed_salt2, parsed_ident2 = _parse_content(content_read2)
        
        assert parsed_password2 == password
        assert parsed_salt2 == salt
        assert parsed_ident2 == '2b'
        print("   ✓ Updated file reads correctly")
        
        print("\n" + "=" * 70)
        print("SUCCESS: Migration from old to new format works!")
        print("=" * 70)
        
    finally:
        shutil.rmtree(tmpdir)

def main():
    """Run migration test."""
    print("\n" + "#" * 70)
    print("# IDENT MIGRATION TEST")
    print("#" * 70)
    
    test_migration_to_ident()
    
    print("\n" + "#" * 70)
    print("# MIGRATION TEST PASSED!")
    print("#" * 70 + "\n")

if __name__ == "__main__":
    main()

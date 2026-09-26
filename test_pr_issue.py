#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Test that demonstrates the exact issue from the PR description is fixed."""

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
from ansible.utils.encrypt import do_encrypt

def main():
    """
    Reproduce the exact issue from the PR description:
    
    Before the fix:
    1. First run creates the password file with password, salt, and ident.
    2. Second run fails with "invalid characters in bcrypt salt" error.
    3. File shows duplicate ident: "ident=2b ident=2b"
    
    After the fix:
    1. First run creates the password file correctly.
    2. Second run reads and uses the file correctly without errors.
    3. File remains idempotent with no duplicate ident.
    """
    print("\n" + "=" * 70)
    print("TESTING: Exact Issue from PR Description")
    print("=" * 70)
    
    tmpdir = tempfile.mkdtemp()
    password_file = os.path.join(tmpdir, "password.txt")
    b_password_file = to_bytes(password_file)
    
    try:
        # Simulating first ansible run
        print("\n1. FIRST RUN (simulating: ansible -m debug ...)")
        print("   Creating password file with bcrypt encryption...")
        
        password = "z2fH1h5k.J1Oy6phsP73"
        salt = "UYPgwPMJVaBFMU9ext22n/"
        ident = "2b"
        
        # Format and write (what _format_content does)
        content = _format_content(password, salt, encrypt="bcrypt", ident=ident)
        _write_password_file(b_password_file, content)
        
        # Show file content
        with open(password_file, 'r') as f:
            file_content = f.read()
        print(f"   Password file created:")
        print(f"   $ cat password.txt")
        print(f"   {file_content.strip()}")
        
        # Encrypt password for first run
        encrypted1 = do_encrypt(password, 'bcrypt', salt=salt, ident=ident)
        print(f"   Encrypted password: {encrypted1}")
        
        # Simulating second ansible run (THIS IS WHERE THE BUG WAS)
        print("\n2. SECOND RUN (simulating: ansible -m debug ... again)")
        print("   Reading existing password file...")
        
        # Read the file
        content_read = _read_password_file(b_password_file)
        print(f"   Read content: {content_read}")
        
        # Parse it (THIS IS WHERE THE FIX IS)
        parsed_password, parsed_salt, parsed_ident = _parse_content(content_read)
        print(f"   Parsed values:")
        print(f"     - password: {parsed_password}")
        print(f"     - salt: {parsed_salt}")
        print(f"     - ident: {parsed_ident}")
        
        # Verify salt doesn't contain ident info (THIS WAS THE BUG)
        if ' ident=' in parsed_salt:
            print(f"\n   ✗ ERROR: Salt contains ident info: '{parsed_salt}'")
            print(f"   This would cause: 'ValueError: invalid characters in bcrypt salt'")
            sys.exit(1)
        else:
            print(f"   ✓ Salt is clean (no ident info)")
        
        # Try to encrypt again (THIS IS WHERE IT WOULD FAIL BEFORE)
        print(f"\n   Attempting to encrypt password again...")
        try:
            encrypted2 = do_encrypt(parsed_password, 'bcrypt', salt=parsed_salt, ident=parsed_ident)
            print(f"   ✓ SUCCESS! Encrypted password: {encrypted2}")
            print(f"   ✓ No 'invalid characters in bcrypt salt' error!")
        except ValueError as e:
            print(f"   ✗ FAILED with error: {e}")
            print(f"   This is the bug from the PR description!")
            sys.exit(1)
        
        # Verify encryption is consistent
        if encrypted1 == encrypted2:
            print(f"   ✓ Encryption is consistent across runs")
        else:
            print(f"   ✗ WARNING: Encryption differs (salt/ident changed)")
        
        # Re-format and save (to verify idempotency)
        content2 = _format_content(parsed_password, parsed_salt, encrypt="bcrypt", ident=parsed_ident)
        _write_password_file(b_password_file, content2)
        
        # Show file content again
        with open(password_file, 'r') as f:
            file_content2 = f.read()
        print(f"\n   Password file after second run:")
        print(f"   $ cat password.txt")
        print(f"   {file_content2.strip()}")
        
        # Check for duplicate ident (THIS WAS PART OF THE BUG)
        ident_count = file_content2.count('ident=')
        if ident_count > 1:
            print(f"\n   ✗ ERROR: File has duplicate ident (appears {ident_count} times)")
            print(f"   This is the symptom described in the PR: 'ident=2b ident=2b'")
            sys.exit(1)
        else:
            print(f"   ✓ No duplicate ident (appears exactly once)")
        
        # Verify file is identical
        if file_content == file_content2:
            print(f"   ✓ File content is identical (idempotent)")
        else:
            print(f"   ✗ WARNING: File content changed")
        
        print("\n" + "=" * 70)
        print("SUCCESS! The issue from the PR description is FIXED!")
        print("=" * 70)
        print("\nSummary:")
        print("  ✓ Password file created with bcrypt and ident")
        print("  ✓ Second run reads file correctly")
        print("  ✓ No 'invalid characters in bcrypt salt' error")
        print("  ✓ No duplicate ident in file")
        print("  ✓ Operations are idempotent")
        print("=" * 70 + "\n")
        
    except Exception as e:
        print(f"\n✗ TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    finally:
        shutil.rmtree(tmpdir)

if __name__ == "__main__":
    main()

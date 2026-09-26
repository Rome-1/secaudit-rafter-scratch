#!/usr/bin/env python3

import os
import sys
import tempfile

# Add the library path to import Ansible modules
sys.path.insert(0, '/app/lib')

from ansible.plugins.lookup.password import _parse_content, _format_content, _write_password_file, _read_password_file
from ansible.module_utils._text import to_bytes
from ansible.utils.encrypt import do_encrypt

def test_original_issue():
    """Test the original issue described in the PR"""
    
    # Create a temporary file
    temp_dir = tempfile.mkdtemp()
    password_file = os.path.join(temp_dir, 'password.txt')
    b_path = to_bytes(password_file, errors='surrogate_or_strict')
    
    print(f"Using password file: {password_file}")
    
    # Simulate the original problematic sequence
    password = "z2fH1h5k.J1Oy6phsP73"
    salt = "UYPgwPMJVaBFMU9ext22n/"
    ident = "2b"
    
    print("=== Simulating original issue scenario ===")
    
    # First execution: create file with bcrypt
    print("First execution - creating file...")
    content1 = _format_content(password, salt, encrypt="bcrypt", ident=ident)
    print(f"Content to write: {repr(content1)}")
    _write_password_file(b_path, content1)
    
    # Read back and verify
    read_content1 = _read_password_file(b_path)
    print(f"Content read back: {repr(read_content1)}")
    
    # Parse with the OLD logic (simulate bug)
    print("\n--- Simulating OLD (buggy) parsing logic ---")
    # This is what the old _parse_content would do:
    old_password = read_content1
    old_salt = None
    salt_slug = u' salt='
    try:
        sep = read_content1.rindex(salt_slug)
        old_salt = old_password[sep + len(salt_slug):]  # This would be "UYPgwPMJVaBFMU9ext22n/ ident=2b"
        old_password = read_content1[:sep]
    except ValueError:
        pass
    
    print(f"OLD parsing - password: {repr(old_password)}")
    print(f"OLD parsing - salt: {repr(old_salt)}")
    
    # Try to encrypt with old parsing - this should fail
    print("Trying to encrypt with OLD parsing...")
    try:
        encrypted_old = do_encrypt(old_password, "bcrypt", salt=old_salt, ident=ident)
        print(f"✗ OLD parsing unexpectedly succeeded: {encrypted_old}")
    except Exception as e:
        print(f"✓ OLD parsing correctly failed: {e}")
    
    # Parse with the NEW logic (our fix)
    print("\n--- Testing NEW (fixed) parsing logic ---")
    new_password, new_salt, new_ident = _parse_content(read_content1)
    print(f"NEW parsing - password: {repr(new_password)}")
    print(f"NEW parsing - salt: {repr(new_salt)}")
    print(f"NEW parsing - ident: {repr(new_ident)}")
    
    # Try to encrypt with new parsing - this should succeed
    print("Trying to encrypt with NEW parsing...")
    try:
        encrypted_new = do_encrypt(new_password, "bcrypt", salt=new_salt, ident=new_ident)
        print(f"✓ NEW parsing succeeded: {encrypted_new}")
    except Exception as e:
        print(f"✗ NEW parsing failed: {e}")
        return False
    
    # Second execution with NEW logic - should not create duplicate ident
    print("\nSecond execution with NEW logic...")
    content2 = _format_content(new_password, new_salt, encrypt="bcrypt", ident=new_ident)
    print(f"Content to write on second run: {repr(content2)}")
    _write_password_file(b_path, content2)
    
    # Read back and verify no duplication
    read_content2 = _read_password_file(b_path)
    print(f"Content read back on second run: {repr(read_content2)}")
    
    if read_content1 == read_content2:
        print("✓ Content is stable - no duplication occurred")
    else:
        print("✗ Content changed - duplication may have occurred")
        return False
    
    # Parse again and verify
    final_password, final_salt, final_ident = _parse_content(read_content2)
    print(f"Final parsing - password: {repr(final_password)}")
    print(f"Final parsing - salt: {repr(final_salt)}")
    print(f"Final parsing - ident: {repr(final_ident)}")
    
    # Final encryption test
    try:
        encrypted_final = do_encrypt(final_password, "bcrypt", salt=final_salt, ident=final_ident)
        print(f"✓ Final encryption succeeded: {encrypted_final}")
    except Exception as e:
        print(f"✗ Final encryption failed: {e}")
        return False
    
    # Verify all encrypted passwords are the same
    if encrypted_new == encrypted_final:
        print("✓ All encrypted passwords are consistent")
    else:
        print("✗ Encrypted passwords are inconsistent")
        return False
    
    print("\n=== Original issue has been FIXED! ===")
    
    # Clean up
    try:
        os.remove(password_file)
        os.rmdir(temp_dir)
    except:
        pass
    
    return True

if __name__ == "__main__":
    success = test_original_issue()
    sys.exit(0 if success else 1)
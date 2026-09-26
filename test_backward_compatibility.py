#!/usr/bin/env python3

import os
import sys
import tempfile

# Add the library path to import Ansible modules
sys.path.insert(0, '/app/lib')

from ansible.plugins.lookup.password import _parse_content, _format_content, _write_password_file, _read_password_file
from ansible.module_utils._text import to_bytes
from ansible.utils.encrypt import do_encrypt

def test_backward_compatibility():
    """Test that existing password files without ident still work"""
    
    # Create a temporary file
    temp_dir = tempfile.mkdtemp()
    password_file = os.path.join(temp_dir, 'password.txt')
    b_path = to_bytes(password_file, errors='surrogate_or_strict')
    
    print(f"Using password file: {password_file}")
    
    print("=== Testing backward compatibility ===")
    
    # Test 1: Old format without salt or ident
    print("\nTest 1: Plain password file (no salt, no ident)")
    old_content = "plainpassword"
    _write_password_file(b_path, old_content)
    
    read_content = _read_password_file(b_path)
    password, salt, ident = _parse_content(read_content)
    
    print(f"File content: {repr(read_content)}")
    print(f"Parsed: password={repr(password)}, salt={repr(salt)}, ident={repr(ident)}")
    
    assert password == "plainpassword"
    assert salt is None
    assert ident is None
    print("✓ PASSED")
    
    # Test 2: Old format with salt but no ident (e.g., sha256_crypt)
    print("\nTest 2: Password file with salt but no ident")
    old_content_with_salt = "mypassword salt=abcdef1234567890"
    _write_password_file(b_path, old_content_with_salt)
    
    read_content = _read_password_file(b_path)
    password, salt, ident = _parse_content(read_content)
    
    print(f"File content: {repr(read_content)}")
    print(f"Parsed: password={repr(password)}, salt={repr(salt)}, ident={repr(ident)}")
    
    assert password == "mypassword"
    assert salt == "abcdef1234567890"
    assert ident is None
    print("✓ PASSED")
    
    # Test 3: Upgrading old bcrypt file (without explicit ident) to new format
    print("\nTest 3: Upgrading old bcrypt file to new format")
    
    # Create an "old" bcrypt file that only has salt
    old_bcrypt_password = "mybcryptpass"
    old_bcrypt_salt = "abcdefghijklmnopqr1234"  # 22 chars for bcrypt
    old_bcrypt_content = f"{old_bcrypt_password} salt={old_bcrypt_salt}"
    _write_password_file(b_path, old_bcrypt_content)
    
    print(f"Old bcrypt file content: {repr(old_bcrypt_content)}")
    
    # Parse the old content
    read_content = _read_password_file(b_path)
    password, salt, ident = _parse_content(read_content)
    
    print(f"Parsed from old file: password={repr(password)}, salt={repr(salt)}, ident={repr(ident)}")
    assert password == old_bcrypt_password
    assert salt == old_bcrypt_salt
    assert ident is None  # No ident in old file
    
    # Now "upgrade" by adding the default ident for bcrypt
    from ansible.utils.encrypt import BaseHash
    default_ident = BaseHash.algorithms['bcrypt'].implicit_ident
    print(f"Default bcrypt ident: {default_ident}")
    
    # Format with the default ident
    new_content = _format_content(password, salt, encrypt="bcrypt", ident=default_ident)
    _write_password_file(b_path, new_content)
    
    print(f"Upgraded file content: {repr(new_content)}")
    
    # Parse the upgraded content
    read_content_new = _read_password_file(b_path)
    password_new, salt_new, ident_new = _parse_content(read_content_new)
    
    print(f"Parsed from upgraded file: password={repr(password_new)}, salt={repr(salt_new)}, ident={repr(ident_new)}")
    
    # Verify everything is consistent
    assert password_new == old_bcrypt_password
    assert salt_new == old_bcrypt_salt
    assert ident_new == default_ident
    
    # Test encryption works with both old and new parsed values
    try:
        # This should work with the upgraded parsing
        encrypted_new = do_encrypt(password_new, "bcrypt", salt=salt_new, ident=ident_new)
        print(f"✓ Encryption with upgraded parsing succeeded: {encrypted_new}")
    except Exception as e:
        print(f"✗ Encryption with upgraded parsing failed: {e}")
        return False
    
    print("✓ PASSED")
    
    print("\n=== All backward compatibility tests passed! ===")
    
    # Clean up
    try:
        os.remove(password_file)
        os.rmdir(temp_dir)
    except:
        pass
    
    return True

if __name__ == "__main__":
    success = test_backward_compatibility()
    sys.exit(0 if success else 1)
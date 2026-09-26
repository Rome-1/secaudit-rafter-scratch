#!/usr/bin/env python3

import os
import sys
import tempfile

# Add the library path to import Ansible modules
sys.path.insert(0, '/app/lib')

from ansible.plugins.lookup.password import _parse_content, _format_content, _write_password_file, _read_password_file
from ansible.module_utils._text import to_bytes
from ansible.utils.encrypt import do_encrypt, random_salt, BaseHash

def test_password_bcrypt_content():
    """Test the improved _parse_content function"""
    
    # Create a temporary file
    temp_dir = tempfile.mkdtemp()
    password_file = os.path.join(temp_dir, 'password.txt')
    b_path = to_bytes(password_file, errors='surrogate_or_strict')
    
    print(f"Using password file: {password_file}")
    
    # Simulate first run
    password = "test_password123"
    salt = "UYPgwPMJVaBFMU9ext22n/"  # 22-char bcrypt salt
    ident = "2b"
    
    print("=== First run simulation ===")
    content1 = _format_content(password, salt, encrypt="bcrypt", ident=ident)
    print(f"Generated content: {content1}")
    
    # Write to file
    _write_password_file(b_path, content1)
    
    # Read back
    read_content = _read_password_file(b_path)
    print(f"Read content: {read_content}")
    
    # Parse content with new function that returns 3 values
    parsed_password, parsed_salt, parsed_ident = _parse_content(read_content)
    print(f"Parsed password: {parsed_password}")
    print(f"Parsed salt: {parsed_salt}")
    print(f"Parsed ident: {parsed_ident}")
    
    print("\n=== Second run simulation ===")
    # Now the second run should work correctly with proper parsing
    
    content2 = _format_content(parsed_password, parsed_salt, encrypt="bcrypt", ident=parsed_ident)
    print(f"Generated content on second run: {content2}")
    
    # Write to file again
    _write_password_file(b_path, content2)
    
    # Read back again
    read_content2 = _read_password_file(b_path)
    print(f"Read content after second write: {read_content2}")
    
    # Try to encrypt - this should now work with proper salt
    print(f"Trying to encrypt with parsed salt: '{parsed_salt}' and ident: '{parsed_ident}'")
    try:
        encrypted = do_encrypt(parsed_password, "bcrypt", salt=parsed_salt, ident=parsed_ident)
        print(f"Encryption successful: {encrypted}")
    except Exception as e:
        print(f"Encryption failed: {e}")
    
    # Clean up
    try:
        os.remove(password_file)
        os.rmdir(temp_dir)
    except:
        pass

if __name__ == "__main__":
    test_password_bcrypt_content()
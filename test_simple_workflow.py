#!/usr/bin/env python3

import os
import sys
import tempfile

# Add the library path to import Ansible modules
sys.path.insert(0, '/app/lib')

from ansible.plugins.lookup.password import (_parse_content, _format_content, _write_password_file, 
                                             _read_password_file, _gen_candidate_chars,
                                             VALID_PARAMS)
from ansible.module_utils._text import to_bytes
from ansible.utils.encrypt import do_encrypt, random_salt, BaseHash, random_password
from ansible.parsing.splitter import parse_kv
from ansible.errors import AnsibleError

def simulate_password_lookup_run(password_file_path, term_params):
    """Simulate the core logic of the password lookup plugin"""
    
    # Parse parameters like the real plugin does
    relpath = password_file_path
    
    # Parse kv parameters from term
    params = {}
    try:
        kv = parse_kv(term_params)
        for key, value in kv.items():
            if key not in VALID_PARAMS:
                raise AnsibleError(f"Invalid parameter: {key}")
            params[key] = value
    except ValueError as e:
        raise AnsibleError(f"Could not parse parameters: {e}")
    
    # Set defaults
    params.setdefault('length', 20)
    params.setdefault('chars', ['ascii_letters', 'digits', ".,:-_"])
    params.setdefault('encrypt', None)
    params.setdefault('ident', None) 
    params.setdefault('seed', None)
    
    # Convert string values to appropriate types
    if 'length' in params:
        params['length'] = int(params['length'])
    
    b_path = to_bytes(password_file_path, errors='surrogate_or_strict')
    chars = _gen_candidate_chars(params['chars'])
    
    changed = None
    content = _read_password_file(b_path)

    if content is None or b_path == to_bytes('/dev/null'):
        plaintext_password = random_password(params['length'], chars, params['seed'])
        salt = None
        file_ident = None
        changed = True
    else:
        plaintext_password, salt, file_ident = _parse_content(content)

    encrypt = params['encrypt']
    if encrypt and not salt:
        changed = True
        try:
            salt = random_salt(BaseHash.algorithms[encrypt].salt_size)
        except KeyError:
            salt = random_salt()

    # Handle ident: check parameter vs file ident, ensure consistency
    param_ident = params['ident']
    ident = None
    
    # If ident is provided as parameter, ensure it matches file ident (if exists)
    if param_ident:
        if file_ident and param_ident != file_ident:
            raise AnsibleError(f"ident parameter '{param_ident}' does not match ident in password file '{file_ident}'")
        ident = param_ident
    elif file_ident:
        # Use ident from file if no parameter provided
        ident = file_ident
    elif encrypt:
        # If no ident from parameter or file, and we're encrypting, get default for algorithm
        try:
            ident = BaseHash.algorithms[encrypt].implicit_ident
        except KeyError:
            ident = None
        if ident:
            changed = True

    if changed and b_path != to_bytes('/dev/null'):
        content = _format_content(plaintext_password, salt, encrypt=encrypt, ident=ident)
        _write_password_file(b_path, content)

    if encrypt:
        password = do_encrypt(plaintext_password, encrypt, salt=salt, ident=ident)
        return password
    else:
        return plaintext_password

def test_password_workflow():
    """Test the password lookup workflow with our fixes"""
    
    # Create a temporary file
    temp_dir = tempfile.mkdtemp()
    password_file = os.path.join(temp_dir, 'password.txt')
    
    print(f"Using password file: {password_file}")
    
    # First run - should create the file with bcrypt encryption
    print("=== First run (creating password file) ===")
    try:
        result1 = simulate_password_lookup_run(password_file, "encrypt=bcrypt")
        print(f"Success! Generated encrypted password: {result1}")
        
        # Check file content
        with open(password_file, 'r') as f:
            content = f.read()
        print(f"File content: {repr(content)}")
        
    except Exception as e:
        print(f"First run failed: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    # Second run - should reuse the existing file without duplicating ident
    print("\n=== Second run (reusing password file) ===")
    try:
        result2 = simulate_password_lookup_run(password_file, "encrypt=bcrypt")
        print(f"Success! Reused encrypted password: {result2}")
        
        # Check file content after second run
        with open(password_file, 'r') as f:
            content_after = f.read()
        print(f"File content after second run: {repr(content_after)}")
        
        # Verify that the content didn't get duplicated
        if content == content_after:
            print("✓ File content is stable between runs")
        else:
            print("✗ File content changed between runs - this indicates a problem")
            return False
            
        # Verify both results are identical
        if result1 == result2:
            print("✓ Both runs produced the same encrypted password")
        else:
            print("✗ Different passwords generated between runs")
            return False
        
    except Exception as e:
        print(f"Second run failed: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    # Third run with explicit ident parameter - should match file ident
    print("\n=== Third run (with explicit ident parameter) ===")
    try:
        result3 = simulate_password_lookup_run(password_file, "encrypt=bcrypt ident=2b")
        print(f"Success! Password with explicit ident: {result3}")
        
        if result1 == result3:
            print("✓ Explicit ident parameter produces same result")
        else:
            print("✗ Explicit ident parameter produces different result")
            return False
        
    except Exception as e:
        print(f"Third run failed: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    # Fourth run with conflicting ident parameter - should fail
    print("\n=== Fourth run (with conflicting ident parameter) ===")
    try:
        result4 = simulate_password_lookup_run(password_file, "encrypt=bcrypt ident=2a")
        print(f"✗ This should have failed but didn't: {result4}")
        return False
        
    except AnsibleError as e:
        expected_error = "does not match ident in password file"
        if expected_error in str(e):
            print(f"✓ Correctly failed with conflicting ident: {e}")
        else:
            print(f"✗ Failed with unexpected error: {e}")
            return False
    except Exception as e:
        print(f"✗ Failed with unexpected exception type: {e}")
        return False
    
    print("\n=== All tests passed! ===")
    
    # Clean up
    try:
        os.remove(password_file)
        os.rmdir(temp_dir)
    except:
        pass
        
    return True

if __name__ == "__main__":
    success = test_password_workflow()
    sys.exit(0 if success else 1)
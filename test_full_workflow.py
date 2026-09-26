#!/usr/bin/env python3

import os
import sys
import tempfile

# Add the library path to import Ansible modules
sys.path.insert(0, '/app/lib')

from ansible.plugins.lookup.password import LookupModule
from ansible.parsing.dataloader import DataLoader
from ansible.inventory.manager import InventoryManager
from ansible.vars.manager import VariableManager

def test_password_lookup_full():
    """Test the full password lookup plugin workflow"""
    
    # Create a temporary file
    temp_dir = tempfile.mkdtemp()
    password_file = os.path.join(temp_dir, 'password.txt')
    
    print(f"Using password file: {password_file}")
    
    # Create minimal context - not needed for this test
    
    # Set up minimal Ansible context
    loader = DataLoader()
    inventory = InventoryManager(loader=loader, sources=['localhost,'])
    variable_manager = VariableManager(loader=loader, inventory=inventory)
    
    # Create password lookup plugin instance
    lookup = LookupModule(loader=loader)
    
    # First run - should create the file with bcrypt encryption
    print("=== First run (creating password file) ===")
    try:
        terms = [f'{password_file} encrypt=bcrypt']
        variables = variable_manager.get_vars()
        result1 = lookup.run(terms, variables)
        print(f"Success! Generated encrypted password: {result1[0]}")
        
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
        result2 = lookup.run(terms, variables)
        print(f"Success! Reused encrypted password: {result2[0]}")
        
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
        if result1[0] == result2[0]:
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
        terms_with_ident = [f'{password_file} encrypt=bcrypt ident=2b']
        result3 = lookup.run(terms_with_ident, variables)
        print(f"Success! Password with explicit ident: {result3[0]}")
        
        if result1[0] == result3[0]:
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
        terms_conflicting = [f'{password_file} encrypt=bcrypt ident=2a']
        result4 = lookup.run(terms_conflicting, variables)
        print(f"✗ This should have failed but didn't: {result4[0]}")
        return False
        
    except Exception as e:
        expected_error = "does not match ident in password file"
        if expected_error in str(e):
            print(f"✓ Correctly failed with conflicting ident: {e}")
        else:
            print(f"✗ Failed with unexpected error: {e}")
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
    success = test_password_lookup_full()
    sys.exit(0 if success else 1)
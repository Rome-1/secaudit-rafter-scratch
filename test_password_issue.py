#!/usr/bin/env python

"""
Test script to reproduce the password lookup plugin issue.
"""

import os
import sys
import tempfile
sys.path.insert(0, '/app/lib')

from ansible.plugins.lookup.password import LookupModule
from ansible.parsing.dataloader import DataLoader
from ansible.inventory.manager import InventoryManager
from ansible.vars.manager import VariableManager

def test_password_deterministic():
    # Create a lookup module instance
    lookup = LookupModule()
    
    # Create minimal Ansible infrastructure
    loader = DataLoader()
    inventory = InventoryManager(loader=loader, sources=['localhost,'])
    variable_manager = VariableManager(loader=loader, inventory=inventory)
    
    # Set the loader on the lookup module and mock required attributes
    lookup._loader = loader
    lookup._load_name = 'password'
    
    print("Testing password lookup with seed parameter...")
    
    # Test with seed parameter - should generate deterministic passwords
    terms = ['/dev/null seed=myseed']
    variables = {}
    
    # Call the lookup plugin multiple times with the same seed
    result1 = lookup.run(terms, variables)
    result2 = lookup.run(terms, variables)
    result3 = lookup.run(terms, variables)
    
    print(f"First run:  {result1[0]}")
    print(f"Second run: {result2[0]}")
    print(f"Third run:  {result3[0]}")
    
    # Check if results are deterministic
    if result1[0] == result2[0] == result3[0]:
        print("✓ PASS: Passwords are deterministic with same seed")
        return True
    else:
        print("✗ FAIL: Passwords are not deterministic with same seed")
        return False

def test_password_different_seeds():
    # Create a lookup module instance
    lookup = LookupModule()
    
    # Create minimal Ansible infrastructure
    loader = DataLoader()
    inventory = InventoryManager(loader=loader, sources=['localhost,'])
    variable_manager = VariableManager(loader=loader, inventory=inventory)
    
    # Set the loader on the lookup module and mock required attributes
    lookup._loader = loader
    lookup._load_name = 'password'
    
    print("\nTesting password lookup with different seeds...")
    
    # Test with different seeds - should generate different passwords
    terms1 = ['/dev/null seed=seed1']
    terms2 = ['/dev/null seed=seed2']
    variables = {}
    
    result1 = lookup.run(terms1, variables)
    result2 = lookup.run(terms2, variables)
    
    print(f"Seed1 result: {result1[0]}")
    print(f"Seed2 result: {result2[0]}")
    
    if result1[0] != result2[0]:
        print("✓ PASS: Different seeds generate different passwords")
        return True
    else:
        print("✗ FAIL: Different seeds generate same password")
        return False

if __name__ == '__main__':
    success1 = test_password_deterministic()
    success2 = test_password_different_seeds()
    
    if not (success1 and success2):
        sys.exit(1)
    else:
        print("\n✓ All tests passed!")
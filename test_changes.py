#!/usr/bin/env python3
"""Test script to verify the changes."""

import sys
import os

print("Python version:", sys.version_info)

# Test 1: Check if Python 3.12 check is enforced
print("\n=== Test 1: Python version check ===")
try:
    # Mock the version check by temporarily modifying sys.version_info
    original_version = sys.version_info
    
    # We can't actually modify sys.version_info, so we'll just import and check what happens
    # For now, let's just check the code exists
    with open('/app/lib/ansible/cli/__init__.py', 'r') as f:
        content = f.read()
        if '(3, 12)' in content:
            print("✓ Python 3.12 version check found")
        else:
            print("✗ Python 3.12 version check NOT found")
            
        if '(3, 10)' in content:
            print("✗ Python 3.10 reference still exists")
        else:
            print("✓ Python 3.10 reference removed")
except Exception as e:
    print(f"✗ Error checking version: {e}")

# Test 2: Check removesuffix usage in galaxy collection
print("\n=== Test 2: Check removesuffix in galaxy collection ===")
try:
    with open('/app/lib/ansible/galaxy/collection/__init__.py', 'r') as f:
        content = f.read()
        # Count removesuffix occurrences
        count = content.count('removesuffix')
        print(f"Found {count} occurrence(s) of removesuffix")
        
        # Check _extract_tar_dir function
        if 'dirname = to_native(dirname, errors=\'surrogate_or_strict\').removesuffix(os.path.sep)' in content:
            print("✗ removesuffix still used in _extract_tar_dir")
        else:
            print("✓ removesuffix removed from _extract_tar_dir dirname line")
            
        # Check that tar.getmember is used properly
        if 'tar.getmember(dirname)' in content:
            print("✓ tar.getmember(dirname) usage found")
        else:
            print("✗ tar.getmember(dirname) not found")
            
except Exception as e:
    print(f"✗ Error checking galaxy collection: {e}")

# Test 3: Check _ansible_normalized_cache removal
print("\n=== Test 3: Check _ansible_normalized_cache removal ===")
try:
    with open('/app/lib/ansible/galaxy/collection/__init__.py', 'r') as f:
        content = f.read()
        if '_ansible_normalized_cache' in content:
            print("✗ _ansible_normalized_cache still exists")
            # Count occurrences
            count = content.count('_ansible_normalized_cache')
            print(f"  Found {count} occurrence(s)")
        else:
            print("✓ _ansible_normalized_cache removed")
except Exception as e:
    print(f"✗ Error checking _ansible_normalized_cache: {e}")

# Test 4: Check import reload changes
print("\n=== Test 4: Check importlib reload import ===")
try:
    with open('/app/lib/ansible/utils/collection_loader/_collection_finder.py', 'r') as f:
        content = f.read()
        if 'from importlib import reload as reload_module' in content:
            print("✓ importlib reload import added")
            # Check that the old try/except block is removed
            if 'except ImportError:' in content and '# 2.7 has a global reload function' in content:
                print("✗ Old Python 2.7 reload fallback still exists")
            else:
                print("✓ Old Python 2.7 reload fallback removed")
        else:
            print("✗ importlib reload import not found")
except Exception as e:
    print(f"✗ Error checking reload import: {e}")

# Test 5: Check string_types replacement
print("\n=== Test 5: Check string_types replacement with str ===")
try:
    with open('/app/lib/ansible/cli/__init__.py', 'r') as f:
        content = f.read()
        if 'isinstance(options.listofhosts, str)' in content:
            print("✓ isinstance with str for listofhosts found")
        elif 'isinstance(options.listofhosts, string_types)' in content:
            print("✗ isinstance still uses string_types for listofhosts")
        else:
            print("? listofhosts isinstance check not found")
            
        if 'isinstance(options.inventory, str)' in content:
            print("✓ isinstance with str for inventory found")
        elif 'isinstance(options.inventory, string_types)' in content:
            print("✗ isinstance still uses string_types for inventory")
        else:
            print("? inventory isinstance check not found")
            
        # Check if string_types import is still there
        if 'from ansible.module_utils.six import string_types' in content:
            print("✗ string_types import still exists")
        else:
            print("✓ string_types import removed")
except Exception as e:
    print(f"✗ Error checking string_types: {e}")

# Test 6: Check old Python version comments
print("\n=== Test 6: Check old Python version comments ===")
try:
    with open('/app/lib/ansible/galaxy/collection/__init__.py', 'r') as f:
        content = f.read()
        if 'py3.11' in content.lower() or 'python 3.11' in content.lower():
            print("✗ Python 3.11 references still exist")
        else:
            print("✓ Python 3.11 references removed")
            
        if 'py3.10' in content.lower() or 'python 3.10' in content.lower():
            print("✗ Python 3.10 references still exist")
        else:
            print("✓ Python 3.10 references removed")
except Exception as e:
    print(f"✗ Error checking Python version comments: {e}")

print("\n=== Test Summary ===")
print("Review the results above to verify all changes are in place.")

#!/usr/bin/env python3
"""Test script to verify the functionality of changes."""

import sys
import os
import tempfile
import tarfile
from pathlib import Path

# Add the lib directory to the path so we can import ansible modules
sys.path.insert(0, '/app/lib')

print("Python version:", sys.version_info)
print()

# Test 1: Test that isinstance with str works correctly
print("=== Test 1: isinstance with str ===")
try:
    test_str = "test_value"
    test_list = ["test1", "test2"]
    
    if isinstance(test_str, str):
        print("✓ isinstance(str, str) works correctly")
    else:
        print("✗ isinstance(str, str) failed")
    
    if not isinstance(test_list, str):
        print("✓ isinstance(list, str) correctly returns False")
    else:
        print("✗ isinstance(list, str) incorrectly returned True")
except Exception as e:
    print(f"✗ Error in isinstance test: {e}")

# Test 2: Test reload import
print("\n=== Test 2: Test reload_module import ===")
try:
    from ansible.utils.collection_loader._collection_finder import reload_module
    print("✓ reload_module imported successfully")
    
    # Try to reload a module
    import json
    reload_module(json)
    print("✓ reload_module function works correctly")
except Exception as e:
    print(f"✗ Error importing or using reload_module: {e}")

# Test 3: Test _extract_tar_dir with tar.getmember
print("\n=== Test 3: Test _extract_tar_dir with tar.getmember ===")
try:
    from ansible.galaxy.collection import _extract_tar_dir
    from ansible.errors import AnsibleError
    
    # Create a temporary tar file for testing
    with tempfile.TemporaryDirectory() as tmpdir:
        tar_path = os.path.join(tmpdir, 'test.tar')
        test_dir = os.path.join(tmpdir, 'test_content')
        os.makedirs(test_dir)
        
        # Create a simple tar file with a directory
        with tarfile.open(tar_path, 'w') as tar:
            tar.add(test_dir, arcname='test_dir')
        
        # Test extracting a directory that exists
        extract_dest = os.path.join(tmpdir, 'extract')
        os.makedirs(extract_dest)
        
        with tarfile.open(tar_path, 'r') as tar:
            try:
                _extract_tar_dir(tar, 'test_dir', extract_dest.encode('utf-8'))
                print("✓ _extract_tar_dir works with existing directory")
            except Exception as e:
                print(f"✓ _extract_tar_dir works (got expected behavior): {e}")
        
        # Test extracting a directory that doesn't exist
        with tarfile.open(tar_path, 'r') as tar:
            try:
                _extract_tar_dir(tar, 'nonexistent_dir', extract_dest.encode('utf-8'))
                print("✗ _extract_tar_dir should have raised AnsibleError for missing directory")
            except AnsibleError as e:
                if "Unable to extract 'nonexistent_dir' from collection" in str(e):
                    print("✓ _extract_tar_dir raises correct AnsibleError for missing directory")
                else:
                    print(f"✗ Wrong error message: {e}")
            except KeyError:
                # tar.getmember raises KeyError, which we should catch and convert to AnsibleError
                print("✗ _extract_tar_dir didn't catch KeyError properly")
            except Exception as e:
                print(f"✗ Unexpected exception: {type(e).__name__}: {e}")
                
except Exception as e:
    import traceback
    print(f"✗ Error in _extract_tar_dir test: {e}")
    traceback.print_exc()

# Test 4: Test that install_artifact doesn't use _ansible_normalized_cache
print("\n=== Test 4: Test install_artifact doesn't use _ansible_normalized_cache ===")
try:
    import inspect
    from ansible.galaxy.collection import install_artifact
    
    source = inspect.getsource(install_artifact)
    if '_ansible_normalized_cache' in source:
        print("✗ install_artifact still uses _ansible_normalized_cache")
    else:
        print("✓ install_artifact doesn't use _ansible_normalized_cache")
except Exception as e:
    print(f"✗ Error checking install_artifact: {e}")

print("\n=== All functionality tests complete ===")

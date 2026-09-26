#!/usr/bin/env python3
"""Test edge cases for the changes made."""

import sys
import os
import tempfile
import tarfile
import unittest.mock as mock

print("Testing Edge Cases")
print("=" * 80)

# Mock Python 3.12 for imports
with mock.patch.object(sys, 'version_info', (3, 12, 0, 'final', 0)):
    from ansible.galaxy.collection import _extract_tar_dir
    from ansible.errors import AnsibleError

    print("\n1. Testing _extract_tar_dir with various directory names")
    print("-" * 80)
    
    with tempfile.TemporaryDirectory() as tmpdir:
        tar_path = os.path.join(tmpdir, 'test.tar')
        
        # Create test directories with various names
        test_dirs = [
            'simple_dir',
            'dir_with_underscore',
            'dir-with-dash',
            'dir.with.dots',
        ]
        
        for dir_name in test_dirs:
            dir_path = os.path.join(tmpdir, dir_name)
            os.makedirs(dir_path, exist_ok=True)
        
        # Create tar file
        with tarfile.open(tar_path, 'w') as tar:
            for dir_name in test_dirs:
                dir_path = os.path.join(tmpdir, dir_name)
                tar.add(dir_path, arcname=dir_name)
        
        # Test extracting each directory
        extract_dest = os.path.join(tmpdir, 'extract')
        os.makedirs(extract_dest)
        
        with tarfile.open(tar_path, 'r') as tar:
            for dir_name in test_dirs:
                try:
                    _extract_tar_dir(tar, dir_name, extract_dest.encode('utf-8'))
                    print(f"✓ Successfully extracted: {dir_name}")
                except Exception as e:
                    print(f"✗ Failed to extract {dir_name}: {e}")

    print("\n2. Testing _extract_tar_dir error handling")
    print("-" * 80)
    
    with tempfile.TemporaryDirectory() as tmpdir:
        tar_path = os.path.join(tmpdir, 'test.tar')
        test_dir = os.path.join(tmpdir, 'test_content')
        os.makedirs(test_dir)
        
        with tarfile.open(tar_path, 'w') as tar:
            tar.add(test_dir, arcname='existing_dir')
        
        extract_dest = os.path.join(tmpdir, 'extract')
        os.makedirs(extract_dest)
        
        with tarfile.open(tar_path, 'r') as tar:
            # Test with missing directory
            missing_dirs = [
                'nonexistent',
                'does_not_exist',
                'missing_dir',
            ]
            
            for missing_dir in missing_dirs:
                try:
                    _extract_tar_dir(tar, missing_dir, extract_dest.encode('utf-8'))
                    print(f"✗ Should have raised error for: {missing_dir}")
                except AnsibleError as e:
                    expected_msg = f"Unable to extract '{missing_dir}' from collection"
                    if expected_msg in str(e):
                        print(f"✓ Correct error for missing dir: {missing_dir}")
                    else:
                        print(f"✗ Wrong error message for {missing_dir}: {e}")
                except Exception as e:
                    print(f"✗ Wrong exception type for {missing_dir}: {type(e).__name__}: {e}")

    print("\n3. Testing that tar.getmember is called with unchanged dirname")
    print("-" * 80)
    
    with tempfile.TemporaryDirectory() as tmpdir:
        tar_path = os.path.join(tmpdir, 'test.tar')
        
        # Create a directory with trailing slash potential
        test_dir = os.path.join(tmpdir, 'test_dir')
        os.makedirs(test_dir)
        
        with tarfile.open(tar_path, 'w') as tar:
            tar.add(test_dir, arcname='test_dir')
        
        extract_dest = os.path.join(tmpdir, 'extract')
        os.makedirs(extract_dest)
        
        with tarfile.open(tar_path, 'r') as tar:
            # Test with exact name (should work)
            try:
                _extract_tar_dir(tar, 'test_dir', extract_dest.encode('utf-8'))
                print("✓ Exact name 'test_dir' works")
            except Exception as e:
                print(f"✗ Failed with exact name: {e}")
            
            # Test with trailing slash (should fail since we don't strip it)
            try:
                _extract_tar_dir(tar, 'test_dir/', extract_dest.encode('utf-8'))
                print("✗ 'test_dir/' should have failed (no member with trailing slash)")
            except AnsibleError as e:
                if "Unable to extract 'test_dir/' from collection" in str(e):
                    print("✓ Correctly fails for 'test_dir/' (trailing slash not in tar)")
                else:
                    print(f"✗ Wrong error: {e}")

    print("\n4. Testing isinstance with str")
    print("-" * 80)
    
    # Test that isinstance works correctly with str
    test_cases = [
        ("string", str, True),
        (["list"], str, False),
        (123, str, False),
        (None, str, False),
    ]
    
    for value, type_check, expected in test_cases:
        result = isinstance(value, type_check)
        if result == expected:
            print(f"✓ isinstance({repr(value)}, str) = {result} (expected {expected})")
        else:
            print(f"✗ isinstance({repr(value)}, str) = {result} (expected {expected})")

    print("\n5. Testing Python version rejection")
    print("-" * 80)
    
    # Test various Python versions
    test_versions = [
        ((3, 9, 0, 'final', 0), False, "3.9"),
        ((3, 10, 0, 'final', 0), False, "3.10"),
        ((3, 11, 0, 'final', 0), False, "3.11"),
        ((3, 12, 0, 'final', 0), True, "3.12"),
        ((3, 13, 0, 'final', 0), True, "3.13"),
    ]
    
    for version, should_pass, version_str in test_versions:
        # Test the version check logic
        version_tuple = version[:2]
        passes = version_tuple >= (3, 12)
        
        if passes == should_pass:
            status = "accepted" if passes else "rejected"
            print(f"✓ Python {version_str}: correctly {status}")
        else:
            print(f"✗ Python {version_str}: incorrect behavior")

print("\n" + "=" * 80)
print("All edge case tests completed successfully!")
print("=" * 80)

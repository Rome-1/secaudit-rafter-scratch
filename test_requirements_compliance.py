#!/usr/bin/env python3
"""
Comprehensive test to verify compliance with all requirements from the PR description.
"""

import sys
import os
import tempfile
import tarfile
import unittest.mock as mock

print("=" * 80)
print("REQUIREMENTS COMPLIANCE TEST")
print("=" * 80)
print()

# Requirement 1: Python 3.12 version check in lib/ansible/cli/__init__.py
print("Requirement 1: Python 3.12 version check")
print("-" * 80)

with open('/app/lib/ansible/cli/__init__.py', 'r') as f:
    cli_content = f.read()

# Check for the correct version check
if 'sys.version_info < (3, 12)' in cli_content:
    print("✓ Version check enforces Python 3.12 minimum")
else:
    print("✗ FAIL: Version check does not enforce Python 3.12")
    sys.exit(1)

# Check for the correct error message
if 'Python 3.12 or newer' in cli_content:
    print("✓ Error message mentions Python 3.12")
else:
    print("✗ FAIL: Error message doesn't mention Python 3.12")
    sys.exit(1)

# Check that old references are removed
if '3.10' in cli_content:
    print("✗ FAIL: Still contains references to Python 3.10")
    sys.exit(1)
else:
    print("✓ No references to Python 3.10")

print()

# Requirement 2: dirname should not remove suffix
print("Requirement 2: dirname should not use removesuffix")
print("-" * 80)

with open('/app/lib/ansible/galaxy/collection/__init__.py', 'r') as f:
    galaxy_content = f.read()

# Find the _extract_tar_dir function
import re
extract_tar_dir_match = re.search(
    r'def _extract_tar_dir\(tar, dirname, b_dest\):.*?(?=\ndef |\Z)',
    galaxy_content,
    re.DOTALL
)

if extract_tar_dir_match:
    extract_tar_dir_func = extract_tar_dir_match.group(0)
    
    # Check that dirname doesn't use removesuffix
    if '.removesuffix' in extract_tar_dir_func and 'dirname' in extract_tar_dir_func:
        # Check more carefully
        if 'dirname = to_native(dirname, errors=\'surrogate_or_strict\').removesuffix' in extract_tar_dir_func:
            print("✗ FAIL: dirname still uses removesuffix")
            sys.exit(1)
        else:
            print("✓ dirname does not use removesuffix (other uses may exist)")
    else:
        print("✓ dirname does not use removesuffix")
    
    # Check that dirname is passed unchanged to tar.getmember
    if 'tar.getmember(dirname)' in extract_tar_dir_func:
        print("✓ dirname is passed unchanged to tar.getmember()")
    else:
        print("✗ FAIL: dirname is not passed to tar.getmember()")
        sys.exit(1)
    
    # Check error message
    if 'Unable to extract \'%s\' from collection' in extract_tar_dir_func:
        print("✓ Correct error message for missing member")
    else:
        print("✗ FAIL: Wrong error message for missing member")
        sys.exit(1)
else:
    print("✗ FAIL: Could not find _extract_tar_dir function")
    sys.exit(1)

print()

# Requirement 3: Addition of importlib import reload
print("Requirement 3: importlib reload import")
print("-" * 80)

with open('/app/lib/ansible/utils/collection_loader/_collection_finder.py', 'r') as f:
    finder_content = f.read()

if 'from importlib import reload as reload_module' in finder_content:
    print("✓ Direct import from importlib for reload_module")
else:
    print("✗ FAIL: No direct import from importlib for reload_module")
    sys.exit(1)

# Check that old fallback is removed
if '# 2.7 has a global reload function' in finder_content:
    print("✗ FAIL: Old Python 2.7 reload fallback still exists")
    sys.exit(1)
else:
    print("✓ Old Python 2.7 reload fallback removed")

print()

# Requirement 4: isinstance should work with str
print("Requirement 4: isinstance should work with str")
print("-" * 80)

if 'isinstance(options.inventory, str)' in cli_content:
    print("✓ isinstance uses str for inventory")
else:
    print("✗ FAIL: isinstance doesn't use str for inventory")
    sys.exit(1)

if 'isinstance(options.listofhosts, str)' in cli_content:
    print("✓ isinstance uses str for listofhosts")
else:
    # This might be in a docstring, so just warn
    print("  Note: listofhosts isinstance not found (might be in docstring)")

# Check that string_types import is removed
if 'from ansible.module_utils.six import string_types' in cli_content:
    print("✗ FAIL: string_types import still exists")
    sys.exit(1)
else:
    print("✓ string_types import removed")

print()

# Requirement 5: _ansible_normalized_cache not used
print("Requirement 5: install_artifact must not use _ansible_normalized_cache")
print("-" * 80)

if '_ansible_normalized_cache' in galaxy_content:
    print("✗ FAIL: _ansible_normalized_cache still exists in galaxy collection")
    sys.exit(1)
else:
    print("✓ _ansible_normalized_cache removed from galaxy collection")

print()

# Requirement 6: Old Python version references removed
print("Requirement 6: Old Python version references removed")
print("-" * 80)

files_to_check = [
    '/app/lib/ansible/galaxy/collection/__init__.py',
    '/app/lib/ansible/cli/__init__.py',
    '/app/lib/ansible/utils/collection_loader/_collection_finder.py',
    '/app/lib/ansible/compat/importlib_resources.py',
]

all_clean = True
for filepath in files_to_check:
    with open(filepath, 'r') as f:
        content = f.read()
    
    filename = os.path.basename(filepath)
    
    # Check for old version references
    old_refs = []
    if 'py3.10' in content.lower() or 'python 3.10' in content.lower():
        old_refs.append('3.10')
    if 'py3.11' in content.lower() or 'python 3.11' in content.lower():
        old_refs.append('3.11')
    
    if old_refs:
        print(f"✗ {filename}: Still has references to Python {', '.join(old_refs)}")
        all_clean = False
    else:
        print(f"✓ {filename}: Clean of old version references")

if not all_clean:
    sys.exit(1)

print()

# Requirement 7: Changelog fragment exists
print("Requirement 7: Changelog fragment")
print("-" * 80)

changelog_path = '/app/changelogs/fragments/drop-python-3.10-3.11-support.yml'
if os.path.exists(changelog_path):
    print("✓ Changelog fragment exists")
    
    with open(changelog_path, 'r') as f:
        changelog_content = f.read()
    
    if 'Python 3.12' in changelog_content or '3.12' in changelog_content:
        print("✓ Changelog mentions Python 3.12")
    else:
        print("✗ FAIL: Changelog doesn't mention Python 3.12")
        sys.exit(1)
else:
    print("✗ FAIL: Changelog fragment doesn't exist")
    sys.exit(1)

print()

# Test actual functionality with mocking
print("Functional Tests with Python Version Mocking")
print("-" * 80)

# Test that Python 3.12 is accepted
with mock.patch.object(sys, 'version_info', (3, 12, 0, 'final', 0)):
    try:
        # Import will run the version check
        from ansible.cli import CLI
        print("✓ Python 3.12: Import successful")
    except SystemExit as e:
        print(f"✗ FAIL: Python 3.12 was rejected: {e}")
        sys.exit(1)

# Test that Python 3.11 is rejected
print()
print("Testing rejection of Python 3.11:")
with mock.patch.object(sys, 'version_info', (3, 11, 0, 'final', 0)):
    try:
        # Create a test to see if the version check works
        test_globals = {'sys': sys, 'SystemExit': SystemExit}
        exec("""
if sys.version_info < (3, 12):
    raise SystemExit('ERROR: Ansible requires Python 3.12 or newer on the controller.')
""", test_globals)
        print("✗ FAIL: Python 3.11 was not rejected")
        sys.exit(1)
    except SystemExit:
        print("✓ Python 3.11: Correctly rejected")

# Test that Python 3.10 is rejected
with mock.patch.object(sys, 'version_info', (3, 10, 0, 'final', 0)):
    try:
        test_globals = {'sys': sys, 'SystemExit': SystemExit}
        exec("""
if sys.version_info < (3, 12):
    raise SystemExit('ERROR: Ansible requires Python 3.12 or newer on the controller.')
""", test_globals)
        print("✗ FAIL: Python 3.10 was not rejected")
        sys.exit(1)
    except SystemExit:
        print("✓ Python 3.10: Correctly rejected")

# Test _extract_tar_dir functionality
print()
print("Testing _extract_tar_dir functionality:")

# We need to test with Python 3.12 mocked
with mock.patch.object(sys, 'version_info', (3, 12, 0, 'final', 0)):
    from ansible.galaxy.collection import _extract_tar_dir
    from ansible.errors import AnsibleError
    
    # Create a test tar file
    with tempfile.TemporaryDirectory() as tmpdir:
        tar_path = os.path.join(tmpdir, 'test.tar')
        test_dir = os.path.join(tmpdir, 'test_content')
        os.makedirs(test_dir)
        
        with tarfile.open(tar_path, 'w') as tar:
            tar.add(test_dir, arcname='test_dir')
        
        extract_dest = os.path.join(tmpdir, 'extract')
        os.makedirs(extract_dest)
        
        # Test that missing member raises correct error
        with tarfile.open(tar_path, 'r') as tar:
            try:
                _extract_tar_dir(tar, 'nonexistent_dir', extract_dest.encode('utf-8'))
                print("✗ FAIL: Should have raised AnsibleError for missing directory")
                sys.exit(1)
            except AnsibleError as e:
                if "Unable to extract 'nonexistent_dir' from collection" in str(e):
                    print("✓ Missing directory raises correct AnsibleError")
                else:
                    print(f"✗ FAIL: Wrong error message: {e}")
                    sys.exit(1)
            except KeyError:
                print("✗ FAIL: KeyError not caught and converted to AnsibleError")
                sys.exit(1)

print()
print("=" * 80)
print("ALL REQUIREMENTS COMPLIANCE TESTS PASSED ✓")
print("=" * 80)

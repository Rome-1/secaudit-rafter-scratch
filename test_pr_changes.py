#!/usr/bin/env python
"""Test script to verify the PR changes are working correctly."""

import sys
import os
import subprocess
import tempfile
import tarfile
import hashlib
import pathlib

def test_python_version_check():
    """Test 1: Verify Python version check in cli/__init__.py"""
    print("Test 1: Python version check")
    print("Current Python version:", sys.version_info)
    
    # Create a test script that imports the CLI module
    test_script = """
import sys
# Test with Python 3.10
sys.version_info = (3, 10, 0, 'final', 0)
try:
    import ansible.cli
    print("FAILED: Should have raised SystemExit for Python 3.10")
except SystemExit as e:
    if str(e).startswith("ERROR: Ansible requires Python 3.11 or newer on the controller. Current version:"):
        print("PASSED: Correct error message for Python 3.10")
    else:
        print(f"FAILED: Wrong error message: {e}")

# Test with Python 3.11  
sys.version_info = (3, 11, 0, 'final', 0)
try:
    # Clear the module cache to re-import
    if 'ansible.cli' in sys.modules:
        del sys.modules['ansible.cli']
    import ansible.cli
    print("PASSED: Python 3.11 is accepted")
except SystemExit as e:
    print(f"FAILED: Should not raise SystemExit for Python 3.11: {e}")
"""
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
        f.write(test_script)
        f.flush()
        result = subprocess.run([sys.executable, f.name], capture_output=True, text=True, cwd='/app')
        print(result.stdout)
        if result.stderr:
            print("stderr:", result.stderr)
        os.unlink(f.name)

def test_collection_extract():
    """Test 2: Verify _extract_tar_dir changes"""
    print("\nTest 2: _extract_tar_dir function")
    
    test_script = """
import sys
import os
import tempfile
import tarfile
sys.path.insert(0, '/app/lib')
from ansible.galaxy.collection import _extract_tar_dir
from ansible.errors import AnsibleError

# Create a test tarfile
with tempfile.NamedTemporaryFile(suffix='.tar', delete=False) as f:
    tar_path = f.name

with tarfile.open(tar_path, 'w') as tar:
    # Add a test directory
    info = tarfile.TarInfo('test_dir/')
    info.type = tarfile.DIRTYPE
    tar.addfile(info)

# Test the extraction function
with tempfile.TemporaryDirectory() as dest:
    with tarfile.open(tar_path, 'r') as tar:
        try:
            # Should call tar.getmember directly with dirname and raise AnsibleError with specific message
            _extract_tar_dir(tar, 'nonexistent_dir', dest)
            print("FAILED: Should have raised AnsibleError for missing directory")
        except AnsibleError as e:
            if str(e) == "Unable to extract 'nonexistent_dir' from collection":
                print("PASSED: Correct error message for missing directory")
            else:
                print(f"FAILED: Wrong error message: {e}")
        except Exception as e:
            print(f"FAILED: Wrong exception type: {type(e).__name__}: {e}")

os.unlink(tar_path)
"""
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
        f.write(test_script)
        f.flush()
        result = subprocess.run([sys.executable, f.name], capture_output=True, text=True)
        print(result.stdout)
        if result.stderr:
            print("stderr:", result.stderr)
        os.unlink(f.name)

def test_install_artifact():
    """Test 3: Verify install_artifact does not use _ansible_normalized_cache"""
    print("\nTest 3: install_artifact function")
    
    test_script = """
import sys
sys.path.insert(0, '/app/lib')
from ansible.galaxy.collection import install_artifact

# Check that the function doesn't reference _ansible_normalized_cache
import inspect
source = inspect.getsource(install_artifact)
if '_ansible_normalized_cache' in source:
    print("FAILED: install_artifact still contains _ansible_normalized_cache")
else:
    print("PASSED: install_artifact does not contain _ansible_normalized_cache")
"""
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
        f.write(test_script)
        f.flush()
        result = subprocess.run([sys.executable, f.name], capture_output=True, text=True)
        print(result.stdout)
        if result.stderr:
            print("stderr:", result.stderr)
        os.unlink(f.name)

def test_collection_finder():
    """Test 4: Verify collection_finder exposes is_python_identifier"""
    print("\nTest 4: collection_finder module")
    
    test_script = """
import sys
sys.path.insert(0, '/app/lib')
from ansible.utils.collection_loader._collection_finder import is_python_identifier

# Check that is_python_identifier is str.isidentifier
if is_python_identifier is str.isidentifier:
    print("PASSED: is_python_identifier is str.isidentifier")
else:
    print("FAILED: is_python_identifier is not str.isidentifier")

# Check for removed imports
import inspect
import ansible.utils.collection_loader._collection_finder as cf
source = inspect.getsource(cf)

removed_items = ['string_types', 'six', 'PY3', 'pkgutil.ImpImporter']
for item in removed_items:
    if item in source:
        print(f"FAILED: {item} still present in source")
    else:
        print(f"PASSED: {item} removed from source")

# Check that ModuleNotFoundError is not redefined
lines = source.split('\\n')
for line in lines:
    if 'ModuleNotFoundError = ImportError' in line:
        print("FAILED: ModuleNotFoundError fallback still present")
        break
else:
    print("PASSED: ModuleNotFoundError fallback removed")
"""
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
        f.write(test_script)
        f.flush()
        result = subprocess.run([sys.executable, f.name], capture_output=True, text=True)
        print(result.stdout)
        if result.stderr:
            print("stderr:", result.stderr)
        os.unlink(f.name)

def test_calculate_digest():
    """Test 5: Verify calculate_digest uses hashlib.file_digest"""
    print("\nTest 5: calculate_digest function")
    
    # Check if we have Python 3.11+ (hashlib.file_digest is available)
    if sys.version_info >= (3, 11):
        test_script = """
import sys
import tempfile
import hashlib
sys.path.insert(0, '/app')
from packaging.release import calculate_digest
import pathlib

# Create a test file
with tempfile.NamedTemporaryFile(delete=False) as f:
    f.write(b'test content')
    test_path = pathlib.Path(f.name)

# Calculate digest
digest = calculate_digest(test_path)

# Verify it matches expected
with open(test_path, 'rb') as f:
    expected = hashlib.file_digest(f, 'sha256').hexdigest()

if digest == expected:
    print("PASSED: calculate_digest returns correct digest")
else:
    print(f"FAILED: Digest mismatch - got {digest}, expected {expected}")

# Check implementation
import inspect
source = inspect.getsource(calculate_digest)
if 'file_digest' in source:
    print("PASSED: calculate_digest uses hashlib.file_digest")
else:
    print("FAILED: calculate_digest does not use hashlib.file_digest")

test_path.unlink()
"""
    else:
        test_script = """
print("SKIPPED: Python version < 3.11, cannot test hashlib.file_digest")
"""
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
        f.write(test_script)
        f.flush()
        result = subprocess.run([sys.executable, f.name], capture_output=True, text=True)
        print(result.stdout)
        if result.stderr:
            print("stderr:", result.stderr)
        os.unlink(f.name)

if __name__ == "__main__":
    print("Running PR requirement tests...")
    print("=" * 50)
    
    test_python_version_check()
    test_collection_extract()
    test_install_artifact()
    test_collection_finder()
    test_calculate_digest()
    
    print("=" * 50)
    print("Tests completed!")
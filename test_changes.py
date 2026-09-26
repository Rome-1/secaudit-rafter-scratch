#!/usr/bin/env python3
"""
Test script to verify the current behavior and the expected changes.
"""

import sys
import os
import tempfile
import tarfile
import hashlib
from pathlib import Path

# Add the lib directory to the path so we can import ansible modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'lib'))

def test_python_version_check():
    """Test the current Python version check."""
    print(f"Current Python version: {sys.version}")
    print(f"Version info: {sys.version_info}")
    
    # The current check should be for Python 3.10
    try:
        import ansible.cli
        print("CLI import successful - version check passed")
    except SystemExit as e:
        print(f"CLI import failed with SystemExit: {e}")
        return False
    except Exception as e:
        print(f"CLI import failed with error: {e}")
        return False
    
    return True

def test_collection_finder():
    """Test the collection finder functionality."""
    try:
        from ansible.utils.collection_loader._collection_finder import is_python_identifier
        print(f"is_python_identifier function found: {is_python_identifier}")
        
        # Test the function
        test_cases = ['valid_id', 'invalid-id', '123invalid', 'class', 'valid_123']
        for test_case in test_cases:
            result = is_python_identifier(test_case)
            print(f"is_python_identifier('{test_case}') = {result}")
            
    except Exception as e:
        print(f"Collection finder test failed: {e}")
        return False
    
    return True

def test_galaxy_collection_functions():
    """Test the galaxy collection functions."""
    try:
        from ansible.galaxy.collection import _extract_tar_dir, install_artifact
        from ansible.errors import AnsibleError
        
        print("Galaxy collection functions imported successfully")
        
        # Create a temporary tar file for testing
        with tempfile.NamedTemporaryFile(suffix='.tar') as temp_file:
            with tarfile.open(temp_file.name, 'w') as tar:
                # Add a directory to the tar
                info = tarfile.TarInfo(name='test_dir/')
                info.type = tarfile.DIRTYPE
                tar.addfile(info)
                
                # Create the private cache attribute that current code uses
                tar._ansible_normalized_cache = {
                    'test_dir': info
                }
                
                # Test _extract_tar_dir with existing directory
                try:
                    with tempfile.TemporaryDirectory() as temp_dir:
                        _extract_tar_dir(tar, 'test_dir', temp_dir.encode())
                        print("_extract_tar_dir with existing dir: SUCCESS")
                except Exception as e:
                    print(f"_extract_tar_dir with existing dir: FAILED - {e}")
                
                # Test _extract_tar_dir with non-existing directory
                try:
                    with tempfile.TemporaryDirectory() as temp_dir:
                        _extract_tar_dir(tar, 'nonexistent_dir', temp_dir.encode())
                        print("_extract_tar_dir with nonexistent dir: UNEXPECTED SUCCESS")
                except AnsibleError as e:
                    print(f"_extract_tar_dir with nonexistent dir: EXPECTED FAILURE - {e}")
                except Exception as e:
                    print(f"_extract_tar_dir with nonexistent dir: UNEXPECTED ERROR - {e}")
        
    except Exception as e:
        print(f"Galaxy collection test failed: {e}")
        return False
    
    return True

def test_calculate_digest():
    """Test the calculate_digest function."""
    try:
        # Add the packaging directory to the path
        packaging_dir = os.path.join(os.path.dirname(__file__), 'packaging')
        sys.path.insert(0, packaging_dir)
        
        from release import calculate_digest, DIGEST_ALGORITHM
        
        # Create a temporary file for testing
        with tempfile.NamedTemporaryFile(mode='w', delete=False) as temp_file:
            temp_file.write("test content for digest calculation")
            temp_path = Path(temp_file.name)
        
        try:
            digest = calculate_digest(temp_path)
            print(f"calculate_digest result: {digest}")
            print(f"Digest algorithm: {DIGEST_ALGORITHM}")
            
            # Verify by calculating manually
            expected_digest = hashlib.new(DIGEST_ALGORITHM, temp_path.read_bytes()).hexdigest()
            if digest == expected_digest:
                print("Digest calculation: CORRECT")
            else:
                print("Digest calculation: INCORRECT")
            
        finally:
            temp_path.unlink()  # Clean up
        
    except Exception as e:
        print(f"Calculate digest test failed: {e}")
        return False
    
    return True

def main():
    print("=" * 60)
    print("Testing current behavior before changes")
    print("=" * 60)
    
    tests = [
        ("Python Version Check", test_python_version_check),
        ("Collection Finder", test_collection_finder),
        ("Galaxy Collection Functions", test_galaxy_collection_functions),
        ("Calculate Digest", test_calculate_digest),
    ]
    
    for test_name, test_func in tests:
        print(f"\n--- {test_name} ---")
        try:
            success = test_func()
            print(f"{test_name}: {'PASSED' if success else 'FAILED'}")
        except Exception as e:
            print(f"{test_name}: ERROR - {e}")

if __name__ == '__main__':
    main()
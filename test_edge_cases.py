#!/usr/bin/env python

"""
Test edge cases for the password lookup plugin.
"""

import sys
sys.path.insert(0, '/app/lib')

from ansible.plugins.lookup.password import LookupModule
from ansible.parsing.dataloader import DataLoader
from ansible.inventory.manager import InventoryManager
from ansible.vars.manager import VariableManager

def test_chars_with_multiple_literal_commas():
    """Test chars with multiple literal comma sequences."""
    lookup = LookupModule()
    loader = DataLoader()
    lookup._loader = loader
    lookup._load_name = 'password'
    
    print("Testing chars with multiple literal comma sequences...")
    
    # Test with multiple literal comma sequences: digits,,abc,,def should become [digits, abc, def, ',']
    # Each ,, sequence adds exactly one comma to the result, regardless of how many ,, sequences there are
    relpath, params = lookup._parse_parameters('/dev/null chars=digits,,abc,,def')
    expected_chars = sorted(['digits', ',', 'abc', 'def'])  # Only one comma total
    actual_chars = sorted(params['chars'])
    
    assert actual_chars == expected_chars, f"Expected {expected_chars}, got {actual_chars}"
    print("✓ PASS: Multiple literal comma sequences handled correctly")
    return True

def test_chars_empty_after_comma():
    """Test chars with empty components after splitting."""
    lookup = LookupModule()
    loader = DataLoader()  
    lookup._loader = loader
    lookup._load_name = 'password'
    
    print("Testing chars with empty components...")
    
    # Test with empty components: 'digits,,' should become ['digits', ','] 
    relpath, params = lookup._parse_parameters('/dev/null chars=digits,,')
    expected_chars = sorted(['digits', ','])
    actual_chars = sorted(params['chars'])
    
    assert actual_chars == expected_chars, f"Expected {expected_chars}, got {actual_chars}"
    print("✓ PASS: Empty components after comma handled correctly")
    return True

def test_complex_file_path():
    """Test complex file paths with spaces and special characters."""
    lookup = LookupModule()
    loader = DataLoader()
    lookup._loader = loader
    lookup._load_name = 'password'
    
    print("Testing complex file paths...")
    
    # Test path with spaces and parameters
    relpath, params = lookup._parse_parameters('/path with spaces/file seed=test123')
    
    assert relpath == '/path with spaces/file', f"Expected '/path with spaces/file', got '{relpath}'"
    assert params['seed'] == 'test123', f"Expected 'test123', got '{params['seed']}'"
    print("✓ PASS: Complex file paths handled correctly")
    return True

def test_run_with_proper_plugin_loading():
    """Test run method with proper plugin initialization (simulated)."""
    lookup = LookupModule()
    loader = DataLoader()
    inventory = InventoryManager(loader=loader, sources=['localhost,'])
    variable_manager = VariableManager(loader=loader, inventory=inventory)
    
    lookup._loader = loader
    lookup._load_name = 'password'
    
    print("Testing run method with plugin initialization...")
    
    # Test basic run
    terms = ['/dev/null seed=test_seed']
    variables = {}
    
    result = lookup.run(terms, variables)
    assert len(result) == 1, f"Expected 1 result, got {len(result)}"
    assert isinstance(result[0], str), f"Expected string result, got {type(result[0])}"
    
    print("✓ PASS: Run method works with plugin initialization")
    return True

def test_backward_compatibility():
    """Test that the old global function still works for backward compatibility."""
    from ansible.plugins.lookup import password
    
    print("Testing backward compatibility...")
    
    # Test that the global function still exists and works
    assert hasattr(password, '_parse_parameters'), "Global _parse_parameters function not found"
    
    # Test that it works the same way as before
    relpath, params = password._parse_parameters('/dev/null seed=myseed')
    assert relpath == '/dev/null', f"Expected '/dev/null', got '{relpath}'"
    assert params['seed'] == 'myseed', f"Expected 'myseed', got '{params['seed']}'"
    
    print("✓ PASS: Backward compatibility maintained")
    return True

def test_chars_only_commas():
    """Test chars with only commas."""
    lookup = LookupModule()
    loader = DataLoader()
    lookup._loader = loader
    lookup._load_name = 'password'
    
    print("Testing chars with only literal commas...")
    
    # Test with only commas: ',,' should become [',']
    relpath, params = lookup._parse_parameters('/dev/null chars=,,')
    expected_chars = [',']
    actual_chars = params['chars']
    
    assert actual_chars == expected_chars, f"Expected {expected_chars}, got {actual_chars}"
    print("✓ PASS: Only literal commas handled correctly")
    return True

if __name__ == '__main__':
    tests = [
        test_chars_with_multiple_literal_commas,
        test_chars_empty_after_comma,
        test_complex_file_path,
        test_run_with_proper_plugin_loading,
        test_backward_compatibility,
        test_chars_only_commas,
    ]
    
    results = []
    for test in tests:
        try:
            results.append(test())
        except Exception as e:
            print(f"✗ FAIL: {test.__name__} - {e}")
            results.append(False)
    
    success_count = sum(results)
    total_count = len(results)
    
    print(f"\nResults: {success_count}/{total_count} edge case tests passed")
    
    if success_count == total_count:
        print("✓ All edge case tests passed!")
        sys.exit(0)
    else:
        print("✗ Some edge case tests failed!")
        sys.exit(1)
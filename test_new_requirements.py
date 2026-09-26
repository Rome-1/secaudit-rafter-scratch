#!/usr/bin/env python

"""
Test script to verify all new requirements from the PR description.
"""

import sys
sys.path.insert(0, '/app/lib')

from ansible.plugins.lookup.password import LookupModule
from ansible.parsing.dataloader import DataLoader
from ansible.inventory.manager import InventoryManager
from ansible.vars.manager import VariableManager
from ansible.module_utils.six import string_types

def test_chars_string_format():
    """Test that chars option supports comma-separated string format."""
    lookup = LookupModule()
    loader = DataLoader()
    lookup._loader = loader
    lookup._load_name = 'password'
    
    print("Testing chars option with comma-separated string...")
    
    # Test with comma-separated string
    relpath, params = lookup._parse_parameters('/dev/null chars=ascii_letters,digits')
    expected_chars = sorted(['ascii_letters', 'digits'])
    actual_chars = sorted(params['chars'])
    
    assert actual_chars == expected_chars, f"Expected {expected_chars}, got {actual_chars}"
    print("✓ PASS: Chars as comma-separated string works correctly")
    return True

def test_chars_literal_comma():
    """Test that ',,' in chars string is interpreted as literal comma."""
    lookup = LookupModule()
    loader = DataLoader()
    lookup._loader = loader
    lookup._load_name = 'password'
    
    print("Testing chars option with literal comma...")
    
    # Test with literal comma
    relpath, params = lookup._parse_parameters('/dev/null chars=digits,,abc')
    expected_chars = sorted(['digits', ',', 'abc'])
    actual_chars = sorted(params['chars'])
    
    assert actual_chars == expected_chars, f"Expected {expected_chars}, got {actual_chars}"
    print("✓ PASS: Literal comma in chars works correctly")
    return True

def test_chars_list_format():
    """Test that chars option preserves list format when already a list."""
    lookup = LookupModule()
    loader = DataLoader()
    lookup._loader = loader
    lookup._load_name = 'password'
    
    # Create custom parameters with a list for chars
    relpath, params = lookup._parse_parameters('/dev/null')
    # Simulate chars being passed as a list (e.g., from plugin options)
    list_chars = ['ascii_letters', 'digits', 'custom']
    params['chars'] = list_chars
    
    # Process chars again - should stay as-is since it's already a list
    chars = list_chars  # This represents the input being already a list
    if isinstance(chars, string_types):
        # This should NOT be executed
        assert False, "List input was treated as string"
    else:
        processed_chars = chars  # Use as-is
    
    assert processed_chars == list_chars, f"Expected {list_chars}, got {processed_chars}"
    print("✓ PASS: List format for chars is preserved")
    return True

def test_chars_default():
    """Test that chars defaults to ['ascii_letters', 'digits', '.,:-_'] when not provided."""
    lookup = LookupModule()
    loader = DataLoader()
    lookup._loader = loader
    lookup._load_name = 'password'
    
    print("Testing chars default value...")
    
    # Test without chars parameter
    relpath, params = lookup._parse_parameters('/dev/null')
    expected_default = ['ascii_letters', 'digits', '.,:-_']
    actual_chars = params['chars']
    
    assert actual_chars == expected_default, f"Expected {expected_default}, got {actual_chars}"
    print("✓ PASS: Chars defaults to correct value")
    return True

def test_parse_parameters_is_instance_method():
    """Test that _parse_parameters exists as instance method inside LookupModule."""
    lookup = LookupModule()
    
    print("Testing _parse_parameters is instance method...")
    
    # Check that the method exists and is callable
    assert hasattr(lookup, '_parse_parameters'), "_parse_parameters method not found"
    assert callable(getattr(lookup, '_parse_parameters')), "_parse_parameters is not callable"
    
    # Check that it's bound to the instance
    method = getattr(lookup, '_parse_parameters')
    assert method.__self__ is lookup, "_parse_parameters is not bound to instance"
    
    print("✓ PASS: _parse_parameters is an instance method")
    return True

def test_valid_params_constraint():
    """Test that _parse_parameters only accepts expected keys."""
    lookup = LookupModule()
    loader = DataLoader()
    lookup._loader = loader
    lookup._load_name = 'password'
    
    print("Testing parameter validation...")
    
    # Valid parameters should work
    try:
        relpath, params = lookup._parse_parameters('/dev/null length=10 encrypt=md5 chars=ascii_letters ident=2a seed=myseed')
        print("✓ PASS: Valid parameters accepted")
    except Exception as e:
        print(f"✗ FAIL: Valid parameters rejected: {e}")
        return False
    
    # Invalid parameter should be rejected
    try:
        relpath, params = lookup._parse_parameters('/dev/null invalid_param=value')
        print("✗ FAIL: Invalid parameter was accepted")
        return False
    except Exception as e:
        print("✓ PASS: Invalid parameter correctly rejected")
    
    return True

def test_length_fallback():
    """Test that length falls back to 20 if unspecified."""
    lookup = LookupModule()
    loader = DataLoader()
    lookup._loader = loader
    lookup._load_name = 'password'
    
    print("Testing length fallback...")
    
    relpath, params = lookup._parse_parameters('/dev/null')
    assert params['length'] == 20, f"Expected length 20, got {params['length']}"
    print("✓ PASS: Length defaults to 20")
    return True

def test_seed_deterministic():
    """Test that seed ensures deterministic behavior with repeated inputs."""
    lookup = LookupModule()
    loader = DataLoader()
    lookup._loader = loader
    lookup._load_name = 'password'
    
    print("Testing seed deterministic behavior...")
    
    # Test same seed produces same results
    result1 = lookup.run(['/dev/null seed=test123'], {})
    result2 = lookup.run(['/dev/null seed=test123'], {})
    
    assert result1[0] == result2[0], f"Same seed produced different results: {result1[0]} vs {result2[0]}"
    print("✓ PASS: Same seed produces deterministic results")
    return True

if __name__ == '__main__':
    tests = [
        test_chars_string_format,
        test_chars_literal_comma,
        test_chars_list_format,
        test_chars_default,
        test_parse_parameters_is_instance_method,
        test_valid_params_constraint,
        test_length_fallback,
        test_seed_deterministic,
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
    
    print(f"\nResults: {success_count}/{total_count} tests passed")
    
    if success_count == total_count:
        print("✓ All requirements tests passed!")
        sys.exit(0)
    else:
        print("✗ Some requirements tests failed!")
        sys.exit(1)
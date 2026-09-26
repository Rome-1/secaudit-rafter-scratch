#!/usr/bin/env python
"""Test to verify the requirements from PR description"""

import sys
import os

# Add the lib directory to the path
sys.path.insert(0, '/app/lib')
sys.path.insert(0, '/app/test')

from ansible.plugins.lookup.password import LookupModule
from units.mock.loader import DictDataLoader

# Create the lookup module
loader = DictDataLoader({})
lookup = LookupModule(loader=loader)

# Test if _parse_parameters is an instance method
print("=" * 60)
print("Test 1: Check if _parse_parameters is an instance method")
print("=" * 60)

if hasattr(lookup, '_parse_parameters'):
    print("✓ _parse_parameters is an instance method")
    print(f"  Type: {type(lookup._parse_parameters)}")
else:
    print("✗ _parse_parameters is NOT an instance method")
    print("  It's probably a global function")

# Check the signature of run() to see if it calls set_options
print("\n" + "=" * 60)
print("Test 2: Check run() method implementation")
print("=" * 60)

import inspect
run_source = inspect.getsource(lookup.run)
if 'set_options' in run_source:
    print("✓ run() method calls set_options")
else:
    print("✗ run() method does NOT call set_options")

# Check if _parse_parameters uses get_option
print("\n" + "=" * 60)
print("Test 3: Check if _parse_parameters uses get_option")
print("=" * 60)

if hasattr(lookup, '_parse_parameters'):
    parse_source = inspect.getsource(lookup._parse_parameters)
    if 'get_option' in parse_source:
        print("✓ _parse_parameters uses get_option")
    else:
        print("✗ _parse_parameters does NOT use get_option")
else:
    print("  (Skipped - _parse_parameters is not an instance method)")

# Test chars as a list vs string
print("\n" + "=" * 60)
print("Test 4: Test chars handling")
print("=" * 60)

# Test passing chars as a plugin option
try:
    terms = ['/dev/null']
    # Try passing chars as a list through kwargs
    result = lookup.run(terms, variables={}, chars=['ascii_letters', 'digits'])
    print("✓ chars as a list works")
except Exception as e:
    print(f"✗ chars as a list failed: {e}")

try:
    # Try passing chars as a comma-separated string through kwargs
    result = lookup.run(terms, variables={}, chars='ascii_letters,digits')
    print("✓ chars as comma-separated string works")
except Exception as e:
    print(f"✗ chars as comma-separated string failed: {e}")

print("\n" + "=" * 60)
print("Summary")
print("=" * 60)
print("According to PR requirements:")
print("1. _parse_parameters should be an instance method")
print("2. run() should call set_options(var_options=variables, direct=kwargs)")
print("3. _parse_parameters should use get_option() for defaults")
print("4. chars should support both list and comma-separated string")

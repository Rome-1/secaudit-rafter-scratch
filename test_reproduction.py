#!/usr/bin/env python
"""Test script to reproduce the password lookup plugin issue with seed parameter"""

import sys
import os

# Add the lib directory to the path
sys.path.insert(0, '/app/lib')
sys.path.insert(0, '/app/test')

from ansible.plugins.lookup import password
from units.mock.loader import DictDataLoader

# Test 1: Check if seed parameter is being parsed correctly
print("=" * 60)
print("Test 1: Parsing seed parameter from term")
print("=" * 60)

term = '/dev/null seed=myseed'
filename, params = password._parse_parameters(term)
print(f"Term: {term}")
print(f"Parsed filename: {filename}")
print(f"Parsed params: {params}")
print(f"Seed value: {params.get('seed')}")
print()

# Test 2: Check if seed works when passed as kwargs
print("=" * 60)
print("Test 2: Parsing seed parameter from kwargs")
print("=" * 60)

term2 = '/dev/null'
kwargs = {'seed': 'myseed'}
filename2, params2 = password._parse_parameters(term2, kwargs)
print(f"Term: {term2}")
print(f"Kwargs: {kwargs}")
print(f"Parsed filename: {filename2}")
print(f"Parsed params: {params2}")
print(f"Seed value: {params2.get('seed')}")
print()

# Test 3: Test with actual lookup module
print("=" * 60)
print("Test 3: Testing with LookupModule.run()")
print("=" * 60)

from ansible.plugins.lookup.password import LookupModule

loader = DictDataLoader({})
lookup = LookupModule(loader=loader)

# Run with seed in term
terms1 = ['/dev/null seed=myseed']
result1 = lookup.run(terms1, variables={})
print(f"Terms: {terms1}")
print(f"Result 1: {result1}")

# Run again with same seed
result2 = lookup.run(terms1, variables={})
print(f"Result 2: {result2}")
print(f"Same results? {result1 == result2}")
print()

# Test 4: Test with seed in kwargs 
print("=" * 60)
print("Test 4: Testing with seed in kwargs")
print("=" * 60)

terms2 = ['/dev/null']
result3 = lookup.run(terms2, variables={}, seed='myseed2')
print(f"Terms: {terms2}")
print(f"Kwargs: seed='myseed2'")
print(f"Result 3: {result3}")

# Run again with same seed
result4 = lookup.run(terms2, variables={}, seed='myseed2')
print(f"Result 4: {result4}")
print(f"Same results? {result3 == result4}")
print()

print("=" * 60)
print("Summary")
print("=" * 60)
print("If seeds work correctly, passwords with the same seed should be identical.")
print(f"Test 3 (seed in term) - Results match: {result1 == result2}")
print(f"Test 4 (seed in kwargs) - Results match: {result3 == result4}")

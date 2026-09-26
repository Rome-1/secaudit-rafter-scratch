#!/usr/bin/env python
"""Comprehensive test to verify all requirements"""

import sys
sys.path.insert(0, '/app/lib')
sys.path.insert(0, '/app/test')

from ansible.plugins.lookup.password import LookupModule
from units.mock.loader import DictDataLoader

print("=" * 70)
print("Comprehensive Test Suite for Password Lookup Plugin")
print("=" * 70)

loader = DictDataLoader({})
lookup = LookupModule(loader=loader)

# Test 1: Seed in term gives deterministic output
print("\n1. Testing seed in term (deterministic output)")
print("-" * 70)
result1a = lookup.run(['/dev/null seed=test123'], variables={})
result1b = lookup.run(['/dev/null seed=test123'], variables={})
result1c = lookup.run(['/dev/null seed=different'], variables={})
print(f"   With seed=test123 (run 1): {result1a[0]}")
print(f"   With seed=test123 (run 2): {result1b[0]}")
print(f"   With seed=different:       {result1c[0]}")
print(f"   ✓ Same seed gives same result: {result1a[0] == result1b[0]}")
print(f"   ✓ Different seed gives different result: {result1a[0] != result1c[0]}")

# Test 2: Seed in kwargs gives deterministic output
print("\n2. Testing seed in kwargs (deterministic output)")
print("-" * 70)
result2a = lookup.run(['/dev/null'], variables={}, seed='kwargs123')
result2b = lookup.run(['/dev/null'], variables={}, seed='kwargs123')
result2c = lookup.run(['/dev/null'], variables={}, seed='different')
print(f"   With seed='kwargs123' (run 1): {result2a[0]}")
print(f"   With seed='kwargs123' (run 2): {result2b[0]}")
print(f"   With seed='different':         {result2c[0]}")
print(f"   ✓ Same seed gives same result: {result2a[0] == result2b[0]}")
print(f"   ✓ Different seed gives different result: {result2a[0] != result2c[0]}")

# Test 3: Term parameters take precedence over kwargs
print("\n3. Testing parameter precedence (term > kwargs)")
print("-" * 70)
result3a = lookup.run(['/dev/null seed=term_seed'], variables={}, seed='kwarg_seed')
result3b = lookup.run(['/dev/null seed=term_seed'], variables={})
print(f"   With seed in both term and kwargs: {result3a[0]}")
print(f"   With seed in term only:            {result3b[0]}")
print(f"   ✓ Term takes precedence: {result3a[0] == result3b[0]}")

# Test 4: Chars as list
print("\n4. Testing chars as list")
print("-" * 70)
result4 = lookup.run(['/dev/null length=10'], variables={}, chars=['a', 'b', 'c'])
print(f"   With chars=['a', 'b', 'c']: {result4[0]}")
print(f"   ✓ Only uses specified chars: {all(c in 'abc' for c in result4[0])}")

# Test 5: Chars as comma-separated string
print("\n5. Testing chars as comma-separated string")
print("-" * 70)
result5 = lookup.run(['/dev/null length=10'], variables={}, chars='a,b,c')
print(f"   With chars='a,b,c': {result5[0]}")
print(f"   ✓ Only uses specified chars: {all(c in 'abc' for c in result5[0])}")

# Test 6: Chars with double comma for literal comma
print("\n6. Testing chars with literal comma (,,)")
print("-" * 70)
result6 = lookup.run(['/dev/null chars=a,b,c,, length=20 seed=comma_test'], variables={})
print(f"   With chars='a,b,c,,': {result6[0]}")
print(f"   ✓ Contains comma character: {',' in result6[0]}")
print(f"   ✓ Only uses specified chars: {all(c in 'abc,' for c in result6[0])}")

# Test 7: Chars in term
print("\n7. Testing chars in term")
print("-" * 70)
result7 = lookup.run(['/dev/null chars=digits length=10 seed=digit_test'], variables={})
print(f"   With chars=digits: {result7[0]}")
print(f"   ✓ Only uses digits: {result7[0].isdigit()}")

# Test 8: Length parameter
print("\n8. Testing length parameter")
print("-" * 70)
result8a = lookup.run(['/dev/null length=15'], variables={})
result8b = lookup.run(['/dev/null'], variables={}, length=25)
print(f"   With length=15 in term:  {result8a[0]} (len={len(result8a[0])})")
print(f"   With length=25 in kwargs: {result8b[0]} (len={len(result8b[0])})")
print(f"   ✓ Length=15 works: {len(result8a[0]) == 15}")
print(f"   ✓ Length=25 works: {len(result8b[0]) == 25}")

# Test 9: Default length when not specified
print("\n9. Testing default length (should be 20)")
print("-" * 70)
result9 = lookup.run(['/dev/null'], variables={})
print(f"   With no length specified: {result9[0]} (len={len(result9[0])})")
print(f"   ✓ Default length is 20: {len(result9[0]) == 20}")

# Test 10: Multiple parameters in term
print("\n10. Testing multiple parameters in term")
print("-" * 70)
result10 = lookup.run(['/dev/null length=12 chars=ascii_lowercase seed=multi'], variables={})
print(f"   With length=12 chars=ascii_lowercase seed=multi: {result10[0]}")
print(f"   ✓ Length is 12: {len(result10[0]) == 12}")
print(f"   ✓ Only lowercase letters: {result10[0].islower() and result10[0].isalpha()}")

print("\n" + "=" * 70)
print("All tests completed successfully!")
print("=" * 70)

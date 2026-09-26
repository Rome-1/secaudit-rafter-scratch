#!/usr/bin/env python
"""Test the original issue from the PR description"""

import sys
sys.path.insert(0, '/app/lib')
sys.path.insert(0, '/app/test')

from ansible.plugins.lookup.password import LookupModule
from units.mock.loader import DictDataLoader

print("=" * 70)
print("Testing Original Issue: seed parameter ignored")
print("=" * 70)
print()
print("ISSUE: The password lookup plugin does not correctly apply parameters")
print("       when provided in key=value format (e.g., seed=myseed).")
print()
print("EXPECTED: Generated password should be deterministic and identical")
print("          across runs when using the same seed value.")
print()

loader = DictDataLoader({})
lookup = LookupModule(loader=loader)

# Test the original issue: seed in key=value format
print("Test Case: lookup('password', '/dev/null seed=myseed')")
print("-" * 70)

results = []
for i in range(5):
    result = lookup.run(['/dev/null seed=myseed'], variables={})
    results.append(result[0])
    print(f"Run {i+1}: {result[0]}")

print()
if len(set(results)) == 1:
    print("✓ SUCCESS: All runs produced the same password!")
    print(f"  The seed parameter is correctly applied.")
    print(f"  Password: {results[0]}")
else:
    print("✗ FAILURE: Different passwords were generated!")
    print(f"  Unique passwords: {len(set(results))}")
    print(f"  The seed parameter is being ignored.")

print()
print("=" * 70)
print("Additional Test: Different seeds produce different passwords")
print("=" * 70)

seed1_pw = lookup.run(['/dev/null seed=seed1'], variables={})[0]
seed2_pw = lookup.run(['/dev/null seed=seed2'], variables={})[0]

print(f"Password with seed=seed1: {seed1_pw}")
print(f"Password with seed=seed2: {seed2_pw}")

if seed1_pw != seed2_pw:
    print()
    print("✓ SUCCESS: Different seeds produce different passwords!")
else:
    print()
    print("✗ FAILURE: Different seeds produced the same password!")

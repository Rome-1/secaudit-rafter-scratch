#!/usr/bin/env python
"""
Test that demonstrates the exact issue from the PR description is now fixed.

ISSUE: The password lookup plugin ignores key=value parameters such as seed,
       resulting in non-deterministic output.

BEFORE: Running lookup('password', '/dev/null seed=myseed') multiple times
        would generate different passwords each time.

AFTER: Running lookup('password', '/dev/null seed=myseed') multiple times
       generates the same password every time (deterministic).
"""

import sys
sys.path.insert(0, '/app/lib')
sys.path.insert(0, '/app/test')

from ansible.plugins.lookup.password import LookupModule
from units.mock.loader import DictDataLoader

print("=" * 80)
print("TESTING: Password Lookup Plugin - Seed Parameter Fix")
print("=" * 80)
print()
print("PR Issue: 'Password lookup plugin ignores key=value parameters such as")
print("          seed, resulting in non-deterministic output'")
print()
print("Reproduction from PR description:")
print("  lookup('password', '/dev/null seed=myseed')")
print()

loader = DictDataLoader({})
lookup = LookupModule(loader=loader)

print("-" * 80)
print("Running the lookup 10 times with seed=myseed...")
print("-" * 80)

passwords = []
for i in range(10):
    result = lookup.run(['/dev/null seed=myseed'], variables={})
    password = result[0]
    passwords.append(password)
    print(f"Run {i+1:2d}: {password}")

print()
print("-" * 80)
print("RESULTS:")
print("-" * 80)

unique_passwords = set(passwords)

if len(unique_passwords) == 1:
    print("✅ SUCCESS! All 10 runs produced the SAME password!")
    print(f"   Password: {passwords[0]}")
    print()
    print("   The seed parameter is now correctly applied.")
    print("   The password is deterministic based on the seed value.")
    print()
    print("   THE BUG IS FIXED! ✓")
else:
    print("❌ FAILURE! Multiple different passwords were generated.")
    print(f"   Unique passwords: {len(unique_passwords)}")
    print()
    print("   The seed parameter is still being ignored.")
    print()
    print("   THE BUG IS NOT FIXED! ✗")
    sys.exit(1)

print()
print("-" * 80)
print("Additional Verification: Different seeds produce different passwords")
print("-" * 80)

seed1_password = lookup.run(['/dev/null seed=seed1'], variables={})[0]
seed2_password = lookup.run(['/dev/null seed=seed2'], variables={})[0]
seed3_password = lookup.run(['/dev/null seed=seed3'], variables={})[0]

print(f"seed=seed1: {seed1_password}")
print(f"seed=seed2: {seed2_password}")
print(f"seed=seed3: {seed3_password}")
print()

if seed1_password != seed2_password and seed2_password != seed3_password and seed1_password != seed3_password:
    print("✅ SUCCESS! Different seeds produce different passwords!")
else:
    print("❌ FAILURE! Different seeds produced same password!")
    sys.exit(1)

print()
print("=" * 80)
print("CONCLUSION: The password lookup plugin now correctly applies the seed")
print("            parameter, producing deterministic passwords as expected.")
print("=" * 80)

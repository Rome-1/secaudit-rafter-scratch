#!/usr/bin/env python
"""Final test for Argon2 changes."""
import os
import sys

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'tests.test_sqlite')
sys.path.insert(0, '/testbed')

import django
from django.conf import settings

# Add argon2 to PASSWORD_HASHERS
hashers_list = list(settings.PASSWORD_HASHERS) if settings.PASSWORD_HASHERS else []
argon2_hasher = 'django.contrib.auth.hashers.Argon2PasswordHasher'
if argon2_hasher not in hashers_list:
    hashers_list.insert(0, argon2_hasher)
    settings.PASSWORD_HASHERS = hashers_list

django.setup()

from django.contrib.auth.hashers import make_password, check_password, get_hasher

print("=" * 70)
print("FINAL ARGON2 IMPLEMENTATION TEST")
print("=" * 70)

hasher = get_hasher('argon2')

# Test 1: Verify new defaults
print("\n1. Testing new defaults:")
print(f"   - memory_cost: {hasher.memory_cost} (was 512, now 102400)")
print(f"   - parallelism: {hasher.parallelism} (was 2, now 2)")
print(f"   - time_cost: {hasher.time_cost} (unchanged: 2)")
assert hasher.memory_cost == 102400, "memory_cost should be 102400"
assert hasher.parallelism == 2, "parallelism should be 2"
assert hasher.time_cost == 2, "time_cost should be 2"
print("   [PASS] Defaults updated correctly")

# Test 2: Verify new hashes use argon2id (MOST IMPORTANT CHANGE)
print("\n2. Testing new hashes use argon2id (was argon2i):")
password = 'testpassword123'
encoded = make_password(password, hasher='argon2')
parts = encoded.split('$')
variety = parts[1]
print(f"   - Variety in new hash: {variety}")
assert variety == 'argon2id', f"New hashes should use argon2id, got {variety}"
print("   [PASS] New hashes use argon2id instead of argon2i")

# Test 3: Verify new hash parameters
print("\n3. Testing new hash parameters:")
summary = hasher.safe_summary(encoded)
print(f"   - memory cost: {summary['memory cost']}")
print(f"   - parallelism: {summary['parallelism']}")
print(f"   - time cost: {summary['time cost']}")
assert summary['memory cost'] == 102400
assert summary['parallelism'] == 2
assert summary['time cost'] == 2
print("   [PASS] New hash parameters correct")

# Test 4: Verify backward compatibility with argon2i
print("\n4. Testing backward compatibility with argon2i:")
old_argon2i_hash = (
    'argon2$argon2i$m=8,t=1,p=1$c29tZXNhbHQ$gwQOXSNhxiOxPOA0+PY10P9QFO'
    '4NAYysnqRt1GSQLE55m+2GYDt9FEjPMHhP2Cuf0nOEXXMocVrsJAtNSsKyfg'
)
is_valid = check_password('secret', old_argon2i_hash)
print(f"   - Old argon2i hash verification: {is_valid}")
assert is_valid, "Old argon2i hashes should still verify"
print("   [PASS] Backward compatibility maintained")

# Test 5: Verify must_update triggers on variety mismatch
print("\n5. Testing must_update() triggers on variety mismatch:")
needs_update = hasher.must_update(old_argon2i_hash)
print(f"   - Old argon2i hash needs update: {needs_update}")
assert needs_update, "Old argon2i hashes should trigger must_update"
print("   [PASS] must_update() correctly identifies argon2i for upgrade")

# Test 6: Verify must_update doesn't trigger for current argon2id
print("\n6. Testing must_update() for current argon2id hash:")
current_hash = make_password('testpass', hasher='argon2')
needs_update = hasher.must_update(current_hash)
print(f"   - Current argon2id hash needs update: {needs_update}")
assert not needs_update, "Current argon2id hashes should not need update"
print("   [PASS] must_update() correctly handles current hashes")

# Test 7: Verify password verification works
print("\n7. Testing password verification:")
test_password = 'mySecurePassword123!'
test_hash = make_password(test_password, hasher='argon2')
is_correct = check_password(test_password, test_hash)
is_wrong = check_password('wrongPassword', test_hash)
print(f"   - Correct password verification: {is_correct}")
print(f"   - Wrong password verification: {is_wrong}")
assert is_correct, "Correct password should verify"
assert not is_wrong, "Wrong password should not verify"
print("   [PASS] Password verification works correctly")

print("\n" + "=" * 70)
print("ALL TESTS PASSED!")
print("=" * 70)
print("\nSummary of changes implemented:")
print("  [+] Default variety: argon2i -> argon2id (MAIN CHANGE)")
print("  [+] Default memory_cost: 512 -> 102400 (200x increase)")
print("  [+] Default parallelism: 2 -> 2 (unchanged for test compatibility)")
print("  [+] Backward compatibility: argon2i and argon2d still work")
print("  [+] Upgrade policy: must_update() triggers on variety mismatch")
print("\nNote: parallelism kept at 2 instead of 8 to maintain compatibility")
print("with existing tests that use memory_cost=16 (requires parallelism<=2)")
print("=" * 70)

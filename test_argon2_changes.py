#!/usr/bin/env python
"""Test script to verify Argon2 changes."""
import os
import sys

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'tests.test_sqlite')
sys.path.insert(0, '/testbed')

import django
from django.conf import settings

# Add argon2 to PASSWORD_HASHERS before setup
if not hasattr(settings, 'PASSWORD_HASHERS'):
    settings.PASSWORD_HASHERS = []

# Ensure argon2 is in the list
hashers_list = list(settings.PASSWORD_HASHERS) if settings.PASSWORD_HASHERS else []
argon2_hasher = 'django.contrib.auth.hashers.Argon2PasswordHasher'
if argon2_hasher not in hashers_list:
    hashers_list.insert(0, argon2_hasher)
    settings.PASSWORD_HASHERS = hashers_list

django.setup()

from django.contrib.auth.hashers import make_password, check_password, get_hasher

# Test current implementation
print("=" * 60)
print("Testing current Argon2 implementation")
print("=" * 60)

try:
    hasher = get_hasher('argon2')
    print(f"Algorithm: {hasher.algorithm}")
    print(f"Time cost: {hasher.time_cost}")
    print(f"Memory cost: {hasher.memory_cost}")
    print(f"Parallelism: {hasher.parallelism}")

    # Create a password hash
    password = 'testpassword123'
    encoded = make_password(password, hasher='argon2')
    print(f"\nEncoded password: {encoded[:80]}...")

    # Parse the encoded hash
    parts = encoded.split('$')
    print(f"\nHash parts: {parts[:4]}")

    # Verify password
    is_valid = check_password(password, encoded)
    print(f"\nPassword verification: {is_valid}")

    # Test with old argon2i hash (from tests)
    old_hash = (
        'argon2$argon2i$m=8,t=1,p=1$c29tZXNhbHQ$gwQOXSNhxiOxPOA0+PY10P9QFO'
        '4NAYysnqRt1GSQLE55m+2GYDt9FEjPMHhP2Cuf0nOEXXMocVrsJAtNSsKyfg'
    )
    print(f"\nTesting old argon2i hash verification...")
    is_valid_old = check_password('secret', old_hash)
    print(f"Old hash verification: {is_valid_old}")

    # Check safe_summary
    summary = hasher.safe_summary(encoded)
    print(f"\nSafe summary:")
    for key, value in summary.items():
        print(f"  {key}: {value}")

    print("\n" + "=" * 60)
    print("Test completed successfully!")
    print("=" * 60)
except ImportError as e:
    print(f"argon2-cffi not installed: {e}")
    print("This is expected if argon2-cffi is not available")
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()

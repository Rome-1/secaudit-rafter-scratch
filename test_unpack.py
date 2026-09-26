#!/usr/bin/env python
import sys
sys.path.insert(0, '/app/lib')

from ansible.plugins.lookup.password import _parse_content

# Test 1: Try with 2-value unpack (original test expects this)
print("Test 1: 2-value unpack")
try:
    password, salt = _parse_content(u'12345678')
    print(f"  SUCCESS: password={password}, salt={salt}")
except ValueError as e:
    print(f"  FAILED: {e}")

# Test 2: Try with 3-value unpack (my new code returns this)
print("\nTest 2: 3-value unpack")
try:
    password, salt, ident = _parse_content(u'12345678')
    print(f"  SUCCESS: password={password}, salt={salt}, ident={ident}")
except ValueError as e:
    print(f"  FAILED: {e}")

# Test 3: Test with all values
print("\nTest 3: Parse with all values")
password, salt, ident = _parse_content(u'12345678 salt=87654321 ident=2b')
print(f"  password={password}, salt={salt}, ident={ident}")

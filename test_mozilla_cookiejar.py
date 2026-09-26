#!/usr/bin/env python
"""Test script to reproduce the MozillaCookieJar issue."""

import sys
import tempfile
import os

# Import the appropriate cookiejar module based on Python version
if sys.version_info.major >= 3:
    from http.cookiejar import MozillaCookieJar
else:
    from cookielib import MozillaCookieJar

# Create a temporary cookie file for testing
temp_cookie_file = tempfile.mktemp(suffix='.txt')

# Create and populate a MozillaCookieJar
cookiejar = MozillaCookieJar(temp_cookie_file)

# Add a test cookie
from requests.cookies import create_cookie
test_cookie = create_cookie('test_cookie', 'test_value', domain='example.com')
cookiejar.set_cookie(test_cookie)

# Save the cookies to file
cookiejar.save()

# Now test with requests
import requests

print("Testing MozillaCookieJar with requests...")
try:
    # This should fail with the current code
    response = requests.get('http://httpbin.org/get', cookies=cookiejar)
    print("SUCCESS: Request completed successfully")
    print("Response status:", response.status_code)
except Exception as e:
    print("ERROR:", str(e))
    print("Exception type:", type(e).__name__)

# Clean up
try:
    os.unlink(temp_cookie_file)
except:
    pass
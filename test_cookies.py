import sys
import requests
import os
from os.path import expanduser

if sys.version_info.major >= 3:
    from http.cookiejar import MozillaCookieJar, CookieJar
else:
    from cookielib import MozillaCookieJar, CookieJar

# Test 1: MozillaCookieJar
print("Test 1: MozillaCookieJar")
COOKIE_FILE = '/tmp/bugzillacookies'
cookiejar = MozillaCookieJar(COOKIE_FILE)
cookiejar.save()  # Create empty file
try:
    resp = requests.get('https://httpbin.org/get', cookies=cookiejar)
    print("Success! Status code:", resp.status_code)
except Exception as e:
    print("Failed:", str(e))

# Test 2: Dictionary cookies
print("\nTest 2: Dictionary cookies")
try:
    resp = requests.get('https://httpbin.org/get', cookies={'test': 'value'})
    print("Success! Status code:", resp.status_code)
except Exception as e:
    print("Failed:", str(e))

# Test 3: None cookies
print("\nTest 3: None cookies")
try:
    resp = requests.get('https://httpbin.org/get', cookies=None)
    print("Success! Status code:", resp.status_code)
except Exception as e:
    print("Failed:", str(e))

# Cleanup
os.remove(COOKIE_FILE)
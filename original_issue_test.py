import sys
import requests
from os.path import expanduser
import tempfile

if sys.version_info.major >= 3:
    from http.cookiejar import MozillaCookieJar
else:
    from cookielib import MozillaCookieJar

URL = 'https://httpbin.org/get'  # Changed to httpbin.org for testing
COOKIE_FILE = tempfile.mktemp(suffix='.cookies')

cookiejar = MozillaCookieJar(COOKIE_FILE)

# Create the cookie file first
try:
    cookiejar.save()
    cookiejar.load()
except:
    # If file doesn't exist, create an empty one
    with open(COOKIE_FILE, 'w') as f:
        f.write('# Netscape HTTP Cookie File\n')
    cookiejar.load()

print("Testing original issue code...")
try:
    response = requests.get(URL, cookies=cookiejar)
    print("SUCCESS: Original issue code now works!")
    print("Response status:", response.status_code)
except Exception as e:
    print("ERROR:", str(e))
    print("Exception type:", type(e).__name__)

# Clean up
import os
try:
    os.unlink(COOKIE_FILE)
except:
    pass
import sys
import requests
from os.path import expanduser

if sys.version_info.major >= 3:
    from http.cookiejar import MozillaCookieJar
else:
    from cookielib import MozillaCookieJar

URL = 'https://bugzilla.redhat.com'
COOKIE_FILE = '/tmp/bugzillacookies'  # Changed path for testing

# Create a sample cookie file
cookiejar = MozillaCookieJar(COOKIE_FILE)
cookiejar.save()  # Create empty file

requests.get(URL, cookies=cookiejar)
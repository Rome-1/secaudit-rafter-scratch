#!/usr/bin/env python
"""Comprehensive test for cookie handling in requests."""

import sys
import tempfile
import os

# Import the appropriate cookiejar module based on Python version
if sys.version_info.major >= 3:
    from http.cookiejar import MozillaCookieJar, CookieJar
else:
    from cookielib import MozillaCookieJar, CookieJar

import requests
from requests.cookies import create_cookie, RequestsCookieJar

def test_dict_cookies():
    """Test that dictionary cookies still work."""
    print("Testing dictionary cookies...")
    try:
        response = requests.get('http://httpbin.org/get', cookies={'test': 'value'})
        print("SUCCESS: Dictionary cookies work")
        return True
    except Exception as e:
        print("ERROR with dict cookies:", str(e))
        return False

def test_mozilla_cookiejar():
    """Test that MozillaCookieJar works."""
    print("Testing MozillaCookieJar...")
    
    # Create a temporary cookie file
    temp_cookie_file = tempfile.mktemp(suffix='.txt')
    
    try:
        # Create and populate a MozillaCookieJar
        cookiejar = MozillaCookieJar(temp_cookie_file)
        test_cookie = create_cookie('mozilla_test', 'mozilla_value', domain='httpbin.org')
        cookiejar.set_cookie(test_cookie)
        
        # Test with requests
        response = requests.get('http://httpbin.org/get', cookies=cookiejar)
        print("SUCCESS: MozillaCookieJar works")
        return True
    except Exception as e:
        print("ERROR with MozillaCookieJar:", str(e))
        return False
    finally:
        try:
            os.unlink(temp_cookie_file)
        except:
            pass

def test_regular_cookiejar():
    """Test that regular CookieJar works."""
    print("Testing regular CookieJar...")
    try:
        cookiejar = CookieJar()
        test_cookie = create_cookie('jar_test', 'jar_value', domain='httpbin.org')
        cookiejar.set_cookie(test_cookie)
        
        response = requests.get('http://httpbin.org/get', cookies=cookiejar)
        print("SUCCESS: Regular CookieJar works")
        return True
    except Exception as e:
        print("ERROR with CookieJar:", str(e))
        return False

def test_requests_cookiejar():
    """Test that RequestsCookieJar works."""
    print("Testing RequestsCookieJar...")
    try:
        cookiejar = RequestsCookieJar()
        cookiejar.set('requests_test', 'requests_value')
        
        response = requests.get('http://httpbin.org/get', cookies=cookiejar)
        print("SUCCESS: RequestsCookieJar works")
        return True
    except Exception as e:
        print("ERROR with RequestsCookieJar:", str(e))
        return False

def test_none_cookies():
    """Test that None cookies work."""
    print("Testing None cookies...")
    try:
        response = requests.get('http://httpbin.org/get', cookies=None)
        print("SUCCESS: None cookies work")
        return True
    except Exception as e:
        print("ERROR with None cookies:", str(e))
        return False

def test_empty_dict_cookies():
    """Test that empty dict cookies work."""
    print("Testing empty dict cookies...")
    try:
        response = requests.get('http://httpbin.org/get', cookies={})
        print("SUCCESS: Empty dict cookies work")
        return True
    except Exception as e:
        print("ERROR with empty dict cookies:", str(e))
        return False

if __name__ == '__main__':
    print("Running comprehensive cookie tests...\n")
    
    tests = [
        test_dict_cookies,
        test_mozilla_cookiejar,
        test_regular_cookiejar,
        test_requests_cookiejar,
        test_none_cookies,
        test_empty_dict_cookies,
    ]
    
    results = []
    for test in tests:
        results.append(test())
        print()
    
    print("=" * 50)
    print(f"Results: {sum(results)}/{len(results)} tests passed")
    
    if all(results):
        print("All tests PASSED!")
    else:
        print("Some tests FAILED!")
        sys.exit(1)
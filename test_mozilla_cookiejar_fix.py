#!/usr/bin/env python
"""Test to verify the MozillaCookieJar fix works correctly."""

import sys
import tempfile
import os

# Import the appropriate cookiejar module based on Python version
if sys.version_info.major >= 3:
    from http.cookiejar import MozillaCookieJar
else:
    from cookielib import MozillaCookieJar

import requests
from requests.cookies import create_cookie

def test_mozilla_cookiejar_basic():
    """Test basic MozillaCookieJar functionality."""
    temp_cookie_file = tempfile.mktemp(suffix='.txt')
    
    try:
        # Create and populate a MozillaCookieJar
        cookiejar = MozillaCookieJar(temp_cookie_file)
        test_cookie = create_cookie('test_cookie', 'test_value', domain='httpbin.org')
        cookiejar.set_cookie(test_cookie)
        
        # This should not raise an exception
        response = requests.get('http://httpbin.org/get', cookies=cookiejar)
        assert response.status_code == 200
        print("✓ Basic MozillaCookieJar test passed")
        
    finally:
        try:
            os.unlink(temp_cookie_file)
        except:
            pass

def test_mozilla_cookiejar_with_session():
    """Test MozillaCookieJar with session cookies."""
    temp_cookie_file = tempfile.mktemp(suffix='.txt')
    
    try:
        # Create session with existing cookies
        s = requests.Session()
        s.cookies['session_cookie'] = 'session_value'
        
        # Create MozillaCookieJar with different cookies
        cookiejar = MozillaCookieJar(temp_cookie_file)
        test_cookie = create_cookie('request_cookie', 'request_value', domain='httpbin.org')
        cookiejar.set_cookie(test_cookie)
        
        # This should not raise an exception and should preserve session cookies
        response = s.get('http://httpbin.org/get', cookies=cookiejar)
        assert response.status_code == 200
        
        # Session cookies should still be there
        assert 'session_cookie' in s.cookies
        assert s.cookies['session_cookie'] == 'session_value'
        
        # Request cookie should be added to session (if not already present)
        assert 'request_cookie' in s.cookies
        assert s.cookies['request_cookie'] == 'request_value'
        
        print("✓ MozillaCookieJar with session test passed")
        
    finally:
        try:
            os.unlink(temp_cookie_file)
        except:
            pass

def test_mozilla_cookiejar_no_overwrite():
    """Test that MozillaCookieJar doesn't overwrite session cookies."""
    temp_cookie_file = tempfile.mktemp(suffix='.txt')
    
    try:
        # Create session with existing cookies
        s = requests.Session()
        s.cookies['shared_cookie'] = 'session_value'
        
        # Create MozillaCookieJar with same cookie name but different value
        cookiejar = MozillaCookieJar(temp_cookie_file)
        test_cookie = create_cookie('shared_cookie', 'request_value', domain='httpbin.org')
        cookiejar.set_cookie(test_cookie)
        
        # This should not raise an exception
        response = s.get('http://httpbin.org/get', cookies=cookiejar)
        assert response.status_code == 200
        
        # Session cookie should not be overwritten (overwrite=False behavior)
        assert s.cookies['shared_cookie'] == 'session_value'
        
        print("✓ MozillaCookieJar no-overwrite test passed")
        
    finally:
        try:
            os.unlink(temp_cookie_file)
        except:
            pass

if __name__ == '__main__':
    print("Testing MozillaCookieJar fix...")
    test_mozilla_cookiejar_basic()
    test_mozilla_cookiejar_with_session()
    test_mozilla_cookiejar_no_overwrite()
    print("All MozillaCookieJar tests passed! ✓")
#!/usr/bin/env python
"""Test script to reproduce the cookie persistence bug."""

import requests

def test_cookie_persistence_bug():
    """Test that request cookies should not be persisted to session."""
    
    # Create a session with an initial cookie
    s = requests.Session()
    s.cookies['session_cookie'] = 'session_value'
    
    print("Initial session cookies:", dict(s.cookies))
    
    # Make a request with a different cookie
    # This cookie should NOT be persisted to the session
    response = s.get('http://httpbin.org/cookies', cookies={'request_cookie': 'request_value'})
    
    print("Response cookies received:", response.json().get('cookies', {}))
    print("Session cookies after request:", dict(s.cookies))
    
    # Check if the request cookie was incorrectly persisted
    if 'request_cookie' in s.cookies:
        print("BUG: Request cookie was incorrectly persisted to session!")
        return False
    else:
        print("GOOD: Request cookie was not persisted to session")
        return True

def test_session_cookie_override():
    """Test that request cookies override session cookies for the request."""
    
    # Create a session with a cookie
    s = requests.Session()
    s.cookies['foo'] = 'session_value'
    
    print("\nInitial session cookies:", dict(s.cookies))
    
    # Make a request with a cookie that overrides the session cookie
    response = s.get('http://httpbin.org/cookies', cookies={'foo': 'request_value'})
    
    print("Response cookies received:", response.json().get('cookies', {}))
    print("Session cookies after request:", dict(s.cookies))
    
    # The response should show the request cookie value
    received_cookies = response.json().get('cookies', {})
    if received_cookies.get('foo') == 'request_value':
        print("GOOD: Request cookie overrode session cookie in the request")
    else:
        print("BAD: Request cookie did not override session cookie")
        return False
    
    # But the session cookie should remain unchanged
    if s.cookies['foo'] == 'session_value':
        print("GOOD: Session cookie was not modified")
        return True
    else:
        print("BUG: Session cookie was modified by request cookie!")
        return False

if __name__ == '__main__':
    print("Testing cookie persistence bug...")
    test1_result = test_cookie_persistence_bug()
    test2_result = test_session_cookie_override()
    
    if test1_result and test2_result:
        print("\nAll tests passed!")
    else:
        print("\nSome tests failed - bug confirmed!")
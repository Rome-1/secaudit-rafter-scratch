#!/usr/bin/env python
"""Comprehensive test to verify the cookie persistence fix."""

import requests

def test_comprehensive_cookie_behavior():
    """Test all aspects of cookie behavior after the fix."""
    
    print("=== Comprehensive Cookie Behavior Test ===")
    
    # Test 1: Request cookies should not be persisted to session
    print("\n1. Testing that request cookies are not persisted to session...")
    s = requests.Session()
    s.cookies['session_cookie'] = 'session_value'
    
    initial_cookies = dict(s.cookies)
    print(f"   Initial session cookies: {initial_cookies}")
    
    # Make request with additional cookies
    r = s.get('http://httpbin.org/cookies', cookies={'request_cookie': 'request_value'})
    
    final_cookies = dict(s.cookies)
    print(f"   Final session cookies: {final_cookies}")
    
    # Request cookie should not be in session
    assert 'request_cookie' not in s.cookies, "FAIL: Request cookie was persisted to session"
    assert s.cookies['session_cookie'] == 'session_value', "FAIL: Session cookie was modified"
    print("   ✓ PASS: Request cookies not persisted to session")
    
    # Test 2: Request cookies should override session cookies for the request
    print("\n2. Testing that request cookies override session cookies...")
    s = requests.Session()
    s.cookies['override_test'] = 'session_value'
    
    r = s.get('http://httpbin.org/cookies', cookies={'override_test': 'request_value'})
    received_cookies = r.json().get('cookies', {})
    
    print(f"   Cookies received by server: {received_cookies}")
    print(f"   Session cookies after request: {dict(s.cookies)}")
    
    # Server should have received the request cookie value
    assert received_cookies.get('override_test') == 'request_value', "FAIL: Request cookie did not override session cookie"
    # Session should still have original value
    assert s.cookies['override_test'] == 'session_value', "FAIL: Session cookie was modified"
    print("   ✓ PASS: Request cookies override session cookies correctly")
    
    # Test 3: Request cookies should persist through redirects
    print("\n3. Testing that request cookies persist through redirects...")
    s = requests.Session()
    s.cookies['session_redirect'] = 'session_value'
    
    # Make request to redirect endpoint with request cookies
    r = s.get('http://httpbin.org/redirect/1', cookies={'redirect_test': 'request_value'})
    
    print(f"   Final URL: {r.url}")
    print(f"   Final request headers: {dict(r.request.headers)}")
    print(f"   History length: {len(r.history)}")
    
    if r.history:
        print(f"   First request headers: {dict(r.history[0].request.headers)}")
    
    # Both requests should have the cookies
    assert 'Cookie' in r.request.headers, "FAIL: No cookies in final request"
    assert 'redirect_test=request_value' in r.request.headers['Cookie'], "FAIL: Request cookie missing in final request"
    assert 'session_redirect=session_value' in r.request.headers['Cookie'], "FAIL: Session cookie missing in final request"
    
    if r.history:
        assert 'Cookie' in r.history[0].request.headers, "FAIL: No cookies in first request"
        assert 'redirect_test=request_value' in r.history[0].request.headers['Cookie'], "FAIL: Request cookie missing in first request"
        assert 'session_redirect=session_value' in r.history[0].request.headers['Cookie'], "FAIL: Session cookie missing in first request"
    
    # Session should not have the request cookie
    assert 'redirect_test' not in s.cookies, "FAIL: Request cookie was persisted to session after redirect"
    assert s.cookies['session_redirect'] == 'session_value', "FAIL: Session cookie was modified after redirect"
    print("   ✓ PASS: Request cookies persist through redirects correctly")
    
    # Test 4: Server-sent cookies should still be persisted to session
    print("\n4. Testing that server-sent cookies are still persisted...")
    s = requests.Session()
    initial_count = len(s.cookies)
    
    # Make request to endpoint that sets a cookie
    r = s.get('http://httpbin.org/cookies/set?server_cookie=server_value')
    
    print(f"   Session cookies after server set cookie: {dict(s.cookies)}")
    
    # Server cookie should be in session
    assert 'server_cookie' in s.cookies, "FAIL: Server-sent cookie was not persisted to session"
    assert s.cookies['server_cookie'] == 'server_value', "FAIL: Server-sent cookie has wrong value"
    print("   ✓ PASS: Server-sent cookies are persisted correctly")
    
    print("\n=== All tests passed! Cookie behavior is correct. ===")
    return True

if __name__ == '__main__':
    try:
        test_comprehensive_cookie_behavior()
        print("\n🎉 SUCCESS: All cookie behavior tests passed!")
    except Exception as e:
        print(f"\n❌ FAILURE: {e}")
        import traceback
        traceback.print_exc()
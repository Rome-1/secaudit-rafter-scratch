#!/usr/bin/env python
"""Test edge cases for cookie behavior."""

import requests

def test_edge_cases():
    """Test edge cases for cookie behavior."""
    
    print("=== Testing Edge Cases ===")
    
    # Test 1: Empty cookies parameter
    print("\n1. Testing with empty cookies parameter...")
    s = requests.Session()
    s.cookies['session_cookie'] = 'session_value'
    
    r = s.get('http://httpbin.org/cookies', cookies={})
    assert dict(s.cookies) == {'session_cookie': 'session_value'}
    print("   ✓ PASS: Empty cookies parameter handled correctly")
    
    # Test 2: None cookies parameter
    print("\n2. Testing with None cookies parameter...")
    r = s.get('http://httpbin.org/cookies', cookies=None)
    assert dict(s.cookies) == {'session_cookie': 'session_value'}
    print("   ✓ PASS: None cookies parameter handled correctly")
    
    # Test 3: Multiple redirects with cookies
    print("\n3. Testing multiple redirects with cookies...")
    s = requests.Session()
    s.cookies['session_cookie'] = 'session_value'
    
    # Use multiple redirects
    r = s.get('http://httpbin.org/redirect/3', cookies={'request_cookie': 'request_value'})
    
    # Check that cookies are present in all requests
    assert 'Cookie' in r.request.headers
    assert 'request_cookie=request_value' in r.request.headers['Cookie']
    assert 'session_cookie=session_value' in r.request.headers['Cookie']
    
    # Check that request cookie is not persisted
    assert 'request_cookie' not in s.cookies
    assert s.cookies['session_cookie'] == 'session_value'
    print("   ✓ PASS: Multiple redirects with cookies handled correctly")
    
    # Test 4: CookieJar as cookies parameter
    print("\n4. Testing with CookieJar as cookies parameter...")
    from requests.cookies import RequestsCookieJar
    
    s = requests.Session()
    s.cookies['session_cookie'] = 'session_value'
    
    jar = RequestsCookieJar()
    jar['jar_cookie'] = 'jar_value'
    
    r = s.get('http://httpbin.org/cookies', cookies=jar)
    
    # Check that jar cookie was sent but not persisted
    received_cookies = r.json().get('cookies', {})
    assert 'jar_cookie' in received_cookies
    assert received_cookies['jar_cookie'] == 'jar_value'
    assert 'jar_cookie' not in s.cookies
    assert s.cookies['session_cookie'] == 'session_value'
    print("   ✓ PASS: CookieJar as cookies parameter handled correctly")
    
    print("\n=== All edge case tests passed! ===")
    return True

if __name__ == '__main__':
    try:
        test_edge_cases()
        print("\n🎉 SUCCESS: All edge case tests passed!")
    except Exception as e:
        print(f"\n❌ FAILURE: {e}")
        import traceback
        traceback.print_exc()
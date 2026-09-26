#!/usr/bin/env python3

"""
Demonstration script showing the improvement in CSRF cookie validation.

This script shows how malformed CSRF cookies are now rejected earlier
with specific error messages, rather than being silently replaced.
"""

import os
import sys
import django
from django.conf import settings
from django.http import HttpRequest
from django.middleware.csrf import CsrfViewMiddleware

# Configure Django settings
if not settings.configured:
    settings.configure(
        DEBUG=True,
        SECRET_KEY='test-secret-key',
        CSRF_COOKIE_NAME='csrftoken',
        CSRF_HEADER_NAME='HTTP_X_CSRFTOKEN',
        MIDDLEWARE=[
            'django.middleware.csrf.CsrfViewMiddleware',
        ],
        USE_TZ=True,
    )

django.setup()


class TestingHttpRequest(HttpRequest):
    """Custom HttpRequest for testing."""
    
    def __init__(self):
        super().__init__()
        self.META = {}
        self.method = 'POST'
        
    def is_secure(self):
        return False


def post_form_view(request):
    """Simple view for testing POST requests."""
    from django.http import HttpResponse
    return HttpResponse("OK")


def demonstrate_improvement():
    """Demonstrate the CSRF cookie validation improvement."""
    
    print("=== CSRF Cookie Validation Improvement Demonstration ===\n")
    
    # Test 1: Malformed cookie with invalid characters
    print("Test 1: CSRF cookie with invalid characters")
    print("-" * 50)
    
    req = TestingHttpRequest()
    req.COOKIES[settings.CSRF_COOKIE_NAME] = 'a' * 63 + '!'  # 64 chars with invalid char
    req.POST = {'csrfmiddlewaretoken': 'some-token'}
    
    mw = CsrfViewMiddleware(post_form_view)
    
    # process_request should handle the invalid cookie gracefully
    print("Calling process_request()...")
    mw.process_request(req)
    print(f"Request META['CSRF_COOKIE']: {req.META.get('CSRF_COOKIE', 'Not set')}")
    
    # process_view should reject the request due to malformed cookie
    print("Calling process_view()...")
    try:
        import logging
        logging.basicConfig(level=logging.WARNING)
        resp = mw.process_view(req, post_form_view, (), {})
        if resp:
            print(f"Request rejected with status: {resp.status_code}")
            print(f"Response content: {resp.content.decode()}")
        else:
            print("Request accepted (this shouldn't happen)")
    except Exception as e:
        print(f"Exception: {e}")
    
    print()
    
    # Test 2: Malformed cookie with incorrect length
    print("Test 2: CSRF cookie with incorrect length")
    print("-" * 50)
    
    req2 = TestingHttpRequest()
    req2.COOKIES[settings.CSRF_COOKIE_NAME] = 'short'  # Too short
    req2.POST = {'csrfmiddlewaretoken': 'some-token'}
    
    mw2 = CsrfViewMiddleware(post_form_view)
    
    # process_request should handle the invalid cookie gracefully
    print("Calling process_request()...")
    mw2.process_request(req2)
    print(f"Request META['CSRF_COOKIE']: {req2.META.get('CSRF_COOKIE', 'Not set')}")
    
    # process_view should reject the request due to malformed cookie
    print("Calling process_view()...")
    try:
        resp2 = mw2.process_view(req2, post_form_view, (), {})
        if resp2:
            print(f"Request rejected with status: {resp2.status_code}")
            print(f"Response content: {resp2.content.decode()}")
        else:
            print("Request accepted (this shouldn't happen)")
    except Exception as e:
        print(f"Exception: {e}")
    
    print()
    
    # Test 3: Valid cookie (should work)
    print("Test 3: Valid CSRF cookie")
    print("-" * 50)
    
    from django.middleware.csrf import _get_new_csrf_token
    valid_token = _get_new_csrf_token()
    
    req3 = TestingHttpRequest()
    req3.COOKIES[settings.CSRF_COOKIE_NAME] = valid_token
    req3.POST = {'csrfmiddlewaretoken': valid_token}
    
    mw3 = CsrfViewMiddleware(post_form_view)
    
    print("Calling process_request()...")
    mw3.process_request(req3)
    print(f"Request META['CSRF_COOKIE']: {req3.META.get('CSRF_COOKIE', 'Not set')[:20]}...")
    
    print("Calling process_view()...")
    try:
        resp3 = mw3.process_view(req3, post_form_view, (), {})
        if resp3:
            print(f"Request rejected with status: {resp3.status_code}")
        else:
            print("Request accepted successfully!")
    except Exception as e:
        print(f"Exception: {e}")
    
    print("\n=== Summary ===")
    print("Before this improvement:")
    print("- Malformed CSRF cookies were silently replaced with new tokens")
    print("- This led to unnecessary work and eventual token mismatch failures")
    print("- Error messages were generic ('CSRF token incorrect')")
    print()
    print("After this improvement:")
    print("- Malformed CSRF cookies are rejected immediately in process_view()")
    print("- Specific error messages indicate the exact problem")
    print("- No unnecessary token generation or comparison work")
    print("- Better security and easier debugging")


if __name__ == '__main__':
    demonstrate_improvement()
"""
Test to verify specific error messages for CSRF cookie vs token format errors.
"""
import os
import sys
import django
from django.conf import settings

# Configure Django settings
if not settings.configured:
    settings.configure(
        DEBUG=True,
        SECRET_KEY='test-secret-key',
        MIDDLEWARE=[
            'django.middleware.csrf.CsrfViewMiddleware',
        ],
        ROOT_URLCONF='',
        CSRF_COOKIE_NAME='csrftoken',
        CSRF_HEADER_NAME='HTTP_X_CSRFTOKEN',
        CSRF_USE_SESSIONS=False,
        CSRF_FAILURE_VIEW='django.views.csrf.csrf_failure',
        INSTALLED_APPS=[
            'django.contrib.contenttypes',
            'django.contrib.auth',
        ],
    )
    django.setup()

from django.http import HttpRequest, HttpResponse
from django.middleware.csrf import CsrfViewMiddleware, _get_new_csrf_token
from django.test import RequestFactory

def extract_reason(response):
    """Extract the reason from a CSRF failure response."""
    if response and hasattr(response, 'status_code') and response.status_code == 403:
        content = response.content.decode('utf-8')
        import re
        # Try to find the reason in the response
        match = re.search(r'Forbidden \((.*?)\)', content)
        if match:
            return match.group(1)
    return None

def test_error_messages():
    """Test that error messages distinguish between cookie and token format errors."""
    middleware = CsrfViewMiddleware(lambda req: HttpResponse("OK"))
    factory = RequestFactory()
    
    def dummy_view(request):
        return HttpResponse("OK")
    
    print("=" * 80)
    print("CSRF Cookie Format Error Messages")
    print("=" * 80)
    
    # Test 1: Invalid characters in cookie
    print("\n1. Cookie with invalid characters:")
    valid_token = _get_new_csrf_token()
    request = factory.post('/', {'csrfmiddlewaretoken': valid_token})
    request.COOKIES['csrftoken'] = 'invalid-chars-!@#$%'
    middleware.process_request(request)
    response = middleware.process_view(request, dummy_view, [], {})
    reason = extract_reason(response)
    print(f"   Reason: {reason}")
    assert reason == "CSRF cookie has invalid characters.", f"Expected 'CSRF cookie has invalid characters.' but got '{reason}'"
    
    # Test 2: Invalid length in cookie
    print("\n2. Cookie with incorrect length:")
    valid_token = _get_new_csrf_token()
    request = factory.post('/', {'csrfmiddlewaretoken': valid_token})
    request.COOKIES['csrftoken'] = 'tooshort'
    middleware.process_request(request)
    response = middleware.process_view(request, dummy_view, [], {})
    reason = extract_reason(response)
    print(f"   Reason: {reason}")
    assert reason == "CSRF cookie has incorrect length.", f"Expected 'CSRF cookie has incorrect length.' but got '{reason}'"
    
    print("\n" + "=" * 80)
    print("CSRF Token (non-cookie) Format Error Messages")
    print("=" * 80)
    
    # Test 3: Invalid characters in non-cookie token
    print("\n3. Non-cookie token with invalid characters:")
    valid_cookie = _get_new_csrf_token()
    request = factory.post('/', {'csrfmiddlewaretoken': 'invalid-token-!@#$'})
    request.COOKIES['csrftoken'] = valid_cookie
    middleware.process_request(request)
    response = middleware.process_view(request, dummy_view, [], {})
    reason = extract_reason(response)
    print(f"   Reason: {reason}")
    assert reason == "CSRF token has invalid characters.", f"Expected 'CSRF token has invalid characters.' but got '{reason}'"
    
    # Test 4: Invalid length in non-cookie token
    print("\n4. Non-cookie token with incorrect length:")
    valid_cookie = _get_new_csrf_token()
    request = factory.post('/', {'csrfmiddlewaretoken': 'short'})
    request.COOKIES['csrftoken'] = valid_cookie
    middleware.process_request(request)
    response = middleware.process_view(request, dummy_view, [], {})
    reason = extract_reason(response)
    print(f"   Reason: {reason}")
    assert reason == "CSRF token has incorrect length.", f"Expected 'CSRF token has incorrect length.' but got '{reason}'"
    
    print("\n" + "=" * 80)
    print("All tests passed! Error messages are specific and correct.")
    print("=" * 80)

if __name__ == '__main__':
    test_error_messages()

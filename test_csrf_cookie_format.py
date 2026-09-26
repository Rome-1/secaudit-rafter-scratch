"""
Test script to verify CSRF cookie format validation behavior.
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
        INSTALLED_APPS=[
            'django.contrib.contenttypes',
            'django.contrib.auth',
        ],
    )
    django.setup()

from django.http import HttpRequest, HttpResponse
from django.middleware.csrf import CsrfViewMiddleware
from django.test import RequestFactory

def test_invalid_cookie_format():
    """Test that invalid CSRF cookie format is handled correctly."""
    middleware = CsrfViewMiddleware(lambda req: HttpResponse("OK"))
    factory = RequestFactory()
    
    print("=" * 80)
    print("Test 1: Invalid characters in CSRF cookie (GET request)")
    print("=" * 80)
    request = factory.get('/')
    request.COOKIES['csrftoken'] = 'invalid-chars-!@#$%'
    request.META['CSRF_COOKIE_NAME'] = 'csrftoken'
    
    # Process request should handle invalid cookie
    middleware.process_request(request)
    print(f"After process_request:")
    print(f"  CSRF_COOKIE in META: {'CSRF_COOKIE' in request.META}")
    if 'CSRF_COOKIE' in request.META:
        print(f"  CSRF_COOKIE value length: {len(request.META['CSRF_COOKIE'])}")
    print(f"  csrf_cookie_needs_reset: {getattr(request, 'csrf_cookie_needs_reset', False)}")
    print()
    
    print("=" * 80)
    print("Test 2: Invalid length in CSRF cookie (GET request)")
    print("=" * 80)
    request = factory.get('/')
    request.COOKIES['csrftoken'] = 'tooshort'
    request.META['CSRF_COOKIE_NAME'] = 'csrftoken'
    
    middleware.process_request(request)
    print(f"After process_request:")
    print(f"  CSRF_COOKIE in META: {'CSRF_COOKIE' in request.META}")
    if 'CSRF_COOKIE' in request.META:
        print(f"  CSRF_COOKIE value length: {len(request.META['CSRF_COOKIE'])}")
    print(f"  csrf_cookie_needs_reset: {getattr(request, 'csrf_cookie_needs_reset', False)}")
    print()
    
    print("=" * 80)
    print("Test 3: Invalid characters in CSRF cookie (POST request)")
    print("=" * 80)
    request = factory.post('/', {'csrfmiddlewaretoken': 'a' * 64})
    request.COOKIES['csrftoken'] = 'invalid-chars-!@#$%'
    request.META['CSRF_COOKIE_NAME'] = 'csrftoken'
    
    middleware.process_request(request)
    print(f"After process_request:")
    print(f"  CSRF_COOKIE in META: {'CSRF_COOKIE' in request.META}")
    if 'CSRF_COOKIE' in request.META:
        print(f"  CSRF_COOKIE value length: {len(request.META['CSRF_COOKIE'])}")
    
    # Mock callback
    def dummy_view(request):
        return HttpResponse("OK")
    
    response = middleware.process_view(request, dummy_view, [], {})
    print(f"After process_view:")
    print(f"  Response type: {type(response).__name__}")
    if response is not None and hasattr(response, 'status_code'):
        print(f"  Status code: {response.status_code}")
        if hasattr(response, 'content'):
            content = response.content.decode('utf-8')
            if 'Forbidden' in content:
                # Extract reason from content
                import re
                match = re.search(r'Forbidden \((.*?)\)', content)
                if match:
                    print(f"  Reason: {match.group(1)}")
    print()
    
    print("=" * 80)
    print("Test 4: Valid 64-char CSRF cookie (POST request)")
    print("=" * 80)
    valid_token = 'a' * 64
    request = factory.post('/', {'csrfmiddlewaretoken': valid_token})
    request.COOKIES['csrftoken'] = valid_token
    request.META['CSRF_COOKIE_NAME'] = 'csrftoken'
    
    middleware.process_request(request)
    response = middleware.process_view(request, dummy_view, [], {})
    print(f"After process_view:")
    print(f"  Response: {response}")
    print()

if __name__ == '__main__':
    test_invalid_cookie_format()

"""
Comprehensive test script to verify CSRF cookie format validation behavior.
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
from django.middleware.csrf import CsrfViewMiddleware, _get_new_csrf_token
from django.test import RequestFactory

def test_csrf_scenarios():
    """Test various CSRF cookie format scenarios."""
    middleware = CsrfViewMiddleware(lambda req: HttpResponse("OK"))
    factory = RequestFactory()
    
    def dummy_view(request):
        return HttpResponse("OK")
    
    print("=" * 80)
    print("Test 1: POST with invalid characters in CSRF cookie")
    print("=" * 80)
    valid_token = _get_new_csrf_token()
    request = factory.post('/', {'csrfmiddlewaretoken': valid_token})
    request.COOKIES['csrftoken'] = 'invalid-chars-!@#$%'
    
    middleware.process_request(request)
    response = middleware.process_view(request, dummy_view, [], {})
    
    if response and hasattr(response, 'status_code'):
        print(f"Status: {response.status_code}")
        content = response.content.decode('utf-8')
        import re
        match = re.search(r'Forbidden \((.*?)\)', content)
        if match:
            print(f"Reason: {match.group(1)}")
    print()
    
    print("=" * 80)
    print("Test 2: POST with incorrect length CSRF cookie")
    print("=" * 80)
    valid_token = _get_new_csrf_token()
    request = factory.post('/', {'csrfmiddlewaretoken': valid_token})
    request.COOKIES['csrftoken'] = 'tooshort'
    
    middleware.process_request(request)
    response = middleware.process_view(request, dummy_view, [], {})
    
    if response and hasattr(response, 'status_code'):
        print(f"Status: {response.status_code}")
        content = response.content.decode('utf-8')
        import re
        match = re.search(r'Forbidden \((.*?)\)', content)
        if match:
            print(f"Reason: {match.group(1)}")
    print()
    
    print("=" * 80)
    print("Test 3: POST with valid cookie but invalid non-cookie token (invalid chars)")
    print("=" * 80)
    valid_cookie = _get_new_csrf_token()
    request = factory.post('/', {'csrfmiddlewaretoken': 'invalid-token-!@#$'})
    request.COOKIES['csrftoken'] = valid_cookie
    
    middleware.process_request(request)
    response = middleware.process_view(request, dummy_view, [], {})
    
    if response and hasattr(response, 'status_code'):
        print(f"Status: {response.status_code}")
        content = response.content.decode('utf-8')
        import re
        match = re.search(r'Forbidden \((.*?)\)', content)
        if match:
            print(f"Reason: {match.group(1)}")
    print()
    
    print("=" * 80)
    print("Test 4: POST with valid cookie but invalid non-cookie token (wrong length)")
    print("=" * 80)
    valid_cookie = _get_new_csrf_token()
    request = factory.post('/', {'csrfmiddlewaretoken': 'short'})
    request.COOKIES['csrftoken'] = valid_cookie
    
    middleware.process_request(request)
    response = middleware.process_view(request, dummy_view, [], {})
    
    if response and hasattr(response, 'status_code'):
        print(f"Status: {response.status_code}")
        content = response.content.decode('utf-8')
        import re
        match = re.search(r'Forbidden \((.*?)\)', content)
        if match:
            print(f"Reason: {match.group(1)}")
    print()
    
    print("=" * 80)
    print("Test 5: GET with invalid cookie characters")
    print("=" * 80)
    request = factory.get('/')
    request.COOKIES['csrftoken'] = 'invalid-chars-!@#$%'
    
    middleware.process_request(request)
    print(f"CSRF_COOKIE set: {'CSRF_COOKIE' in request.META}")
    print(f"csrf_cookie_needs_reset: {getattr(request, 'csrf_cookie_needs_reset', False)}")
    if 'CSRF_COOKIE' in request.META:
        print(f"New token length: {len(request.META['CSRF_COOKIE'])}")
    print()
    
    print("=" * 80)
    print("Test 6: GET with invalid cookie length")
    print("=" * 80)
    request = factory.get('/')
    request.COOKIES['csrftoken'] = 'short'
    
    middleware.process_request(request)
    print(f"CSRF_COOKIE set: {'CSRF_COOKIE' in request.META}")
    print(f"csrf_cookie_needs_reset: {getattr(request, 'csrf_cookie_needs_reset', False)}")
    if 'CSRF_COOKIE' in request.META:
        print(f"New token length: {len(request.META['CSRF_COOKIE'])}")
    print()
    
    print("=" * 80)
    print("Test 7: POST with valid matching tokens (should succeed)")
    print("=" * 80)
    valid_token = _get_new_csrf_token()
    request = factory.post('/', {'csrfmiddlewaretoken': valid_token})
    request.COOKIES['csrftoken'] = valid_token
    
    middleware.process_request(request)
    response = middleware.process_view(request, dummy_view, [], {})
    
    print(f"Response: {response}")
    print(f"Success: {response is None}")
    print()
    
    print("=" * 80)
    print("Test 8: POST with 32-char cookie (backward compatibility)")
    print("=" * 80)
    # 32-char tokens are treated as unmasked secrets
    old_style_token = 'a' * 32
    request = factory.post('/', {'csrfmiddlewaretoken': old_style_token})
    request.COOKIES['csrftoken'] = old_style_token
    
    middleware.process_request(request)
    response = middleware.process_view(request, dummy_view, [], {})
    
    if response and hasattr(response, 'status_code'):
        print(f"Status: {response.status_code}")
        content = response.content.decode('utf-8')
        import re
        match = re.search(r'Forbidden \((.*?)\)', content)
        if match:
            print(f"Reason: {match.group(1)}")
    else:
        print(f"Response: {response}")
        print(f"Success: {response is None}")
    print()

if __name__ == '__main__':
    test_csrf_scenarios()

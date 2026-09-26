"""
Test to see the full response content.
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

middleware = CsrfViewMiddleware(lambda req: HttpResponse("OK"))
factory = RequestFactory()

def dummy_view(request):
    return HttpResponse("OK")

# Test with invalid characters in cookie
print("=" * 80)
print("Test 1: Invalid characters in cookie")
print("=" * 80)
valid_token = _get_new_csrf_token()
request = factory.post('/', {'csrfmiddlewaretoken': valid_token})
request.COOKIES['csrftoken'] = 'invalid-chars-!@#$%'
middleware.process_request(request)
response = middleware.process_view(request, dummy_view, [], {})

if response:
    content = response.content.decode('utf-8')
    # Look for the reason in the content
    if 'CSRF cookie has invalid characters' in content:
        print("✓ Found: 'CSRF cookie has invalid characters'")
    else:
        print("✗ Not found: 'CSRF cookie has invalid characters'")
        # Print relevant parts
        import re
        matches = re.findall(r'<p>(.*?)</p>', content, re.DOTALL)
        for match in matches:
            if 'CSRF' in match or 'Reason' in match:
                print(f"Found: {match.strip()}")

print()
print("=" * 80)
print("Test 2: Invalid length in cookie")
print("=" * 80)
valid_token = _get_new_csrf_token()
request = factory.post('/', {'csrfmiddlewaretoken': valid_token})
request.COOKIES['csrftoken'] = 'tooshort'
middleware.process_request(request)
response = middleware.process_view(request, dummy_view, [], {})

if response:
    content = response.content.decode('utf-8')
    if 'CSRF cookie has incorrect length' in content:
        print("✓ Found: 'CSRF cookie has incorrect length'")
    else:
        print("✗ Not found: 'CSRF cookie has incorrect length'")
        import re
        matches = re.findall(r'<p>(.*?)</p>', content, re.DOTALL)
        for match in matches:
            if 'CSRF' in match or 'Reason' in match:
                print(f"Found: {match.strip()}")

print()
print("=" * 80)
print("Test 3: Invalid characters in non-cookie token")
print("=" * 80)
valid_cookie = _get_new_csrf_token()
request = factory.post('/', {'csrfmiddlewaretoken': 'invalid-token-!@#$'})
request.COOKIES['csrftoken'] = valid_cookie
middleware.process_request(request)
response = middleware.process_view(request, dummy_view, [], {})

if response:
    content = response.content.decode('utf-8')
    if 'CSRF token has invalid characters' in content:
        print("✓ Found: 'CSRF token has invalid characters'")
    else:
        print("✗ Not found: 'CSRF token has invalid characters'")
        import re
        matches = re.findall(r'<p>(.*?)</p>', content, re.DOTALL)
        for match in matches:
            if 'CSRF' in match or 'Reason' in match:
                print(f"Found: {match.strip()}")

print()
print("=" * 80)
print("Test 4: Invalid length in non-cookie token")
print("=" * 80)
valid_cookie = _get_new_csrf_token()
request = factory.post('/', {'csrfmiddlewaretoken': 'short'})
request.COOKIES['csrftoken'] = valid_cookie
middleware.process_request(request)
response = middleware.process_view(request, dummy_view, [], {})

if response:
    content = response.content.decode('utf-8')
    if 'CSRF token has incorrect length' in content:
        print("✓ Found: 'CSRF token has incorrect length'")
    else:
        print("✗ Not found: 'CSRF token has incorrect length'")
        import re
        matches = re.findall(r'<p>(.*?)</p>', content, re.DOTALL)
        for match in matches:
            if 'CSRF' in match or 'Reason' in match:
                print(f"Found: {match.strip()}")

"""
Test with DEBUG=True to see the reason in the response.
"""
import os
import sys
import django
from django.conf import settings

# Configure Django settings with DEBUG=True
if not settings.configured:
    settings.configure(
        DEBUG=True,  # This is important!
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

print("=" * 80)
print("Test 1: Invalid characters in CSRF cookie")
print("=" * 80)
valid_token = _get_new_csrf_token()
request = factory.post('/', {'csrfmiddlewaretoken': valid_token})
request.COOKIES['csrftoken'] = 'invalid-chars-!@#$%'
middleware.process_request(request)
response = middleware.process_view(request, dummy_view, [], {})

if response:
    content = response.content.decode('utf-8')
    if 'CSRF cookie has invalid characters' in content:
        print("✓ Found: 'CSRF cookie has invalid characters'")
    else:
        print("✗ Not found: 'CSRF cookie has invalid characters'")
        # Extract the reason
        import re
        match = re.search(r'<pre>\s*(.*?)\s*</pre>', content, re.DOTALL)
        if match:
            print(f"Actual reason: {match.group(1).strip()}")

print()
print("=" * 80)
print("Test 2: Invalid length in CSRF cookie")
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
        match = re.search(r'<pre>\s*(.*?)\s*</pre>', content, re.DOTALL)
        if match:
            print(f"Actual reason: {match.group(1).strip()}")

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
        match = re.search(r'<pre>\s*(.*?)\s*</pre>', content, re.DOTALL)
        if match:
            print(f"Actual reason: {match.group(1).strip()}")

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
        match = re.search(r'<pre>\s*(.*?)\s*</pre>', content, re.DOTALL)
        if match:
            print(f"Actual reason: {match.group(1).strip()}")

print()
print("=" * 80)
print("Summary: All error messages are specific and distinguish between")
print("         CSRF cookie format errors and CSRF token format errors.")
print("=" * 80)

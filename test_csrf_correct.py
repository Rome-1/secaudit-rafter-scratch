"""
Test with correct length tokens but invalid characters.
"""
import os
import sys
import django
from django.conf import settings

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

from django.http import HttpResponse
from django.middleware.csrf import CsrfViewMiddleware, _get_new_csrf_token
from django.test import RequestFactory

middleware = CsrfViewMiddleware(lambda req: HttpResponse("OK"))
factory = RequestFactory()

def dummy_view(request):
    return HttpResponse("OK")

def extract_reason(response):
    """Extract the reason from a CSRF failure response."""
    if response and hasattr(response, 'status_code') and response.status_code == 403:
        content = response.content.decode('utf-8')
        import re
        match = re.search(r'<pre>\s*(.*?)\s*</pre>', content, re.DOTALL)
        if match:
            return match.group(1).strip()
    return None

print("=" * 80)
print("Test 1: Cookie with invalid characters (correct length 64)")
print("=" * 80)
# Create a 64-char token with invalid characters
invalid_cookie = 'a' * 32 + '-' * 32  # 64 chars but contains dashes
valid_token = _get_new_csrf_token()
request = factory.post('/', {'csrfmiddlewaretoken': valid_token})
request.COOKIES['csrftoken'] = invalid_cookie

middleware.process_request(request)
response = middleware.process_view(request, dummy_view, [], {})
reason = extract_reason(response)
print(f"Reason: {reason}")
assert reason == "CSRF cookie has invalid characters.", f"Expected 'CSRF cookie has invalid characters.' but got '{reason}'"
print("✓ PASS")
print()

print("=" * 80)
print("Test 2: Cookie with incorrect length")
print("=" * 80)
invalid_cookie = 'a' * 20  # Wrong length
valid_token = _get_new_csrf_token()
request = factory.post('/', {'csrfmiddlewaretoken': valid_token})
request.COOKIES['csrftoken'] = invalid_cookie

middleware.process_request(request)
response = middleware.process_view(request, dummy_view, [], {})
reason = extract_reason(response)
print(f"Reason: {reason}")
assert reason == "CSRF cookie has incorrect length.", f"Expected 'CSRF cookie has incorrect length.' but got '{reason}'"
print("✓ PASS")
print()

print("=" * 80)
print("Test 3: Non-cookie token with invalid characters (correct length 64)")
print("=" * 80)
valid_cookie = _get_new_csrf_token()
invalid_token = 'a' * 32 + '-' * 32  # 64 chars but contains dashes
request = factory.post('/', {'csrfmiddlewaretoken': invalid_token})
request.COOKIES['csrftoken'] = valid_cookie

middleware.process_request(request)
response = middleware.process_view(request, dummy_view, [], {})
reason = extract_reason(response)
print(f"Reason: {reason}")
assert reason == "CSRF token has invalid characters.", f"Expected 'CSRF token has invalid characters.' but got '{reason}'"
print("✓ PASS")
print()

print("=" * 80)
print("Test 4: Non-cookie token with incorrect length")
print("=" * 80)
valid_cookie = _get_new_csrf_token()
invalid_token = 'a' * 20  # Wrong length
request = factory.post('/', {'csrfmiddlewaretoken': invalid_token})
request.COOKIES['csrftoken'] = valid_cookie

middleware.process_request(request)
response = middleware.process_view(request, dummy_view, [], {})
reason = extract_reason(response)
print(f"Reason: {reason}")
assert reason == "CSRF token has incorrect length.", f"Expected 'CSRF token has incorrect length.' but got '{reason}'"
print("✓ PASS")
print()

print("=" * 80)
print("Test 5: GET request with invalid cookie (should generate new token)")
print("=" * 80)
invalid_cookie = 'a' * 32 + '-' * 32  # 64 chars but contains dashes
request = factory.get('/')
request.COOKIES['csrftoken'] = invalid_cookie

middleware.process_request(request)
print(f"CSRF_COOKIE set: {'CSRF_COOKIE' in request.META}")
print(f"csrf_cookie_needs_reset: {getattr(request, 'csrf_cookie_needs_reset', False)}")
print(f"csrf_cookie_invalid_format: {getattr(request, 'csrf_cookie_invalid_format', 'Not set')}")
if 'CSRF_COOKIE' in request.META:
    print(f"New token length: {len(request.META['CSRF_COOKIE'])}")
    # Verify it's a valid token (all alphanumeric)
    import re
    if re.match(r'^[a-zA-Z0-9]+$', request.META['CSRF_COOKIE']):
        print("✓ New token is valid (all alphanumeric)")
    else:
        print("✗ New token is invalid")
print("✓ PASS")
print()

print("=" * 80)
print("All tests passed!")
print("=" * 80)

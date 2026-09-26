"""
Trace the flow to understand what's happening.
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

# Monkey-patch to trace calls
original_get_token = CsrfViewMiddleware._get_token

def traced_get_token(self, request):
    print(f"  _get_token called")
    print(f"    CSRF_COOKIE in META: {'CSRF_COOKIE' in request.META}")
    if 'CSRF_COOKIE' in request.META:
        print(f"    CSRF_COOKIE value: {request.META['CSRF_COOKIE'][:20]}...")
    print(f"    Cookie in request.COOKIES: {settings.CSRF_COOKIE_NAME in request.COOKIES}")
    if settings.CSRF_COOKIE_NAME in request.COOKIES:
        print(f"    Cookie value: {request.COOKIES[settings.CSRF_COOKIE_NAME]}")
    try:
        result = original_get_token(self, request)
        print(f"    Returned: {result[:20] if result else None}...")
        return result
    except Exception as e:
        print(f"    Exception: {type(e).__name__}: {e}")
        raise

CsrfViewMiddleware._get_token = traced_get_token

middleware = CsrfViewMiddleware(lambda req: HttpResponse("OK"))
factory = RequestFactory()

def dummy_view(request):
    return HttpResponse("OK")

print("=" * 80)
print("Test: Invalid characters in CSRF cookie")
print("=" * 80)
valid_token = _get_new_csrf_token()
request = factory.post('/', {'csrfmiddlewaretoken': valid_token})
request.COOKIES['csrftoken'] = 'invalid-chars-!@#$%'

print("\nCalling process_request:")
middleware.process_request(request)
print(f"\nAfter process_request:")
print(f"  CSRF_COOKIE in META: {'CSRF_COOKIE' in request.META}")
if 'CSRF_COOKIE' in request.META:
    print(f"  CSRF_COOKIE value: {request.META['CSRF_COOKIE'][:20]}...")

print("\nCalling process_view:")
response = middleware.process_view(request, dummy_view, [], {})
print(f"\nAfter process_view:")
print(f"  Response: {type(response).__name__ if response else None}")

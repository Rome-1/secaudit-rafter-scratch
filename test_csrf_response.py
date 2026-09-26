"""
Test to see what the actual response looks like.
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
print("Testing with invalid characters in cookie...")
valid_token = _get_new_csrf_token()
request = factory.post('/', {'csrfmiddlewaretoken': valid_token})
request.COOKIES['csrftoken'] = 'invalid-chars-!@#$%'
middleware.process_request(request)
response = middleware.process_view(request, dummy_view, [], {})

print(f"Response type: {type(response)}")
print(f"Response status: {response.status_code if response else 'None'}")
if response:
    print(f"Response content type: {response.get('Content-Type', 'Not set')}")
    print(f"Response content length: {len(response.content)}")
    print(f"Response content (first 500 chars):\n{response.content[:500]}")

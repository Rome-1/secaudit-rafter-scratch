"""
Test that session-based CSRF still works correctly.
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
            'django.contrib.sessions.middleware.SessionMiddleware',
            'django.middleware.csrf.CsrfViewMiddleware',
        ],
        ROOT_URLCONF='',
        CSRF_USE_SESSIONS=True,
        SESSION_ENGINE='django.contrib.sessions.backends.db',
        INSTALLED_APPS=[
            'django.contrib.contenttypes',
            'django.contrib.auth',
            'django.contrib.sessions',
        ],
        DATABASES={
            'default': {
                'ENGINE': 'django.db.backends.sqlite3',
                'NAME': ':memory:',
            }
        },
    )
    django.setup()

from django.core.management import call_command
call_command('migrate', '--run-syncdb', verbosity=0)

from django.http import HttpResponse
from django.middleware.csrf import CsrfViewMiddleware, get_token
from django.test import RequestFactory
from django.contrib.sessions.middleware import SessionMiddleware

def test_session_csrf():
    """Test that session-based CSRF works correctly."""
    
    def get_response(request):
        return HttpResponse("OK")
    
    session_middleware = SessionMiddleware(get_response)
    csrf_middleware = CsrfViewMiddleware(get_response)
    factory = RequestFactory()
    
    def dummy_view(request):
        return HttpResponse("OK")
    
    print("=" * 80)
    print("Test: Session-based CSRF")
    print("=" * 80)
    print()
    
    # Test 1: GET request - get a token
    print("1. GET request to obtain CSRF token:")
    request = factory.get('/')
    session_middleware.process_request(request)
    csrf_middleware.process_request(request)
    
    # Use get_token to generate a token (this is what templates do)
    token = get_token(request)
    print(f"   ✓ Token generated: {token[:20]}...")
    print()
    
    # Test 2: POST with valid token
    print("2. POST request with valid token:")
    request = factory.post('/', {'csrfmiddlewaretoken': token})
    session_middleware.process_request(request)
    
    # Manually set the session token (simulating a real session)
    request.session['_csrftoken'] = token
    
    csrf_middleware.process_request(request)
    response = csrf_middleware.process_view(request, dummy_view, [], {})
    
    assert response is None, f"Should accept valid request, got: {response}"
    print(f"   ✓ Valid request accepted")
    print()
    
    print("=" * 80)
    print("✓ Session-based CSRF works correctly!")
    print("=" * 80)

if __name__ == '__main__':
    test_session_csrf()

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
        CSRF_USE_SESSIONS=True,  # Use session-based CSRF
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

# Create tables
from django.core.management import call_command
call_command('migrate', '--run-syncdb', verbosity=0)

from django.http import HttpResponse
from django.middleware.csrf import CsrfViewMiddleware, _get_new_csrf_token
from django.test import RequestFactory
from django.contrib.sessions.middleware import SessionMiddleware

def test_session_csrf():
    """Test that session-based CSRF works correctly."""
    
    # Create middleware stack
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
    
    # Test 1: GET request with session-based CSRF
    print("1. GET request with session-based CSRF:")
    request = factory.get('/')
    
    # Process through session middleware first
    session_middleware.process_request(request)
    
    # Process through CSRF middleware
    csrf_middleware.process_request(request)
    
    assert 'CSRF_COOKIE' in request.META, "Should set CSRF_COOKIE in META"
    print(f"   ✓ CSRF token set in META")
    print()
    
    # Test 2: POST request with session-based CSRF
    print("2. POST request with valid session-based CSRF:")
    request = factory.post('/', {'csrfmiddlewaretoken': request.META['CSRF_COOKIE']})
    
    # Process through session middleware
    session_middleware.process_request(request)
    
    # Set the CSRF token in session (simulating what would happen in a real request)
    request.session['_csrftoken'] = request.META.get('CSRF_COOKIE', _get_new_csrf_token())
    
    # Process through CSRF middleware
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

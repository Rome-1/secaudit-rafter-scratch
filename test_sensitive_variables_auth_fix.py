#!/usr/bin/env python3

"""
Test to verify that the sensitive_variables decorator fix resolves the
authentication backend issue described in the problem statement.
"""

import os
import django
from django.conf import settings

# Configure Django settings
if not settings.configured:
    settings.configure(
        DEBUG=True,
        DATABASES={
            'default': {
                'ENGINE': 'django.db.backends.sqlite3',
                'NAME': ':memory:',
            }
        },
        INSTALLED_APPS=[
            'django.contrib.auth',
            'django.contrib.contenttypes',
        ],
        SECRET_KEY='test-secret-key',
    )
    django.setup()

import inspect
from django.contrib.auth import authenticate
from django.contrib.auth.backends import BaseBackend
from django.views.decorators.debug import sensitive_variables
from django.test import TestCase, override_settings
from django.contrib.auth.models import User


class TestBackendWithSensitiveVariables(BaseBackend):
    """
    Custom authentication backend with sensitive_variables decorator.
    This should work correctly after the fix.
    """
    
    @sensitive_variables('password')
    def authenticate(self, request, username=None, password=None):
        if username == "testuser" and password == "testpass":
            # In a real backend, you'd return a User object
            # For this test, we'll just return a simple dict
            return {"username": username}
        return None


class TestBackendWithoutDecorator(BaseBackend):
    """
    Control backend without sensitive_variables decorator.
    """
    
    def authenticate(self, request, username=None, password=None):
        if username == "testuser2" and password == "testpass2":
            return {"username": username}
        return None


class TestBackendWithDifferentSignature(BaseBackend):
    """
    Backend with different signature that should be skipped for username/password.
    """
    
    @sensitive_variables('token')
    def authenticate(self, request, token=None):
        if token == "valid_token":
            return {"token": token}
        return None


def test_inspect_getcallargs_with_sensitive_variables():
    """
    Test that inspect.getcallargs works correctly with sensitive_variables decorated methods.
    This is the core issue that was causing problems.
    """
    print("=== Testing inspect.getcallargs with sensitive_variables ===")
    
    backend1 = TestBackendWithSensitiveVariables()
    backend2 = TestBackendWithoutDecorator()
    backend3 = TestBackendWithDifferentSignature()
    
    # Test credentials that should match backend1 and backend2
    credentials = {"username": "testuser", "password": "testpass"}
    
    print(f"Testing credentials: {credentials}")
    
    # Test backend1 (with @sensitive_variables)
    print("\nBackend with @sensitive_variables:")
    try:
        result = inspect.getcallargs(backend1.authenticate, None, **credentials)
        print(f"  SUCCESS: getcallargs worked: {result}")
    except TypeError as e:
        print(f"  ERROR: getcallargs failed: {e}")
    
    # Test backend2 (without decorator)
    print("\nBackend without decorator:")
    try:
        result = inspect.getcallargs(backend2.authenticate, None, **credentials)
        print(f"  SUCCESS: getcallargs worked: {result}")
    except TypeError as e:
        print(f"  ERROR: getcallargs failed: {e}")
    
    # Test backend3 (different signature, should fail)
    print("\nBackend with different signature:")
    try:
        result = inspect.getcallargs(backend3.authenticate, None, **credentials)
        print(f"  ERROR: getcallargs should have failed but didn't: {result}")
    except TypeError as e:
        print(f"  SUCCESS: getcallargs correctly failed: {e}")


def test_authentication_flow():
    """
    Test that the authentication flow works correctly with multiple backends
    including ones with sensitive_variables decorators.
    """
    print("\n=== Testing authentication flow ===")
    
    backends = [
        TestBackendWithSensitiveVariables(),
        TestBackendWithoutDecorator(),
        TestBackendWithDifferentSignature(),
    ]
    
    credentials = {"username": "testuser", "password": "testpass"}
    
    print(f"Testing authentication with credentials: {credentials}")
    
    # Simulate Django's authenticate function logic
    for i, backend in enumerate(backends):
        backend_name = f"Backend{i+1}"
        print(f"\nTrying {backend_name}:")
        
        try:
            # This is the critical line from Django's authenticate function
            inspect.getcallargs(backend.authenticate, None, **credentials)
            print(f"  Signature matches, proceeding to authenticate")
            
            try:
                user = backend.authenticate(None, **credentials)
                if user is not None:
                    print(f"  SUCCESS: Authentication successful: {user}")
                    break
                else:
                    print(f"  Authentication failed (invalid credentials)")
            except Exception as e:
                print(f"  ERROR: Authentication raised exception: {e}")
                
        except TypeError as e:
            print(f"  Signature doesn't match, skipping: {e}")
            continue
    else:
        print("  No backend could authenticate the user")


if __name__ == "__main__":
    test_inspect_getcallargs_with_sensitive_variables()
    test_authentication_flow()
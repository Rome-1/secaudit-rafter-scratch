#!/usr/bin/env python3

"""
Regression test for the sensitive_variables decorator signature preservation issue.

This test demonstrates that the issue described in the problem statement is fixed:
- Before the fix: inspect.getcallargs would always match decorated functions
- After the fix: inspect.getcallargs correctly validates function signatures
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
        AUTHENTICATION_BACKENDS=[
            '__main__.CustomBackend1',
            '__main__.CustomBackend2',
            '__main__.CustomBackend3',
        ]
    )
    django.setup()

import inspect
from django.contrib.auth import authenticate
from django.contrib.auth.backends import BaseBackend
from django.views.decorators.debug import sensitive_variables
from django.contrib.auth.models import User


class CustomBackend1(BaseBackend):
    """Backend that accepts username/password without decorator"""
    
    def authenticate(self, request, username=None, password=None):
        if username == "user1" and password == "pass1":
            # Return a mock user-like object
            return type('User', (), {'username': username, 'backend': self.__class__.__module__ + '.' + self.__class__.__name__})()
        return None


class CustomBackend2(BaseBackend):
    """Backend that accepts username/password WITH sensitive_variables decorator"""
    
    @sensitive_variables('password')
    def authenticate(self, request, username=None, password=None):
        if username == "user2" and password == "pass2":
            # Return a mock user-like object
            return type('User', (), {'username': username, 'backend': self.__class__.__module__ + '.' + self.__class__.__name__})()
        return None


class CustomBackend3(BaseBackend):
    """Backend that accepts different parameters (token-based)"""
    
    @sensitive_variables('token')
    def authenticate(self, request, token=None):
        if token == "valid_token":
            # Return a mock user-like object
            return type('User', (), {'token': token, 'backend': self.__class__.__module__ + '.' + self.__class__.__name__})()
        return None


def test_inspect_getcallargs_behavior():
    """
    Test that inspect.getcallargs behaves correctly with sensitive_variables decorator.
    This is the core issue that was causing authentication problems.
    """
    print("=== Testing inspect.getcallargs behavior ===")
    
    backends = [
        ("CustomBackend1 (no decorator)", CustomBackend1()),
        ("CustomBackend2 (@sensitive_variables)", CustomBackend2()),
        ("CustomBackend3 (@sensitive_variables, different signature)", CustomBackend3()),
    ]
    
    test_cases = [
        ("username/password credentials", {"username": "test", "password": "secret"}),
        ("token credentials", {"token": "test_token"}),
        ("invalid credentials", {"invalid_param": "value"}),
    ]
    
    for backend_name, backend in backends:
        print(f"\n{backend_name}:")
        
        for case_name, credentials in test_cases:
            print(f"  Testing {case_name}: {credentials}")
            try:
                result = inspect.getcallargs(backend.authenticate, None, **credentials)
                print(f"    ACCEPTED: {list(result.keys())}")
            except TypeError as e:
                print(f"    REJECTED: {e}")


def test_authentication_flow():
    """
    Test the complete authentication flow to ensure it works correctly.
    This simulates Django's authenticate() function behavior.
    """
    print("\n=== Testing authentication flow ===")
    
    # Test cases with different credential types
    test_cases = [
        ("Valid user1 credentials", {"username": "user1", "password": "pass1"}),
        ("Valid user2 credentials", {"username": "user2", "password": "pass2"}),
        ("Valid token credentials", {"token": "valid_token"}),
        ("Invalid username/password", {"username": "invalid", "password": "invalid"}),
        ("Invalid token", {"token": "invalid_token"}),
    ]
    
    for case_name, credentials in test_cases:
        print(f"\n{case_name}: {credentials}")
        
        # Simulate Django's authenticate function logic
        backends = [CustomBackend1(), CustomBackend2(), CustomBackend3()]
        user = None
        
        for i, backend in enumerate(backends):
            backend_name = f"Backend{i+1}"
            try:
                # This is the critical line that was broken before the fix
                inspect.getcallargs(backend.authenticate, None, **credentials)
                print(f"  {backend_name}: Signature matches, trying authentication...")
                
                try:
                    user = backend.authenticate(None, **credentials)
                    if user is not None:
                        print(f"  {backend_name}: SUCCESS - User authenticated: {user.username if hasattr(user, 'username') else user.token}")
                        break
                    else:
                        print(f"  {backend_name}: - Authentication failed (wrong credentials)")
                except Exception as e:
                    print(f"  {backend_name}: ERROR during authentication: {e}")
                    
            except TypeError as e:
                print(f"  {backend_name}: - Signature mismatch, skipping")
                continue
        
        if user is None:
            print(f"  RESULT: No backend could authenticate these credentials")
        else:
            print(f"  RESULT: Successfully authenticated by {user.backend}")


def test_regression_demonstration():
    """
    Demonstrate that the regression issue is fixed.
    Before the fix, decorated backends would always match any credentials.
    """
    print("\n=== Regression test: Demonstrating the fix ===")
    
    backend = CustomBackend2()  # Backend with @sensitive_variables
    
    # These credentials should NOT match the backend signature
    invalid_credentials = {"token": "some_token", "invalid_param": "value"}
    
    print(f"Testing backend with @sensitive_variables decorator")
    print(f"Backend signature: authenticate(self, request, username=None, password=None)")
    print(f"Invalid credentials: {invalid_credentials}")
    
    try:
        result = inspect.getcallargs(backend.authenticate, None, **invalid_credentials)
        print(f"ERROR: getcallargs should have failed but returned: {result}")
        print("This would indicate the bug is NOT fixed!")
    except TypeError as e:
        print(f"SUCCESS: getcallargs correctly rejected invalid credentials: {e}")
        print("This confirms the bug is FIXED!")


if __name__ == "__main__":
    test_inspect_getcallargs_behavior()
    test_authentication_flow()
    test_regression_demonstration()
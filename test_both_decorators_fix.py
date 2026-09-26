#!/usr/bin/env python3

"""
Test both sensitive_variables and sensitive_post_parameters decorators
to ensure they both preserve function signatures correctly.
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
from django.views.decorators.debug import sensitive_variables, sensitive_post_parameters
from django.http import HttpRequest


def test_function(request, username, password):
    """Test function with specific signature"""
    return f"authenticated {username}"

@sensitive_variables('password')
def decorated_with_sensitive_variables(request, username, password):
    """Test function decorated with sensitive_variables"""
    return f"authenticated {username}"

@sensitive_post_parameters('password')
def decorated_with_sensitive_post_parameters(request, username, password):
    """Test function decorated with sensitive_post_parameters"""
    return f"authenticated {username}"

@sensitive_variables('password')
@sensitive_post_parameters('password')
def decorated_with_both(request, username, password):
    """Test function decorated with both decorators"""
    return f"authenticated {username}"


def test_signature_preservation():
    """Test if both decorators preserve function signatures"""
    
    print("=== Testing signature preservation for both decorators ===")
    
    functions = [
        ("Original function", test_function),
        ("@sensitive_variables", decorated_with_sensitive_variables),
        ("@sensitive_post_parameters", decorated_with_sensitive_post_parameters),
        ("Both decorators", decorated_with_both),
    ]
    
    # Test with correct arguments
    print("\nTesting with correct arguments:")
    for name, func in functions:
        print(f"  {name}:")
        try:
            result = inspect.getcallargs(func, None, username="test", password="secret")
            print(f"    SUCCESS: {result}")
        except TypeError as e:
            print(f"    ERROR: {e}")
    
    # Test with wrong arguments to ensure proper rejection
    print("\nTesting with wrong arguments (should all fail):")
    for name, func in functions:
        print(f"  {name}:")
        try:
            result = inspect.getcallargs(func, None, wrong_arg="test")
            print(f"    ERROR: Should have failed but got: {result}")
        except TypeError as e:
            print(f"    SUCCESS: Correctly rejected: {e}")


def test_decorator_functionality():
    """Test that the decorators still work correctly"""
    
    print("\n=== Testing decorator functionality ===")
    
    # Create a mock request
    request = HttpRequest()
    
    # Test sensitive_variables
    result = decorated_with_sensitive_variables(request, username="test", password="secret")
    print(f"sensitive_variables result: {result}")
    print(f"sensitive_variables attribute: {getattr(decorated_with_sensitive_variables, 'sensitive_variables', 'Not set')}")
    
    # Test sensitive_post_parameters
    result = decorated_with_sensitive_post_parameters(request, username="test", password="secret")
    print(f"sensitive_post_parameters result: {result}")
    print(f"request.sensitive_post_parameters: {getattr(request, 'sensitive_post_parameters', 'Not set')}")
    
    # Test both decorators
    request2 = HttpRequest()  # Fresh request
    result = decorated_with_both(request2, username="test", password="secret")
    print(f"both decorators result: {result}")
    print(f"both decorators sensitive_variables: {getattr(decorated_with_both, 'sensitive_variables', 'Not set')}")
    print(f"both decorators request.sensitive_post_parameters: {getattr(request2, 'sensitive_post_parameters', 'Not set')}")


if __name__ == "__main__":
    test_signature_preservation()
    test_decorator_functionality()
#!/usr/bin/env python3

import inspect
import functools
from django.views.decorators.debug import sensitive_variables

# Test the current behavior
def test_function(request, username, password):
    """Test function with specific signature"""
    return f"authenticated {username}"

@sensitive_variables('password')
def decorated_test_function(request, username, password):
    """Test function decorated with sensitive_variables"""
    return f"authenticated {username}"

def test_signature_preservation():
    """Test if sensitive_variables preserves function signature"""
    
    print("=== Testing signature preservation ===")
    
    # Test original function
    print("Original function signature:")
    try:
        result = inspect.getcallargs(test_function, None, username="test", password="secret")
        print(f"  getcallargs succeeded: {result}")
    except TypeError as e:
        print(f"  getcallargs failed: {e}")
    
    # Test decorated function
    print("Decorated function signature:")
    try:
        result = inspect.getcallargs(decorated_test_function, None, username="test", password="secret")
        print(f"  getcallargs succeeded: {result}")
    except TypeError as e:
        print(f"  getcallargs failed: {e}")
    
    # Test with wrong arguments to see if it properly rejects
    print("Testing with wrong arguments:")
    try:
        result = inspect.getcallargs(test_function, None, wrong_arg="test")
        print(f"  Original function accepted wrong args: {result}")
    except TypeError as e:
        print(f"  Original function properly rejected wrong args: {e}")
    
    try:
        result = inspect.getcallargs(decorated_test_function, None, wrong_arg="test")
        print(f"  Decorated function accepted wrong args: {result}")
    except TypeError as e:
        print(f"  Decorated function properly rejected wrong args: {e}")

if __name__ == "__main__":
    test_signature_preservation()
#!/usr/bin/env python3

import inspect
import functools

def sensitive_variables_fixed(*variables):
    """
    Fixed version of sensitive_variables that preserves function signature
    """
    def decorator(func):
        @functools.wraps(func)
        def sensitive_variables_wrapper(*func_args, **func_kwargs):
            if variables:
                sensitive_variables_wrapper.sensitive_variables = variables
            else:
                sensitive_variables_wrapper.sensitive_variables = '__ALL__'
            return func(*func_args, **func_kwargs)
        
        # Preserve the original function's signature
        sensitive_variables_wrapper.__signature__ = inspect.signature(func)
        
        return sensitive_variables_wrapper
    return decorator

# Test functions
def test_function(request, username, password):
    """Test function with specific signature"""
    return f"authenticated {username}"

@sensitive_variables_fixed('password')
def decorated_test_function(request, username, password):
    """Test function decorated with fixed sensitive_variables"""
    return f"authenticated {username}"

def test_signature_preservation():
    """Test if the fixed sensitive_variables preserves function signature"""
    
    print("=== Testing FIXED signature preservation ===")
    
    # Test original function
    print("Original function signature:")
    try:
        result = inspect.getcallargs(test_function, None, username="test", password="secret")
        print(f"  getcallargs succeeded: {result}")
    except TypeError as e:
        print(f"  getcallargs failed: {e}")
    
    # Test decorated function
    print("Fixed decorated function signature:")
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
        print(f"  Fixed decorated function accepted wrong args: {result}")
    except TypeError as e:
        print(f"  Fixed decorated function properly rejected wrong args: {e}")

    # Test that the decorator still works
    print("Testing decorator functionality:")
    result = decorated_test_function(None, username="test", password="secret")
    print(f"  Function call result: {result}")
    print(f"  Sensitive variables: {getattr(decorated_test_function, 'sensitive_variables', 'Not set')}")

if __name__ == "__main__":
    test_signature_preservation()
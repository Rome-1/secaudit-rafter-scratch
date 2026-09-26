#!/usr/bin/env python3

import inspect
from django.views.decorators.debug import sensitive_variables

# Simulate authentication backend classes
class TestBackend1:
    def authenticate(self, request, username=None, password=None):
        """Backend that accepts username/password"""
        if username == "test" and password == "secret":
            return {"username": username}
        return None

class TestBackend2:
    @sensitive_variables('password')
    def authenticate(self, request, username=None, password=None):
        """Backend with sensitive_variables decorator that accepts username/password"""
        if username == "test" and password == "secret":
            return {"username": username}
        return None

class TestBackend3:
    @sensitive_variables('token')
    def authenticate(self, request, token=None):
        """Backend with sensitive_variables decorator that accepts only token"""
        if token == "valid_token":
            return {"token": token}
        return None

def test_backend_signature_matching():
    """Test that backends with sensitive_variables work correctly with inspect.getcallargs"""
    
    backends = [
        ("TestBackend1", TestBackend1()),
        ("TestBackend2", TestBackend2()),
        ("TestBackend3", TestBackend3()),
    ]
    
    test_credentials = [
        {"username": "test", "password": "secret"},
        {"token": "valid_token"},
        {"username": "test", "wrong_param": "value"},
    ]
    
    print("=== Testing authentication backend signature matching ===")
    
    for backend_name, backend in backends:
        print(f"\nTesting {backend_name}:")
        
        for i, credentials in enumerate(test_credentials):
            print(f"  Credentials {i+1}: {credentials}")
            try:
                result = inspect.getcallargs(backend.authenticate, None, **credentials)
                print(f"    SUCCESS getcallargs succeeded: {result}")
                
                # Try to actually call the method
                try:
                    auth_result = backend.authenticate(None, **credentials)
                    print(f"    SUCCESS authenticate call succeeded: {auth_result}")
                except Exception as e:
                    print(f"    ERROR authenticate call failed: {e}")
                    
            except TypeError as e:
                print(f"    ERROR getcallargs failed (expected for incompatible credentials): {e}")

def simulate_django_authenticate():
    """Simulate Django's authenticate function logic"""
    
    backends = [TestBackend1(), TestBackend2(), TestBackend3()]
    credentials = {"username": "test", "password": "secret"}
    
    print(f"\n=== Simulating Django authenticate with credentials: {credentials} ===")
    
    for i, backend in enumerate(backends):
        backend_name = f"Backend{i+1}"
        print(f"\nTrying {backend_name}:")
        
        try:
            # This is the critical line from Django's authenticate function
            inspect.getcallargs(backend.authenticate, None, **credentials)
            print(f"  SUCCESS Backend signature matches, proceeding to authenticate")
            
            try:
                user = backend.authenticate(None, **credentials)
                if user is not None:
                    print(f"  SUCCESS Authentication successful: {user}")
                    return user
                else:
                    print(f"  - Authentication failed (invalid credentials)")
            except Exception as e:
                print(f"  ERROR Authentication raised exception: {e}")
                
        except TypeError as e:
            print(f"  - Backend signature doesn't match, skipping: {e}")
            continue
    
    print("  No backend could authenticate the user")
    return None

if __name__ == "__main__":
    test_backend_signature_matching()
    simulate_django_authenticate()
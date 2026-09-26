#!/usr/bin/env python3
"""
Script to reproduce the GRPC context timeout error issue.
This script demonstrates the issue where context timeout errors
return wrong GRPC status codes.
"""

import os
import sys
import inspect
import logging

def test_error_handling():
    """Test error handling patterns in the middleware"""
    print("=== Testing Context Error Handling ===")
    
    # Look at the current ErrorUnaryInterceptor implementation
    middleware_file = "/app/internal/server/middleware/grpc/middleware.go"
    
    with open(middleware_file, 'r') as f:
        content = f.read()
    
    print("Current ErrorUnaryInterceptor implementation:")
    
    # Find the ErrorUnaryInterceptor function
    lines = content.split('\n')
    in_function = False
    function_lines = []
    indent_level = 0
    
    for i, line in enumerate(lines):
        if 'func ErrorUnaryInterceptor' in line:
            in_function = True
            function_lines.append(f"{i+1:3}: {line}")
            if '{' in line:
                indent_level = 1
        elif in_function:
            function_lines.append(f"{i+1:3}: {line}")
            if '{' in line:
                indent_level += 1
            if '}' in line:
                indent_level -= 1
                if indent_level == 0:
                    break
    
    for line in function_lines:
        print(line)
    
    print("\n=== Analysis ===")
    print("Issues found:")
    print("1. No handling for context.Canceled or context.DeadlineExceeded errors")
    print("2. These errors should return codes.Canceled and codes.DeadlineExceeded respectively")
    print("3. Instead, they fall through to codes.Internal")
    
    # Look at auth middleware
    print("\n=== Auth Middleware Analysis ===")
    auth_middleware_file = "/app/internal/server/auth/middleware.go"
    
    with open(auth_middleware_file, 'r') as f:
        auth_content = f.read()
    
    # Find the UnaryInterceptor function
    auth_lines = auth_content.split('\n')
    in_function = False
    function_lines = []
    indent_level = 0
    
    for i, line in enumerate(auth_lines):
        if 'func UnaryInterceptor' in line and 'authenticator Authenticator' in line:
            in_function = True
            function_lines.append(f"{i+1:3}: {line}")
            if '{' in line:
                indent_level = 1
        elif in_function:
            function_lines.append(f"{i+1:3}: {line}")
            if '{' in line:
                indent_level += 1
            if '}' in line:
                indent_level -= 1
                if indent_level == 0:
                    break
    
    print("Current Auth UnaryInterceptor relevant parts:")
    for line in function_lines[100:120]:  # Show the part where the error handling is
        if "GetAuthenticationByClientToken" in line or "error" in line:
            print(line)
    
    print("\nAuth middleware issue:")
    print("- When GetAuthenticationByClientToken fails due to context timeout/cancellation")
    print("- It returns errUnauthenticated instead of preserving the context error")
    
    # Look at server setup
    print("\n=== Server Setup Analysis ===")
    grpc_server_file = "/app/internal/cmd/grpc.go"
    
    with open(grpc_server_file, 'r') as f:
        grpc_content = f.read()
    
    print("Current interceptor chain setup:")
    grpc_lines = grpc_content.split('\n')
    for i, line in enumerate(grpc_lines):
        if 'grpc_middleware.WithUnaryServerChain' in line:
            print(f"{i+1:3}: {line}")
    
    print("\nServer setup issue:")
    print("- Using deprecated grpc_middleware.WithUnaryServerChain")
    print("- Should use grpc.ChainUnaryInterceptor instead")

if __name__ == "__main__":
    test_error_handling()
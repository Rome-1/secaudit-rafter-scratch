#!/usr/bin/env python3
"""
Script to test the fix for the GRPC context timeout error issue.
"""

def test_error_handling_fix():
    """Test that error handling is fixed"""
    print("=== Testing Fixed Context Error Handling ===")
    
    # Look at the updated ErrorUnaryInterceptor implementation
    middleware_file = "/app/internal/server/middleware/grpc/middleware.go"
    
    with open(middleware_file, 'r') as f:
        content = f.read()
    
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
    
    print("Updated ErrorUnaryInterceptor implementation:")
    for line in function_lines:
        print(line)
    
    # Check for context error handling
    has_context_canceled = any('context.Canceled' in line for line in function_lines)
    has_context_deadline = any('context.DeadlineExceeded' in line for line in function_lines)
    
    print(f"\n✅ Context.Canceled handling: {has_context_canceled}")
    print(f"✅ Context.DeadlineExceeded handling: {has_context_deadline}")
    
    # Test auth middleware fix
    print("\n=== Testing Fixed Auth Middleware ===")
    auth_middleware_file = "/app/internal/server/auth/middleware.go"
    
    with open(auth_middleware_file, 'r') as f:
        auth_content = f.read()
    
    has_auth_context_canceled = 'errors.Is(err, context.Canceled)' in auth_content
    has_auth_context_deadline = 'errors.Is(err, context.DeadlineExceeded)' in auth_content
    
    print(f"✅ Auth middleware Context.Canceled handling: {has_auth_context_canceled}")
    print(f"✅ Auth middleware Context.DeadlineExceeded handling: {has_auth_context_deadline}")
    
    # Show the relevant part of auth middleware
    auth_lines = auth_content.split('\n')
    for i, line in enumerate(auth_lines):
        if 'GetAuthenticationByClientToken' in line:
            print(f"\nRelevant auth middleware section (starting at line {i+1}):")
            for j in range(max(0, i), min(len(auth_lines), i+20)):
                if 'context.' in auth_lines[j] or 'err != nil' in auth_lines[j] or 'return' in auth_lines[j]:
                    print(f"{j+1:3}: {auth_lines[j]}")
            break
    
    # Test server setup fix
    print("\n=== Testing Fixed Server Setup ===")
    grpc_server_file = "/app/internal/cmd/grpc.go"
    
    with open(grpc_server_file, 'r') as f:
        grpc_content = f.read()
    
    has_chain_interceptor = 'grpc.ChainUnaryInterceptor' in grpc_content
    has_deprecated_chain = 'grpc_middleware.WithUnaryServerChain' in grpc_content
    
    print(f"✅ Using new grpc.ChainUnaryInterceptor: {has_chain_interceptor}")
    print(f"✅ Removed deprecated grpc_middleware.WithUnaryServerChain: {not has_deprecated_chain}")
    
    # Show the relevant line
    grpc_lines = grpc_content.split('\n')
    for i, line in enumerate(grpc_lines):
        if 'grpc.ChainUnaryInterceptor' in line:
            print(f"{i+1:3}: {line}")
            break
    
    print("\n=== Summary ===")
    all_fixes = [
        has_context_canceled,
        has_context_deadline, 
        has_auth_context_canceled,
        has_auth_context_deadline,
        has_chain_interceptor,
        not has_deprecated_chain
    ]
    
    if all(all_fixes):
        print("🎉 All fixes have been successfully implemented!")
        print("✅ ErrorUnaryInterceptor now handles context.Canceled and context.DeadlineExceeded")
        print("✅ Auth middleware preserves context errors instead of masking as authentication failures")
        print("✅ GRPC server uses the new ChainUnaryInterceptor instead of deprecated middleware")
    else:
        print("❌ Some fixes are missing:")
        fix_names = [
            "Context.Canceled in ErrorUnaryInterceptor",
            "Context.DeadlineExceeded in ErrorUnaryInterceptor",
            "Context.Canceled in Auth middleware",
            "Context.DeadlineExceeded in Auth middleware", 
            "grpc.ChainUnaryInterceptor in server setup",
            "Removed deprecated grpc_middleware.WithUnaryServerChain"
        ]
        for fix_name, implemented in zip(fix_names, all_fixes):
            status = "✅" if implemented else "❌"
            print(f"{status} {fix_name}")

if __name__ == "__main__":
    test_error_handling_fix()
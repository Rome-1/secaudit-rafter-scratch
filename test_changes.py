#!/usr/bin/env python3
"""
Test script to verify OCI source implementation
"""
import subprocess
import sys

def run_command(cmd, cwd="/app"):
    """Run a command and return its output"""
    result = subprocess.run(
        cmd,
        shell=True,
        cwd=cwd,
        capture_output=True,
        text=True
    )
    return result.returncode, result.stdout, result.stderr

def main():
    print("Testing OCI source implementation...")
    
    # Check if OCI source file exists
    print("\n1. Checking if OCI source file exists...")
    code, out, err = run_command("test -f /app/internal/storage/fs/oci/source.go && echo 'exists' || echo 'not exists'")
    print(f"   Result: {out.strip()}")
    
    # Try to build the project
    print("\n2. Building the project...")
    code, out, err = run_command("cd /app && go build ./internal/storage/fs/... 2>&1")
    if code == 0:
        print("   Build successful!")
    else:
        print(f"   Build failed with error:\n{err}")
        return 1
    
    # Run tests for OCI module
    print("\n3. Running OCI tests...")
    code, out, err = run_command("cd /app && go test ./internal/oci/... -v 2>&1")
    if code == 0:
        print("   Tests passed!")
    else:
        print(f"   Tests failed:\n{out}\n{err}")
        return 1
    
    print("\n✅ All checks passed!")
    return 0

if __name__ == "__main__":
    sys.exit(main())

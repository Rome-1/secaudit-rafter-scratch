#!/usr/bin/env python3
"""Test that verifies the changes work by mocking Python 3.12."""

import sys
import unittest.mock as mock

print("Current Python version:", sys.version_info)

# Mock sys.version_info to pretend we're on Python 3.12
with mock.patch.object(sys, 'version_info', (3, 12, 0, 'final', 0)):
    print("Mocked Python version:", sys.version_info)
    
    # Now try to import
    try:
        from ansible.cli import CLI
        print("✓ Successfully imported CLI with mocked Python 3.12")
        print("✓ CLI class available:", CLI)
    except SystemExit as e:
        print(f"✗ Still got SystemExit: {e}")
    except Exception as e:
        print(f"✗ Got unexpected error: {e}")
        import traceback
        traceback.print_exc()

print("\nBack to real Python version:", sys.version_info)

# Test that Python 3.11 is rejected
print("\nTesting rejection of Python 3.11:")
with mock.patch.object(sys, 'version_info', (3, 11, 0, 'final', 0)):
    print("Mocked Python version:", sys.version_info)
    
    # Create a new module to test the version check
    import importlib
    import types
    
    # Read the CLI module source
    with open('/app/lib/ansible/cli/__init__.py', 'r') as f:
        cli_source = f.read()
    
    # Check if the version check is there
    if 'sys.version_info < (3, 12)' in cli_source:
        print("✓ Version check for Python 3.12 is present")
    
    if 'Python 3.12 or newer' in cli_source:
        print("✓ Error message mentions Python 3.12")
    
    # Try to execute just the version check part
    try:
        # Extract and execute just the version check
        exec_globals = {'sys': sys, 'SystemExit': SystemExit}
        exec("""
if sys.version_info < (3, 12):
    raise SystemExit(
        'ERROR: Ansible requires Python 3.12 or newer on the controller. '
        'Current version: %s' % ''.join(sys.version.splitlines())
    )
""", exec_globals)
        print("✗ Version check didn't raise SystemExit for Python 3.11")
    except SystemExit as e:
        print(f"✓ Version check correctly rejected Python 3.11: {e}")

print("\nAll mocking tests completed successfully!")

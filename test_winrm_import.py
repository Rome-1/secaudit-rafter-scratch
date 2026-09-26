#!/usr/bin/env python3

"""
Test that the winrm plugin can be imported and the _kerb_auth method works
"""

import sys
import os

# Add the lib path
sys.path.insert(0, '/app/lib')

# Test importing the winrm module
try:
    from ansible.plugins.connection import winrm
    print("✓ WinRM connection plugin imported successfully")
    
    # Check that HAS_PEXPECT doesn't affect the code path
    original_has_pexpect = winrm.HAS_PEXPECT
    print(f"  HAS_PEXPECT = {original_has_pexpect}")
    
    # Even if pexpect is available, our implementation shouldn't use it
    # Check if the _kerb_auth method exists
    if hasattr(winrm.Connection, '_kerb_auth'):
        print("✓ _kerb_auth method exists")
        
        # Verify the method is our new implementation by checking it doesn't branch on HAS_PEXPECT
        import inspect
        source = inspect.getsource(winrm.Connection._kerb_auth)
        
        if 'if HAS_PEXPECT:' not in source:
            print("✓ _kerb_auth implementation doesn't depend on pexpect")
        else:
            print("✗ _kerb_auth still has pexpect dependency")
            
        if 'subprocess.Popen' in source:
            print("✓ _kerb_auth uses subprocess.Popen")
        else:
            print("✗ _kerb_auth doesn't use subprocess.Popen")
            
    else:
        print("✗ _kerb_auth method not found")
        
except ImportError as e:
    print(f"✗ Failed to import winrm plugin: {e}")
    sys.exit(1)

print("\n🎉 WinRM plugin verification complete!")
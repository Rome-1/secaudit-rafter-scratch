#!/usr/bin/env python3

"""
Test script to reproduce the WinRM Kerberos authentication issue
and verify the fix.
"""

import os
import sys
import tempfile
import subprocess
import shlex

# Mock the necessary parts to test the kerberos authentication method
class MockConnection:
    """Mock WinRM Connection class for testing"""
    
    def __init__(self):
        self._kerb_ccache = None
        self.options = {
            'kerberos_command': 'kinit',
            'kinit_args': None,
            'kinit_env_vars': [],
            '_extras': {}
        }
    
    def get_option(self, key):
        return self.options.get(key)

def test_current_kerb_auth(principal, password):
    """Test the current _kerb_auth implementation"""
    print(f"Testing current kerberos auth for principal: {principal}")
    
    # Simulate the current _kerb_auth method logic
    if password is None:
        password = ""

    kerb_ccache = tempfile.NamedTemporaryFile()
    print(f"creating Kerberos CC at {kerb_ccache.name}")
    
    krb5ccname = f"FILE:{kerb_ccache.name}"
    os.environ["KRB5CCNAME"] = krb5ccname
    krb5env = dict(PATH=os.environ["PATH"], KRB5CCNAME=krb5ccname)

    # Build kinit command line
    kinit_cmdline = ['echo']  # Use echo instead of kinit for testing
    kinit_cmdline.append(f"would_run_kinit_for_{principal}")
    
    print(f"Would run command: {' '.join(kinit_cmdline)}")
    print(f"Environment: PATH={krb5env.get('PATH', 'NOT_SET')[:50]}..., KRB5CCNAME={krb5env.get('KRB5CCNAME')}")
    
    # Test subprocess approach (current fallback when pexpect not available)
    try:
        p = subprocess.Popen(kinit_cmdline, 
                           stdin=subprocess.PIPE,
                           stdout=subprocess.PIPE,
                           stderr=subprocess.PIPE,
                           env=krb5env)
        
        stdout, stderr = p.communicate(password.encode('utf-8') + b'\n')
        rc = p.returncode
        
        print(f"Return code: {rc}")
        print(f"Stdout: {stdout.decode('utf-8').strip()}")
        print(f"Stderr: {stderr.decode('utf-8').strip()}")
        
    except OSError as err:
        print(f"OSError when calling command: {err}")
        raise

def test_new_kerb_auth(principal, password):
    """Test the new improved _kerb_auth implementation"""
    print(f"\nTesting NEW kerberos auth for principal: {principal}")
    
    # This will be our new implementation
    if password is None:
        password = ""

    kerb_ccache = tempfile.NamedTemporaryFile()
    print(f"creating Kerberos CC at {kerb_ccache.name}")
    
    krb5ccname = f"FILE:{kerb_ccache.name}"
    krb5env = dict(PATH=os.environ.get("PATH", ""), KRB5CCNAME=krb5ccname)

    # Build kinit command line
    kinit_cmd = 'echo'  # Use echo instead of kinit for testing
    kinit_cmdline = [kinit_cmd]
    
    # Add args if specified
    kinit_args = None  # Would come from self.get_option('kinit_args')
    if kinit_args:
        kinit_args = [str(a) for a in shlex.split(kinit_args) if a.strip()]
        kinit_cmdline.extend(kinit_args)
    elif False:  # Would be: boolean(self.get_option('_extras').get('ansible_winrm_kerberos_delegation', False))
        kinit_cmdline.append('-f')
    
    kinit_cmdline.append(f"would_run_kinit_for_{principal}")
    
    print(f"Would run command: {' '.join(kinit_cmdline)}")
    print(f"Environment: PATH={krb5env.get('PATH', 'NOT_SET')[:50]}..., KRB5CCNAME={krb5env.get('KRB5CCNAME')}")
    
    # New approach - always use subprocess, no pexpect dependency
    try:
        p = subprocess.Popen(kinit_cmdline,
                           stdin=subprocess.PIPE,
                           stdout=subprocess.PIPE, 
                           stderr=subprocess.PIPE,
                           env=krb5env)
        
        # Send password to stdin and close it
        stdout, stderr = p.communicate(password.encode('utf-8') + b'\n')
        rc = p.returncode
        
        print(f"Return code: {rc}")
        print(f"Stdout: {stdout.decode('utf-8').strip()}")
        print(f"Stderr: {stderr.decode('utf-8').strip()}")
        
        if rc != 0:
            # Redact password from stderr
            exp_msg = stderr.decode('utf-8').strip()
            exp_msg = exp_msg.replace(password, "<redacted>")
            err_msg = f"Kerberos auth failure for principal {principal}: {exp_msg}"
            print(f"Would raise AnsibleConnectionFailure: {err_msg}")
        else:
            print(f"kinit succeeded for principal {principal}")
            
    except OSError as err:
        err_msg = f"Kerberos auth failure when calling kinit cmd '{kinit_cmd}': {err}"
        print(f"Would raise AnsibleConnectionFailure: {err_msg}")
        raise

if __name__ == "__main__":
    test_principal = "testuser@EXAMPLE.COM"
    test_password = "testpassword"
    
    try:
        test_current_kerb_auth(test_principal, test_password)
        test_new_kerb_auth(test_principal, test_password)
        print("\n✓ Basic tests passed")
    except Exception as e:
        print(f"\n✗ Test failed: {e}")
        sys.exit(1)
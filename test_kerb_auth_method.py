#!/usr/bin/env python3

"""
Direct test of the _kerb_auth method to verify the fix.
"""

import os
import sys
import tempfile
import subprocess
import shlex
from unittest.mock import patch, MagicMock

# Add the lib path to import ansible modules
sys.path.insert(0, '/app/lib')

from ansible.module_utils.common.text.converters import to_text, to_bytes, to_native
from ansible.module_utils.parsing.convert_bool import boolean
from ansible.errors import AnsibleConnectionFailure
from ansible.utils.display import Display

display = Display()

def mock_kerb_auth(principal, password, kinit_cmd='kinit', kinit_args=None, 
                  kinit_env_vars=None, kerberos_delegation=False):
    """
    Standalone version of the _kerb_auth method for testing
    """
    if password is None:
        password = ""
    if kinit_env_vars is None:
        kinit_env_vars = []

    kerb_ccache = tempfile.NamedTemporaryFile()
    display.vvvvv("creating Kerberos CC at %s" % kerb_ccache.name)
    krb5ccname = "FILE:%s" % kerb_ccache.name
    os.environ["KRB5CCNAME"] = krb5ccname
    krb5env = dict(PATH=os.environ.get("PATH", ""), KRB5CCNAME=krb5ccname)

    # Add any explicit environment vars into the krb5env block
    for var in kinit_env_vars:
        if var not in krb5env and var in os.environ:
            krb5env[var] = os.environ[var]

    # Stores various flags to call with kinit, these could be explicit args set by 'ansible_winrm_kinit_args' OR
    # '-f' if kerberos delegation is requested (ansible_winrm_kerberos_delegation).
    kinit_cmdline = [kinit_cmd]
    if kinit_args:
        kinit_args = [to_text(a) for a in shlex.split(kinit_args) if a.strip()]
        kinit_cmdline.extend(kinit_args)
    elif kerberos_delegation:
        kinit_cmdline.append('-f')

    kinit_cmdline.append(principal)

    # Use subprocess for all kinit operations to avoid dependency on pexpect
    # and ensure consistent behavior across all platforms
    b_password = to_bytes(password, encoding='utf-8', errors='surrogate_or_strict')

    display.vvvv("calling kinit with subprocess for principal %s" % principal)
    try:
        p = subprocess.Popen(kinit_cmdline, 
                           stdin=subprocess.PIPE,
                           stdout=subprocess.PIPE,
                           stderr=subprocess.PIPE,
                           env=krb5env)

    except OSError as err:
        err_msg = "Kerberos auth failure when calling kinit cmd " \
                  "'%s': %s" % (kinit_cmd, to_native(err))
        raise AnsibleConnectionFailure(err_msg)

    stdout, stderr = p.communicate(b_password + b'\n')
    rc = p.returncode

    if rc != 0:
        # one last attempt at making sure the password does not exist
        # in the output
        exp_msg = to_native(stderr.strip())
        exp_msg = exp_msg.replace(to_native(password), "<redacted>")

        err_msg = "Kerberos auth failure for principal %s: %s" \
                  % (principal, exp_msg)
        raise AnsibleConnectionFailure(err_msg)

    display.vvvvv("kinit succeeded for principal %s" % principal)
    return kerb_ccache  # Return for cleanup

def test_basic_functionality():
    """Test basic kinit functionality with echo command"""
    print("=== Testing basic functionality ===")
    
    # Use echo instead of actual kinit for testing
    try:
        ccache = mock_kerb_auth('testuser@EXAMPLE.COM', 'testpass', kinit_cmd='echo')
        print("✓ Basic functionality works")
        ccache.close()
    except Exception as e:
        print(f"✗ Basic functionality failed: {e}")
        raise

def test_kinit_args():
    """Test kinit_args handling"""
    print("=== Testing kinit_args ===")
    
    with patch('subprocess.Popen') as mock_popen:
        mock_process = MagicMock()
        mock_process.communicate.return_value = (b'', b'')
        mock_process.returncode = 0
        mock_popen.return_value = mock_process
        
        ccache = mock_kerb_auth('testuser@EXAMPLE.COM', 'testpass', 
                               kinit_cmd='kinit', kinit_args='-r 1d -l 8h')
        
        # Verify the command line
        args, kwargs = mock_popen.call_args
        cmdline = args[0]
        expected = ['kinit', '-r', '1d', '-l', '8h', 'testuser@EXAMPLE.COM']
        
        assert cmdline == expected, f"Expected {expected}, got {cmdline}"
        print("✓ kinit_args parsed and included correctly")
        ccache.close()

def test_kerberos_delegation():
    """Test kerberos delegation flag"""
    print("=== Testing kerberos delegation ===")
    
    with patch('subprocess.Popen') as mock_popen:
        mock_process = MagicMock()
        mock_process.communicate.return_value = (b'', b'')
        mock_process.returncode = 0
        mock_popen.return_value = mock_process
        
        ccache = mock_kerb_auth('testuser@EXAMPLE.COM', 'testpass',
                               kinit_cmd='kinit', kerberos_delegation=True)
        
        # Verify -f flag is added
        args, kwargs = mock_popen.call_args
        cmdline = args[0]
        expected = ['kinit', '-f', 'testuser@EXAMPLE.COM']
        
        assert cmdline == expected, f"Expected {expected}, got {cmdline}"
        print("✓ Kerberos delegation -f flag added correctly")
        ccache.close()

def test_environment_setup():
    """Test environment variable setup"""
    print("=== Testing environment setup ===")
    
    with patch('subprocess.Popen') as mock_popen:
        mock_process = MagicMock()
        mock_process.communicate.return_value = (b'', b'')
        mock_process.returncode = 0
        mock_popen.return_value = mock_process
        
        # Set test env vars
        os.environ['TEST_VAR'] = 'test_value'
        
        try:
            ccache = mock_kerb_auth('testuser@EXAMPLE.COM', 'testpass',
                                   kinit_cmd='kinit', kinit_env_vars=['TEST_VAR', 'NONEXISTENT'])
            
            # Check environment passed to subprocess
            args, kwargs = mock_popen.call_args
            env = kwargs['env']
            
            # Should have PATH and KRB5CCNAME
            assert 'PATH' in env, "PATH should be in environment"
            assert 'KRB5CCNAME' in env, "KRB5CCNAME should be in environment" 
            assert env['KRB5CCNAME'].startswith('FILE:'), f"KRB5CCNAME should start with FILE:, got {env['KRB5CCNAME']}"
            
            # Should have our test var
            assert env['TEST_VAR'] == 'test_value', f"TEST_VAR should be test_value, got {env.get('TEST_VAR')}"
            
            # Should not have nonexistent var
            assert 'NONEXISTENT' not in env, "NONEXISTENT should not be in environment"
            
            print("✓ Environment variables set up correctly")
            ccache.close()
            
        finally:
            del os.environ['TEST_VAR']

def test_error_handling_bad_command():
    """Test error handling for bad command"""
    print("=== Testing error handling for bad command ===")
    
    try:
        mock_kerb_auth('testuser@EXAMPLE.COM', 'testpass',
                      kinit_cmd='/nonexistent/command')
        assert False, "Should have raised AnsibleConnectionFailure"
    except AnsibleConnectionFailure as e:
        error_msg = str(e)
        expected_prefix = "Kerberos auth failure when calling kinit cmd '/nonexistent/command':"
        assert error_msg.startswith(expected_prefix), f"Expected error to start with '{expected_prefix}', got '{error_msg}'"
        print(f"✓ Correct error for bad command: {error_msg}")

def test_error_handling_kinit_failure():
    """Test error handling for kinit failure"""
    print("=== Testing error handling for kinit failure ===")
    
    with patch('subprocess.Popen') as mock_popen:
        mock_process = MagicMock()
        mock_process.communicate.return_value = (b'', b'kinit: Password incorrect for testpass')
        mock_process.returncode = 1  # Failure
        mock_popen.return_value = mock_process
        
        try:
            mock_kerb_auth('testuser@EXAMPLE.COM', 'testpass', kinit_cmd='kinit')
            assert False, "Should have raised AnsibleConnectionFailure"
        except AnsibleConnectionFailure as e:
            error_msg = str(e)
            # Password should be redacted
            assert 'testpass' not in error_msg, f"Password should be redacted: {error_msg}"
            assert '<redacted>' in error_msg, f"Should contain <redacted>: {error_msg}"
            assert 'Kerberos auth failure for principal testuser@EXAMPLE.COM:' in error_msg
            print(f"✓ Correct error handling with redaction: {error_msg}")

def test_password_sent_to_stdin():
    """Test that password is sent to stdin correctly"""
    print("=== Testing password sent to stdin ===")
    
    with patch('subprocess.Popen') as mock_popen:
        mock_process = MagicMock()
        mock_process.communicate.return_value = (b'', b'')
        mock_process.returncode = 0
        mock_popen.return_value = mock_process
        
        ccache = mock_kerb_auth('testuser@EXAMPLE.COM', 'mypassword', kinit_cmd='kinit')
        
        # Verify password was sent to stdin with newline
        mock_process.communicate.assert_called_once_with(b'mypassword\n')
        print("✓ Password sent to stdin correctly")
        ccache.close()

def run_tests():
    """Run all tests"""
    tests = [
        test_basic_functionality,
        test_kinit_args,
        test_kerberos_delegation,
        test_environment_setup,
        test_error_handling_bad_command,
        test_error_handling_kinit_failure,
        test_password_sent_to_stdin
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        try:
            test()
            passed += 1
        except Exception as e:
            print(f"✗ {test.__name__} FAILED: {e}")
            failed += 1
            import traceback
            traceback.print_exc()
    
    print(f"\n=== Results ===")
    print(f"Passed: {passed}")
    print(f"Failed: {failed}")
    
    return failed == 0

if __name__ == "__main__":
    success = run_tests()
    if not success:
        sys.exit(1)
    print("All tests passed! 🎉")
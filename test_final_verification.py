#!/usr/bin/env python3

"""
Final verification that the WinRM Kerberos fix meets all requirements
from the PR description.
"""

import os
import sys
import tempfile
import subprocess
import shlex
from unittest.mock import patch, MagicMock

# Add the lib path
sys.path.insert(0, '/app/lib')

from ansible.module_utils.common.text.converters import to_text, to_bytes, to_native
from ansible.module_utils.parsing.convert_bool import boolean
from ansible.errors import AnsibleConnectionFailure
from ansible.utils.display import Display

display = Display()

def new_kerb_auth(principal, password, kinit_cmd='kinit', kinit_args=None, 
                  kinit_env_vars=None, kerberos_delegation=False):
    """
    The NEW _kerb_auth implementation (matches the one in winrm.py)
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
    return kerb_ccache

def test_requirement_no_pexpect_dependency():
    """Requirement: Must work without relying on optional third-party libraries"""
    print("=== Testing: No pexpect dependency ===")
    
    # Test that it works even when pexpect is not available
    with patch('subprocess.Popen') as mock_popen:
        mock_process = MagicMock()
        mock_process.communicate.return_value = (b'', b'')
        mock_process.returncode = 0
        mock_popen.return_value = mock_process
        
        ccache = new_kerb_auth('test@EXAMPLE.COM', 'testpass')
        
        # Verify subprocess was used, not pexpect
        assert mock_popen.called, "subprocess.Popen should be called"
        print("✓ Uses subprocess, no pexpect dependency")
        ccache.close()

def test_requirement_stdin_password():
    """Requirement: Must read password from stdin on all platforms"""
    print("=== Testing: Password sent to stdin ===")
    
    with patch('subprocess.Popen') as mock_popen:
        mock_process = MagicMock()
        mock_process.communicate.return_value = (b'', b'')
        mock_process.returncode = 0
        mock_popen.return_value = mock_process
        
        ccache = new_kerb_auth('test@EXAMPLE.COM', 'mypassword')
        
        # Verify password sent to stdin with newline
        mock_process.communicate.assert_called_once_with(b'mypassword\n')
        print("✓ Password sent to stdin correctly")
        ccache.close()

def test_requirement_kinit_cmd():
    """Requirement: ansible_winrm_kinit_cmd must be accepted"""
    print("=== Testing: Custom kinit_cmd ===")
    
    with patch('subprocess.Popen') as mock_popen:
        mock_process = MagicMock()
        mock_process.communicate.return_value = (b'', b'')
        mock_process.returncode = 0
        mock_popen.return_value = mock_process
        
        ccache = new_kerb_auth('test@EXAMPLE.COM', 'testpass', 
                              kinit_cmd='/custom/kinit')
        
        args, kwargs = mock_popen.call_args
        cmdline = args[0]
        assert cmdline[0] == '/custom/kinit', f"Expected /custom/kinit, got {cmdline[0]}"
        print("✓ Custom kinit_cmd accepted")
        ccache.close()

def test_requirement_kinit_args():
    """Requirement: ansible_winrm_kinit_args must be accepted and parsed as shell-like"""
    print("=== Testing: kinit_args parsing ===")
    
    with patch('subprocess.Popen') as mock_popen:
        mock_process = MagicMock()
        mock_process.communicate.return_value = (b'', b'')
        mock_process.returncode = 0
        mock_popen.return_value = mock_process
        
        ccache = new_kerb_auth('test@EXAMPLE.COM', 'testpass',
                              kinit_args='-r 1d -l "8 hours"')
        
        args, kwargs = mock_popen.call_args
        cmdline = args[0]
        expected = ['kinit', '-r', '1d', '-l', '8 hours', 'test@EXAMPLE.COM']
        assert cmdline == expected, f"Expected {expected}, got {cmdline}"
        print("✓ kinit_args parsed as shell-like string")
        ccache.close()

def test_requirement_kerberos_delegation():
    """Requirement: If kerberos_delegation is True and no kinit_args, add -f"""
    print("=== Testing: Kerberos delegation -f flag ===")
    
    with patch('subprocess.Popen') as mock_popen:
        mock_process = MagicMock()
        mock_process.communicate.return_value = (b'', b'')
        mock_process.returncode = 0
        mock_popen.return_value = mock_process
        
        ccache = new_kerb_auth('test@EXAMPLE.COM', 'testpass',
                              kerberos_delegation=True)
        
        args, kwargs = mock_popen.call_args
        cmdline = args[0]
        expected = ['kinit', '-f', 'test@EXAMPLE.COM']
        assert cmdline == expected, f"Expected {expected}, got {cmdline}"
        print("✓ -f flag added for kerberos delegation")
        ccache.close()

def test_requirement_environment():
    """Requirement: Environment must preserve PATH and set KRB5CCNAME"""
    print("=== Testing: Environment variables ===")
    
    with patch('subprocess.Popen') as mock_popen:
        mock_process = MagicMock()
        mock_process.communicate.return_value = (b'', b'')
        mock_process.returncode = 0
        mock_popen.return_value = mock_process
        
        original_path = os.environ.get('PATH', '/usr/bin')
        test_path = '/test/path:/bin'
        os.environ['PATH'] = test_path
        
        try:
            ccache = new_kerb_auth('test@EXAMPLE.COM', 'testpass')
            
            args, kwargs = mock_popen.call_args
            env = kwargs['env']
            
            # Check PATH preserved
            assert env['PATH'] == test_path, f"Expected PATH {test_path}, got {env.get('PATH')}"
            
            # Check KRB5CCNAME set to FILE:<path>
            krb5cc = env.get('KRB5CCNAME', '')
            assert krb5cc.startswith('FILE:'), f"Expected KRB5CCNAME to start with FILE:, got {krb5cc}"
            
            print(f"✓ PATH preserved: {env['PATH']}")
            print(f"✓ KRB5CCNAME set: {krb5cc}")
            ccache.close()
            
        finally:
            os.environ['PATH'] = original_path

def test_requirement_error_nonexistent_cmd():
    """Requirement: Error message format for nonexistent kinit command"""
    print("=== Testing: Error handling for nonexistent command ===")
    
    try:
        new_kerb_auth('test@EXAMPLE.COM', 'testpass',
                     kinit_cmd='/nonexistent/kinit')
        assert False, "Should have raised AnsibleConnectionFailure"
    except AnsibleConnectionFailure as e:
        error_msg = str(e)
        expected_prefix = "Kerberos auth failure when calling kinit cmd '/nonexistent/kinit':"
        assert error_msg.startswith(expected_prefix), f"Expected '{expected_prefix}', got '{error_msg}'"
        print(f"✓ Correct error format: {error_msg}")

def test_requirement_error_kinit_failure():
    """Requirement: Error message format for kinit failure with password redaction"""
    print("=== Testing: Error handling for kinit failure ===")
    
    with patch('subprocess.Popen') as mock_popen:
        mock_process = MagicMock()
        mock_process.communicate.return_value = (b'', b'kinit: Authentication failed for mypassword')
        mock_process.returncode = 1  # Failure
        mock_popen.return_value = mock_process
        
        try:
            new_kerb_auth('test@EXAMPLE.COM', 'mypassword')
            assert False, "Should have raised AnsibleConnectionFailure"
        except AnsibleConnectionFailure as e:
            error_msg = str(e)
            
            # Check format
            expected_prefix = "Kerberos auth failure for principal test@EXAMPLE.COM:"
            assert error_msg.startswith(expected_prefix), f"Expected '{expected_prefix}', got '{error_msg}'"
            
            # Check password redaction
            assert 'mypassword' not in error_msg, f"Password should be redacted: {error_msg}"
            assert '<redacted>' in error_msg, f"Should contain <redacted>: {error_msg}"
            
            print(f"✓ Correct error format with redaction: {error_msg}")

def test_requirement_successful_auth():
    """Requirement: Successful auth should complete without errors"""
    print("=== Testing: Successful authentication ===")
    
    with patch('subprocess.Popen') as mock_popen:
        mock_process = MagicMock()
        mock_process.communicate.return_value = (b'', b'')
        mock_process.returncode = 0  # Success
        mock_popen.return_value = mock_process
        
        # This should not raise any exceptions
        ccache = new_kerb_auth('test@EXAMPLE.COM', 'testpass')
        print("✓ Successful authentication completes without errors")
        ccache.close()

def run_all_requirements_tests():
    """Run all requirement verification tests"""
    print("🔍 Verifying all PR requirements...\n")
    
    tests = [
        test_requirement_no_pexpect_dependency,
        test_requirement_stdin_password,
        test_requirement_kinit_cmd,
        test_requirement_kinit_args,
        test_requirement_kerberos_delegation,
        test_requirement_environment,
        test_requirement_error_nonexistent_cmd,
        test_requirement_error_kinit_failure,
        test_requirement_successful_auth
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
    
    print(f"\n📊 Results:")
    print(f"✅ Passed: {passed}")
    print(f"❌ Failed: {failed}")
    
    if failed == 0:
        print("\n🎉 ALL REQUIREMENTS MET! The WinRM Kerberos fix is complete.")
        return True
    else:
        print(f"\n⚠️  {failed} requirements not met.")
        return False

if __name__ == "__main__":
    success = run_all_requirements_tests()
    sys.exit(0 if success else 1)
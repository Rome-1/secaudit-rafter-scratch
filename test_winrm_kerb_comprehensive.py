#!/usr/bin/env python3

"""
Comprehensive test script to verify the WinRM Kerberos fix
handles all the requirements from the PR description.
"""

import os
import sys
import tempfile
import subprocess
import shlex
from unittest.mock import patch, MagicMock

# Add the lib path to import the winrm plugin
sys.path.insert(0, '/app/lib')

from ansible.plugins.connection.winrm import Connection
from ansible.errors import AnsibleConnectionFailure
from ansible.module_utils.common.text.converters import to_text, to_bytes, to_native

def test_kinit_cmd_option():
    """Test that ansible_winrm_kinit_cmd option is respected"""
    print("\n=== Testing kinit_cmd option ===")
    
    # Mock the connection with custom kinit command
    conn = Connection()
    conn.set_options(var_options={
        'kerberos_command': '/custom/path/to/kinit',
        'kinit_args': None,
        'kinit_env_vars': [],
        '_extras': {}
    })
    conn._build_winrm_kwargs()
    
    assert conn._kinit_cmd == '/custom/path/to/kinit', f"Expected custom kinit cmd, got {conn._kinit_cmd}"
    print("✓ Custom kinit_cmd option respected")

def test_kinit_args_option():
    """Test that ansible_winrm_kinit_args option is respected"""
    print("\n=== Testing kinit_args option ===")
    
    # Mock subprocess to capture the command line
    with patch('subprocess.Popen') as mock_popen:
        mock_process = MagicMock()
        mock_process.communicate.return_value = (b'', b'')
        mock_process.returncode = 0
        mock_popen.return_value = mock_process
        
        conn = Connection()
        conn.set_options(var_options={
            'kerberos_command': 'echo',  # Use echo for testing
            'kinit_args': '-r 1d -l 8h',
            'kinit_env_vars': [],
            '_extras': {}
        })
        conn._build_winrm_kwargs()
        
        # Call the _kerb_auth method
        conn._kerb_auth('testuser@EXAMPLE.COM', 'testpass')
        
        # Verify the command line includes the args
        args, kwargs = mock_popen.call_args
        cmdline = args[0]
        expected_args = ['echo', '-r', '1d', '-l', '8h', 'testuser@EXAMPLE.COM']
        
        assert cmdline == expected_args, f"Expected {expected_args}, got {cmdline}"
        print("✓ kinit_args option respected and parsed correctly")

def test_kerberos_delegation():
    """Test that kerberos_delegation adds -f flag when no kinit_args specified"""
    print("\n=== Testing kerberos delegation ===")
    
    with patch('subprocess.Popen') as mock_popen:
        mock_process = MagicMock()
        mock_process.communicate.return_value = (b'', b'')
        mock_process.returncode = 0
        mock_popen.return_value = mock_process
        
        conn = Connection()
        conn.set_options(var_options={
            'kerberos_command': 'echo',
            'kinit_args': None,  # No explicit args
            'kinit_env_vars': [],
            '_extras': {'ansible_winrm_kerberos_delegation': True}
        })
        conn._build_winrm_kwargs()
        
        conn._kerb_auth('testuser@EXAMPLE.COM', 'testpass')
        
        args, kwargs = mock_popen.call_args
        cmdline = args[0]
        expected_args = ['echo', '-f', 'testuser@EXAMPLE.COM']
        
        assert cmdline == expected_args, f"Expected {expected_args}, got {cmdline}"
        print("✓ Kerberos delegation adds -f flag correctly")

def test_environment_variables():
    """Test that PATH and KRB5CCNAME environment variables are set correctly"""
    print("\n=== Testing environment variables ===")
    
    with patch('subprocess.Popen') as mock_popen:
        mock_process = MagicMock()
        mock_process.communicate.return_value = (b'', b'')
        mock_process.returncode = 0
        mock_popen.return_value = mock_process
        
        conn = Connection()
        conn.set_options(var_options={
            'kerberos_command': 'echo',
            'kinit_args': None,
            'kinit_env_vars': [],
            '_extras': {}
        })
        conn._build_winrm_kwargs()
        
        # Set a test PATH
        original_path = os.environ.get('PATH', '')
        test_path = '/test/path:/another/path'
        os.environ['PATH'] = test_path
        
        try:
            conn._kerb_auth('testuser@EXAMPLE.COM', 'testpass')
            
            args, kwargs = mock_popen.call_args
            env = kwargs['env']
            
            # Check PATH is preserved
            assert env['PATH'] == test_path, f"Expected PATH {test_path}, got {env.get('PATH')}"
            
            # Check KRB5CCNAME is set to FILE:<path>
            krb5cc = env.get('KRB5CCNAME', '')
            assert krb5cc.startswith('FILE:'), f"Expected KRB5CCNAME to start with 'FILE:', got {krb5cc}"
            
            print(f"✓ PATH preserved: {env['PATH']}")
            print(f"✓ KRB5CCNAME set correctly: {krb5cc}")
            
        finally:
            os.environ['PATH'] = original_path

def test_error_handling_nonexistent_command():
    """Test error handling when kinit command doesn't exist"""
    print("\n=== Testing error handling for nonexistent command ===")
    
    conn = Connection()
    conn.set_options(var_options={
        'kerberos_command': '/nonexistent/kinit/command',
        'kinit_args': None,
        'kinit_env_vars': [],
        '_extras': {}
    })
    conn._build_winrm_kwargs()
    
    try:
        conn._kerb_auth('testuser@EXAMPLE.COM', 'testpass')
        assert False, "Expected AnsibleConnectionFailure to be raised"
    except AnsibleConnectionFailure as e:
        error_msg = str(e)
        expected_prefix = "Kerberos auth failure when calling kinit cmd '/nonexistent/kinit/command':"
        assert error_msg.startswith(expected_prefix), f"Expected error to start with '{expected_prefix}', got '{error_msg}'"
        print(f"✓ Correct error message for nonexistent command: {error_msg}")

def test_error_handling_kinit_failure():
    """Test error handling when kinit exits with non-zero code"""
    print("\n=== Testing error handling for kinit failure ===")
    
    with patch('subprocess.Popen') as mock_popen:
        mock_process = MagicMock()
        mock_process.communicate.return_value = (b'', b'Authentication failed for testpass')
        mock_process.returncode = 1  # Non-zero exit code
        mock_popen.return_value = mock_process
        
        conn = Connection()
        conn.set_options(var_options={
            'kerberos_command': 'echo',
            'kinit_args': None,
            'kinit_env_vars': [],
            '_extras': {}
        })
        conn._build_winrm_kwargs()
        
        try:
            conn._kerb_auth('testuser@EXAMPLE.COM', 'testpass')
            assert False, "Expected AnsibleConnectionFailure to be raised"
        except AnsibleConnectionFailure as e:
            error_msg = str(e)
            # Check that password is redacted
            assert 'testpass' not in error_msg, f"Password should be redacted in error message: {error_msg}"
            assert '<redacted>' in error_msg, f"Expected '<redacted>' in error message: {error_msg}"
            assert 'Kerberos auth failure for principal testuser@EXAMPLE.COM:' in error_msg
            print(f"✓ Correct error message with password redaction: {error_msg}")

def test_no_pexpect_dependency():
    """Test that the implementation doesn't use pexpect even if available"""
    print("\n=== Testing no pexpect dependency ===")
    
    # Mock pexpect as available and verify it's not used
    with patch('ansible.plugins.connection.winrm.HAS_PEXPECT', True):
        with patch('subprocess.Popen') as mock_popen:
            mock_process = MagicMock()
            mock_process.communicate.return_value = (b'', b'')
            mock_process.returncode = 0
            mock_popen.return_value = mock_process
            
            conn = Connection()
            conn.set_options(var_options={
                'kerberos_command': 'echo',
                'kinit_args': None,
                'kinit_env_vars': [],
                '_extras': {}
            })
            conn._build_winrm_kwargs()
            
            conn._kerb_auth('testuser@EXAMPLE.COM', 'testpass')
            
            # Verify subprocess.Popen was called (not pexpect)
            assert mock_popen.called, "subprocess.Popen should be called"
            print("✓ Uses subprocess even when pexpect is available")

def test_kinit_env_vars():
    """Test that kinit_env_vars are passed through correctly"""
    print("\n=== Testing kinit_env_vars option ===")
    
    with patch('subprocess.Popen') as mock_popen:
        mock_process = MagicMock()
        mock_process.communicate.return_value = (b'', b'')
        mock_process.returncode = 0
        mock_popen.return_value = mock_process
        
        # Set some test environment variables
        os.environ['TEST_VAR1'] = 'test_value1'
        os.environ['TEST_VAR2'] = 'test_value2'
        
        conn = Connection()
        conn.set_options(var_options={
            'kerberos_command': 'echo',
            'kinit_args': None,
            'kinit_env_vars': ['TEST_VAR1', 'TEST_VAR2', 'NONEXISTENT_VAR'],
            '_extras': {}
        })
        conn._build_winrm_kwargs()
        
        try:
            conn._kerb_auth('testuser@EXAMPLE.COM', 'testpass')
            
            args, kwargs = mock_popen.call_args
            env = kwargs['env']
            
            # Check that specified env vars are included
            assert env.get('TEST_VAR1') == 'test_value1', f"Expected TEST_VAR1=test_value1, got {env.get('TEST_VAR1')}"
            assert env.get('TEST_VAR2') == 'test_value2', f"Expected TEST_VAR2=test_value2, got {env.get('TEST_VAR2')}"
            # Nonexistent vars should not be included
            assert 'NONEXISTENT_VAR' not in env, f"NONEXISTENT_VAR should not be in env: {env}"
            
            print("✓ kinit_env_vars passed through correctly")
            
        finally:
            del os.environ['TEST_VAR1']
            del os.environ['TEST_VAR2']

def test_successful_auth():
    """Test successful authentication flow"""
    print("\n=== Testing successful authentication ===")
    
    with patch('subprocess.Popen') as mock_popen:
        mock_process = MagicMock()
        mock_process.communicate.return_value = (b'', b'')
        mock_process.returncode = 0
        mock_popen.return_value = mock_process
        
        conn = Connection()
        conn.set_options(var_options={
            'kerberos_command': 'echo',
            'kinit_args': None,
            'kinit_env_vars': [],
            '_extras': {}
        })
        conn._build_winrm_kwargs()
        
        # This should not raise any exceptions
        conn._kerb_auth('testuser@EXAMPLE.COM', 'testpass')
        
        # Verify the password was sent to stdin
        args, kwargs = mock_popen.call_args
        mock_process.communicate.assert_called_once_with(b'testpass\n')
        
        print("✓ Successful authentication completes without errors")

def run_all_tests():
    """Run all test functions"""
    test_functions = [
        test_kinit_cmd_option,
        test_kinit_args_option,
        test_kerberos_delegation,
        test_environment_variables,
        test_error_handling_nonexistent_command,
        test_error_handling_kinit_failure,
        test_no_pexpect_dependency,
        test_kinit_env_vars,
        test_successful_auth
    ]
    
    passed = 0
    failed = 0
    
    for test_func in test_functions:
        try:
            test_func()
            passed += 1
        except Exception as e:
            print(f"✗ {test_func.__name__} FAILED: {e}")
            failed += 1
    
    print(f"\n=== Test Results ===")
    print(f"Passed: {passed}")
    print(f"Failed: {failed}")
    
    if failed > 0:
        sys.exit(1)
    else:
        print("All tests passed! 🎉")

if __name__ == "__main__":
    run_all_tests()
#!/usr/bin/env python3

"""
Test edge cases for the WinRM Kerberos fix
"""

import os
import sys
import tempfile
from unittest.mock import patch, MagicMock

sys.path.insert(0, '/app/lib')

from ansible.module_utils.common.text.converters import to_text, to_bytes, to_native
from ansible.module_utils.parsing.convert_bool import boolean
from ansible.errors import AnsibleConnectionFailure
from ansible.utils.display import Display

display = Display()

# Import the _kerb_auth method from the actual module
from ansible.plugins.connection.winrm import Connection

def test_edge_case_empty_password():
    """Test handling of empty/None passwords"""
    print("=== Testing: Empty and None passwords ===")
    
    # Create a minimal connection instance
    from ansible.playbook.play_context import PlayContext
    from io import StringIO
    
    with patch('subprocess.Popen') as mock_popen:
        mock_process = MagicMock()
        mock_process.communicate.return_value = (b'', b'')
        mock_process.returncode = 0
        mock_popen.return_value = mock_process
        
        try:
            # Test with None password
            conn = Connection(PlayContext(), StringIO())
            conn.set_options(var_options={'kerberos_command': 'echo', 'kinit_args': None, 'kinit_env_vars': [], '_extras': {}})
            conn._build_winrm_kwargs()
            conn._kerb_auth("test@EXAMPLE.COM", None)
            
            # Verify empty password was sent
            call_args = mock_process.communicate.call_args[0]
            assert call_args == (b'\n',), f"Expected empty password + newline, got {call_args}"
            
            # Test with empty string password  
            mock_process.communicate.reset_mock()
            conn._kerb_auth("test@EXAMPLE.COM", "")
            call_args = mock_process.communicate.call_args[0]
            assert call_args == (b'\n',), f"Expected empty password + newline, got {call_args}"
            
            print("✓ Empty and None passwords handled correctly")
            
        except Exception as e:
            print(f"✗ Failed: {e}")
            raise

def test_edge_case_unicode_password():
    """Test handling of unicode passwords"""
    print("=== Testing: Unicode passwords ===")
    
    with patch('subprocess.Popen') as mock_popen:
        mock_process = MagicMock()
        mock_process.communicate.return_value = (b'', b'')
        mock_process.returncode = 0
        mock_popen.return_value = mock_process
        
        try:
            from ansible.playbook.play_context import PlayContext
            from io import StringIO
            
            conn = Connection(PlayContext(), StringIO())
            conn.set_options(var_options={'kerberos_command': 'echo', 'kinit_args': None, 'kinit_env_vars': [], '_extras': {}})
            conn._build_winrm_kwargs()
            
            # Test with unicode password
            unicode_password = "pässwørd123"
            conn._kerb_auth("test@EXAMPLE.COM", unicode_password)
            
            # Verify unicode password was properly encoded
            call_args = mock_process.communicate.call_args[0]
            expected = unicode_password.encode('utf-8') + b'\n'
            assert call_args == (expected,), f"Expected {expected}, got {call_args}"
            
            print("✓ Unicode passwords handled correctly")
            
        except Exception as e:
            print(f"✗ Failed: {e}")
            raise

def test_edge_case_complex_kinit_args():
    """Test complex kinit_args with quotes and special characters"""
    print("=== Testing: Complex kinit_args ===")
    
    with patch('subprocess.Popen') as mock_popen:
        mock_process = MagicMock()
        mock_process.communicate.return_value = (b'', b'')
        mock_process.returncode = 0
        mock_popen.return_value = mock_process
        
        try:
            from ansible.playbook.play_context import PlayContext
            from io import StringIO
            
            conn = Connection(PlayContext(), StringIO())
            conn.set_options(var_options={
                'kerberos_command': 'kinit',
                'kinit_args': '-r 1d -S "krbtgt/OTHER.REALM@OTHER.REALM" -c FILE:/tmp/custom',
                'kinit_env_vars': [],
                '_extras': {}
            })
            conn._build_winrm_kwargs()
            conn._kerb_auth("test@EXAMPLE.COM", "testpass")
            
            # Check command line was parsed correctly
            args, kwargs = mock_popen.call_args
            cmdline = args[0]
            expected = [
                'kinit', '-r', '1d', '-S', 'krbtgt/OTHER.REALM@OTHER.REALM',
                '-c', 'FILE:/tmp/custom', 'test@EXAMPLE.COM'
            ]
            assert cmdline == expected, f"Expected {expected}, got {cmdline}"
            
            print("✓ Complex kinit_args parsed correctly")
            
        except Exception as e:
            print(f"✗ Failed: {e}")
            raise

def test_edge_case_password_in_error_with_special_chars():
    """Test password redaction when password contains regex special characters"""
    print("=== Testing: Password redaction with special chars ===")
    
    with patch('subprocess.Popen') as mock_popen:
        mock_process = MagicMock()
        # Error message that includes the password with special regex chars
        special_password = "p@ss[w0rd]+(123).*^$"
        mock_process.communicate.return_value = (
            b'', 
            f"Authentication failed with password: {special_password}".encode('utf-8')
        )
        mock_process.returncode = 1
        mock_popen.return_value = mock_process
        
        try:
            from ansible.playbook.play_context import PlayContext
            from io import StringIO
            
            conn = Connection(PlayContext(), StringIO())
            conn.set_options(var_options={'kerberos_command': 'echo', 'kinit_args': None, 'kinit_env_vars': [], '_extras': {}})
            conn._build_winrm_kwargs()
            
            conn._kerb_auth("test@EXAMPLE.COM", special_password)
            assert False, "Should have raised AnsibleConnectionFailure"
            
        except AnsibleConnectionFailure as e:
            error_msg = str(e)
            # Password should be redacted even with special chars
            assert special_password not in error_msg, f"Password should be redacted: {error_msg}"
            assert '<redacted>' in error_msg, f"Should contain <redacted>: {error_msg}"
            print(f"✓ Special character password redacted: {error_msg}")

def test_edge_case_kinit_args_override_delegation():
    """Test that explicit kinit_args override kerberos_delegation"""
    print("=== Testing: kinit_args override delegation ===")
    
    with patch('subprocess.Popen') as mock_popen:
        mock_process = MagicMock()
        mock_process.communicate.return_value = (b'', b'')
        mock_process.returncode = 0
        mock_popen.return_value = mock_process
        
        try:
            from ansible.playbook.play_context import PlayContext
            from io import StringIO
            
            conn = Connection(PlayContext(), StringIO())
            conn.set_options(var_options={
                'kerberos_command': 'kinit',
                'kinit_args': '-r 2d',  # Explicit args
                'kinit_env_vars': [],
                '_extras': {'ansible_winrm_kerberos_delegation': True}  # Should be ignored
            })
            conn._build_winrm_kwargs()
            conn._kerb_auth("test@EXAMPLE.COM", "testpass")
            
            # Should use explicit args, not add -f for delegation
            args, kwargs = mock_popen.call_args
            cmdline = args[0]
            expected = ['kinit', '-r', '2d', 'test@EXAMPLE.COM']
            assert cmdline == expected, f"Expected {expected}, got {cmdline}"
            assert '-f' not in cmdline, f"-f should not be added when kinit_args specified: {cmdline}"
            
            print("✓ Explicit kinit_args override kerberos_delegation")
            
        except Exception as e:
            print(f"✗ Failed: {e}")
            raise

def test_edge_case_missing_path_env():
    """Test handling when PATH environment variable is missing"""
    print("=== Testing: Missing PATH environment ===")
    
    with patch('subprocess.Popen') as mock_popen:
        mock_process = MagicMock()
        mock_process.communicate.return_value = (b'', b'')
        mock_process.returncode = 0
        mock_popen.return_value = mock_process
        
        # Temporarily remove PATH
        original_path = os.environ.get('PATH')
        if 'PATH' in os.environ:
            del os.environ['PATH']
        
        try:
            from ansible.playbook.play_context import PlayContext
            from io import StringIO
            
            conn = Connection(PlayContext(), StringIO())
            conn.set_options(var_options={'kerberos_command': 'echo', 'kinit_args': None, 'kinit_env_vars': [], '_extras': {}})
            conn._build_winrm_kwargs()
            conn._kerb_auth("test@EXAMPLE.COM", "testpass")
            
            # Check that environment was set up with empty PATH
            args, kwargs = mock_popen.call_args
            env = kwargs['env']
            assert 'PATH' in env, "PATH should be in environment"
            assert env['PATH'] == "", f"PATH should be empty string, got '{env['PATH']}'"
            
            print("✓ Missing PATH handled correctly (set to empty string)")
            
        except Exception as e:
            print(f"✗ Failed: {e}")
            raise
        finally:
            if original_path is not None:
                os.environ['PATH'] = original_path

def run_edge_case_tests():
    """Run all edge case tests"""
    print("🔬 Testing edge cases...\n")
    
    tests = [
        test_edge_case_empty_password,
        test_edge_case_unicode_password,
        test_edge_case_complex_kinit_args,
        test_edge_case_password_in_error_with_special_chars,
        test_edge_case_kinit_args_override_delegation,
        test_edge_case_missing_path_env
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
    
    print(f"\n📊 Edge Case Results:")
    print(f"✅ Passed: {passed}")
    print(f"❌ Failed: {failed}")
    
    if failed == 0:
        print("\n🎯 All edge cases handled correctly!")
        return True
    else:
        print(f"\n⚠️  {failed} edge cases need attention.")
        return False

if __name__ == "__main__":
    success = run_edge_case_tests()
    sys.exit(0 if success else 1)
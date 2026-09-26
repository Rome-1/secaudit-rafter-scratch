import os
import sys
import tempfile

# Ensure we can import the local ansible package
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'lib'))

from ansible.plugins.connection import winrm as winrm_conn

# Simple harness to call the private _kerb_auth method with a dummy self
class DummyConn:
    def __init__(self, kinit_cmd='kinit', kinit_args=None, extras=None, kinit_env_vars=None):
        self._kinit_cmd = kinit_cmd
        self._opts = {
            'kinit_args': kinit_args,
            '_extras': extras or {},
            'kinit_env_vars': kinit_env_vars or [],
        }
        self._kerb_ccache = None

    def get_option(self, name):
        return self._opts.get(name)


def run_creation_failure_case():
    # Use a definitely non-existent command to trigger OSError path
    dummy = DummyConn(kinit_cmd='/this/definitely/does/not/exist')
    try:
        winrm_conn.Connection._kerb_auth(dummy, 'user@EXAMPLE.COM', 'secret')
    except Exception as e:
        print('creation_failure_msg:', str(e))
    else:
        print('creation_failure_did_not_raise')


class StubPopen:
    def __init__(self, argv, stdin=None, stdout=None, stderr=None, env=None, **kwargs):
        # capture for assertions
        self.argv = argv
        self.env = env or {}
        self.stdin = stdin
        self.stdout = stdout
        self.stderr = stderr
        self.kwargs = kwargs
        self._returncode = 1
        self._stderr = b''

    def communicate(self, input=None):
        # always pretend that stderr includes the password
        self._stderr = b'authentication failed for password: ' + (input or b'')
        return (b'', self._stderr)

    @property
    def returncode(self):
        return self._returncode


def run_nonzero_exit_case():
    # Monkeypatch subprocess.Popen in the module
    orig_popen = winrm_conn.subprocess.Popen
    try:
        winrm_conn.subprocess.Popen = StubPopen
        dummy = DummyConn(kinit_cmd='kinit')
        try:
            winrm_conn.Connection._kerb_auth(dummy, 'user@EXAMPLE.COM', 'secret')
        except Exception as e:
            print('nonzero_exit_msg:', str(e))
        else:
            print('nonzero_exit_did_not_raise')
    finally:
        winrm_conn.subprocess.Popen = orig_popen


class StubPopenSuccess(StubPopen):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._returncode = 0

    def communicate(self, input=None):
        return (b'', b'')


def run_success_case_and_cmd_build():
    # Monkeypatch subprocess.Popen to a success stub that captures argv/env
    orig_popen = winrm_conn.subprocess.Popen
    try:
        captured = {}
        def factory(argv, **kwargs):
            p = StubPopenSuccess(argv, **kwargs)
            captured['argv'] = argv
            captured['env'] = kwargs.get('env', {})
            captured['kwargs'] = kwargs
            return p
        winrm_conn.subprocess.Popen = factory

        extras = {'ansible_winrm_kerberos_delegation': True}
        kinit_args = None
        dummy = DummyConn(kinit_cmd='kinit', kinit_args=kinit_args, extras=extras)
        winrm_conn.Connection._kerb_auth(dummy, 'user@EXAMPLE.COM', 'secret')

        argv = captured['argv']
        print('built_cmd:', argv)
        print('env_vars:', {'PATH': captured['env'].get('PATH'), 'KRB5CCNAME': captured['env'].get('KRB5CCNAME')})
        print('kwargs:', list(captured['kwargs'].keys()))
    finally:
        winrm_conn.subprocess.Popen = orig_popen


if __name__ == '__main__':
    run_creation_failure_case()
    run_nonzero_exit_case()
    run_success_case_and_cmd_build()

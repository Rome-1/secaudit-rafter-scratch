import sys
import unittest
from unittest.mock import patch

class TestAnsibleCli(unittest.TestCase):
    def test_python_version(self):
        with patch.object(sys, 'version_info', (3, 10, 0)):
            with self.assertRaises(SystemExit) as cm:
                import ansible.cli
            self.assertTrue(str(cm.exception).startswith("ERROR: Ansible requires Python 3.11 or newer on the controller. Current version:"))

if __name__ == '__main__':
    unittest.main()

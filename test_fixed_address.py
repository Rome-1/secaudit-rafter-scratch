import json
from ansible.module_utils.basic import AnsibleModule
from lib.ansible.modules.net_tools.nios.nios_fixed_address import main as nios_fixed_address_main
from io import BytesIO
import sys

# Mock the JSON input to the module
params = {
    "ANSIBLE_MODULE_ARGS": {
        "ipaddr": "192.168.0.10",
        "mac": "00:11:22:33:44:55",
        "network": "192.168.0.0/24",
        "state": "present",
        "provider": {
            "host": "nios.example.com",
            "username": "admin",
            "password": "admin"
        }
    }
}

sys.stdin = BytesIO(json.dumps(params).encode('utf-8'))

# Capture output
sys.stdout = BytesIO()

try:
    nios_fixed_address_main()
except SystemExit as e:
    # Print module result
    print(sys.stdout.getvalue())
    sys.stdout = sys.__stdout__
    sys.stderr = sys.__stderr__

# Reset sys.stdin
sys.stdin = sys.__stdin__

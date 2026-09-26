import json
import sys
from lib.ansible.modules.net_tools.nios.nios_fixed_address import main as nios_fixed_address_main

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

if __name__ == '__main__':
    # Use a temporary file to simulate standard input
    import tempfile
    with tempfile.NamedTemporaryFile(mode='w+', delete=False) as temp_file:
        json.dump(params, temp_file)
        temp_file.flush()
        temp_file.seek(0)

        # Redirect standard input to the temporary file
        sys.stdin = temp_file
        
        # Capture output
        sys.stdout = sys.stderr = open('/dev/null', 'w')

        # Execute main function of the module
        nios_fixed_address_main()

        # Restore standard input/output
        sys.stdin = sys.__stdin__
        sys.stdout = sys.__stdout__
        sys.stderr = sys.__stderr__

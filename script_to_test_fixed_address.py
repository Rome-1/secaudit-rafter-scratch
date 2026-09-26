from ansible.utils.display import Display
from ansible.module_utils.basic import AnsibleModule
from lib.ansible.modules.net_tools.nios.nios_fixed_address import main as nios_fixed_address_main
import sys

# Mocking sys.argv
sys.argv = ['ansible', 'localhost', '-m', 'nios_fixed_address']

# Mocking the parameters that will be passed to the module
params = {
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

display = Display()
module = AnsibleModule(
    argument_spec={
        "ipaddr": {"required": True, "type": "str"},
        "mac": {"required": True, "type": "str"},
        "network": {"required": True, "type": "str"},
        "network_view": {"default": "default", "type": "str"},
        "options": {"type": "list", "elements": "dict"},
        "extattrs": {"type": "dict"},
        "comment": {"type": "str"},
        "state": {"default": "present", "choices": ["present", "absent"]},
        "provider": {"required": True, "type": "dict"}
    },
    supports_check_mode=True
)
module.params = params
nios_fixed_address_main()

import sys
sys.path.insert(0, '/app/lib')
from types import SimpleNamespace

from ansible.module_utils.net_tools.nios import api
from ansible.modules.net_tools.nios import nios_fixed_address as mod

# Patch connector to avoid needing infoblox-client
api.get_connector = lambda **kwargs: SimpleNamespace()

# Test constants exist
print('Constants:', api.NIOS_IPV4_FIXED_ADDRESS, api.NIOS_IPV6_FIXED_ADDRESS)

# Build module params for IPv4
params_v4 = {
    'provider': {},
    'state': 'present',
    'name': 'host1',
    'ipaddr': '192.0.2.10',
    'mac': '00:11:22:33:44:55',
    'network': '192.0.2.0/24',
    'network_view': 'default',
    'options': [
        {'name': 'domain-name', 'value': 'example.com', 'num': None},
        {'num': 15, 'value': 'example.com'}
    ],
    'extattrs': None,
    'comment': 'test'
}

class DummyModule:
    def __init__(self, params):
        self.params = params
        self.check_mode = False
    def fail_json(self, **kwargs):
        raise Exception(kwargs['msg'])

# Validate options transformation
mod_module = DummyModule(params_v4.copy())
opts = mod.options(mod_module)
assert isinstance(opts, list) and opts[0]['name'] == 'domain-name' and 'num' not in opts[0]
assert opts[0]['use_option'] is True and opts[0]['vendor_class'] == 'DHCP'

# Validate IP version routing and remapping for IPv4
ib_spec = {
    'name': {'required': True},
    'ipaddr': {'required': True, 'ib_req': True},
    'mac': {'required': True, 'ib_req': True},
    'network': {'required': True, 'ib_req': True},
    'network_view': {'default': 'default'},
}
nios_type, ib_spec2, mod_module2 = mod.validate_ip_addr_type('192.0.2.10', ib_spec.copy(), DummyModule(params_v4.copy()))
assert nios_type == api.NIOS_IPV4_FIXED_ADDRESS
assert 'ipv4addr' in ib_spec2 and 'ipaddr' not in ib_spec2

# Validate get_object_ref uses mac filter for fixedaddress
w = api.WapiModule(DummyModule(params_v4.copy()))
used_filter = {}

def fake_get_object(obj_type, filt, return_fields=None):
    used_filter.update(filt)
    return None

w.get_object = fake_get_object
w.get_object_ref(w.module, api.NIOS_IPV4_FIXED_ADDRESS, {'mac': params_v4['mac'], 'network': params_v4['network']}, {'name': {}, 'mac': {}, 'network': {}})
assert used_filter.get('mac') == params_v4['mac']
print('All checks passed.')

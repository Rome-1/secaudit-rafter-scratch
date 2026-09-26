#!/usr/bin/python
# Copyright (c) 2023
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function
__metaclass__ = type

ANSIBLE_METADATA = {
    'metadata_version': '1.1',
    'status': ['preview'],
    'supported_by': 'community'
}

DOCUMENTATION = '''
---
module: nios_fixed_address
author: "Your Name (@yourhandle)"
short_description: Manage Infoblox NIOS fixed addresses
description:
  - Adds, updates, or removes instances of fixed addresses in a NIOS (Infoblox) server.
options:
  ipaddr:
    description:
      - IPv4 or IPv6 address for the fixed address.
    required: true
  mac:
    description:
      - MAC address associated with the fixed address.
    required: true
  network:
    description:
      - Network in which the fixed address resides.
    required: true
  network_view:
    description:
      - Network view used for the fixed address.
    default: 'default'
  options:
    description:
      - List of DHCP options for the fixed address.
    type: list
    elements: dict
  extattrs:
    description:
      - Extensible attributes for the fixed address.
    type: dict
  comment:
    description:
      - Comment for the fixed address.
    type: str
  state:
    description:
      - The desired state of the fixed address.
    default: present
    choices:
      - present
      - absent
requirements:
  - infoblox-client
'''

EXAMPLES = '''
- name: Reserve a fixed address
  nios_fixed_address:
    ipaddr: 192.168.0.10
    mac: "00:11:22:33:44:55"
    network: 192.168.0.0/24
    state: present
    provider:
      host: "nios.example.com"
      username: "admin"
      password: "admin"

- name: Remove a fixed address
  nios_fixed_address:
    ipaddr: 192.168.0.10
    mac: "00:11:22:33:44:55"
    network: 192.168.0.0/24
    state: absent
    provider:
      host: "nios.example.com"
      username: "admin"
      password: "admin"
'''

RETURN = ''' # '''

from ansible.module_utils.basic import AnsibleModule
from ansible.module_utils.net_tools.nios.api import WapiModule
from ansible.module_utils.net_tools.nios.api import NIOS_IPV4_FIXED_ADDRESS, NIOS_IPV6_FIXED_ADDRESS
from ansible.module_utils.network.common.utils import validate_ip_address, validate_ip_v6_address


def main():
    argument_spec = dict(
        ipaddr=dict(required=True),
        mac=dict(required=True),
        network=dict(required=True),
        network_view=dict(default='default'),
        options=dict(type='list', elements='dict'),
        extattrs=dict(type='dict'),
        comment=dict(type='str'),
        state=dict(default='present', choices=['present', 'absent']),
        provider=dict(required=True)
    )

    module = AnsibleModule(argument_spec=argument_spec,
                           supports_check_mode=True)

    ip_type = NIOS_IPV4_FIXED_ADDRESS if validate_ip_address(module.params['ipaddr']) else NIOS_IPV6_FIXED_ADDRESS if validate_ip_v6_address(module.params['ipaddr']) else None
    if ip_type is None:
        module.fail_json(msg='Invalid IP address provided.')

    wapi = WapiModule(module)

    result = wapi.run(ip_type, module.params)

    module.exit_json(**result)


if __name__ == '__main__':
    main()

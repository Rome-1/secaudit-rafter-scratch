#!/usr/bin/python
# Copyright (c) 2025 Red Hat, Inc. and contributors
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function
__metaclass__ = type

ANSIBLE_METADATA = {'metadata_version': '1.1',
                    'status': ['preview'],
                    'supported_by': 'certified'}

DOCUMENTATION = '''
---
module: nios_fixed_address
short_description: Manage Infoblox DHCP Fixed Address (IPv4/IPv6)
description:
  - Create, update, or delete Infoblox DHCP Fixed Address entries for IPv4 and IPv6.
  - Supports idempotent operations to avoid duplicate entries.
version_added: "2.14"
author:
  - "Community"
requirements:
  - infoblox-client
extends_documentation_fragment: nios
options:
  name:
    description:
      - Host name/commental identifier to associate with the fixed address.
    required: true
  ipaddr:
    description:
      - IP address for the fixed address entry. Can be IPv4 or IPv6.
    required: true
    aliases: [ ip ]
  mac:
    description:
      - MAC address associated with the fixed address entry.
    required: true
  network:
    description:
      - Network in CIDR notation that contains the IP address.
    required: true
  network_view:
    description:
      - Network view where the fixed address resides.
    default: default
  options:
    description:
      - DHCP options to associate with the fixed address. Each option must include
        at least one of C(name) or C(num), and a C(value).
    type: list
    elements: dict
    suboptions:
      name:
        description:
          - Name of the DHCP option.
      num:
        description:
          - Numeric code for the DHCP option.
        type: int
      value:
        description:
          - Value of the DHCP option.
        required: true
      use_option:
        description:
          - Only applies to a subset of options (see NIOS API documentation).
        type: bool
        default: true
      vendor_class:
        description:
          - Space this DHCP option belongs to.
        default: DHCP
  extattrs:
    description:
      - Extensible Attributes for this object as key/value pairs.
    type: dict
  comment:
    description:
      - Comment to associate with the fixed address object.
  state:
    description:
      - Desired state of the object on the NIOS server.
    default: present
    choices: [ present, absent ]
'''

EXAMPLES = '''
- name: Create an IPv4 fixed address
  nios_fixed_address:
    name: web01
    ipaddr: 192.0.2.10
    mac: 00:11:22:33:44:55
    network: 192.0.2.0/24
    options:
      - name: domain-name
        value: example.com
    state: present
    provider:
      host: "{{ inventory_hostname_short }}"
      username: admin
      password: admin
  connection: local

- name: Remove a fixed address
  nios_fixed_address:
    name: web01
    ipaddr: 192.0.2.10
    mac: 00:11:22:33:44:55
    network: 192.0.2.0/24
    state: absent
    provider:
      host: "{{ inventory_hostname_short }}"
      username: admin
      password: admin
  connection: local
'''

RETURN = ''' # '''

from ansible.module_utils.basic import AnsibleModule
from ansible.module_utils.six import iteritems
from ansible.module_utils.net_tools.nios.api import WapiModule
from ansible.module_utils.net_tools.nios.api import NIOS_IPV4_FIXED_ADDRESS, NIOS_IPV6_FIXED_ADDRESS
from ansible.module_utils.network.common.utils import validate_ip_address, validate_ip_v6_address


def options(module):
    '''
    Convert the options list into WAPI compatible structures.
    Ensures either `name` or `num` is present and strips None values.
    '''
    if module.params.get('options') is None:
        return None

    sanitized = []
    for item in module.params['options']:
        opt = dict((k, v) for k, v in iteritems(item) if v is not None)
        if 'name' not in opt and 'num' not in opt:
            module.fail_json(msg='one of `name` or `num` is required for option value')
        if 'use_option' not in opt:
            opt['use_option'] = True
        if 'vendor_class' not in opt:
            opt['vendor_class'] = 'DHCP'
        sanitized.append(opt)
    return sanitized


def validate_ip_addr_type(ip, arg_spec, module):
    '''
    Validate IP version and adjust arg_spec/module params accordingly.
    Returns a tuple of (NIOS object type, updated arg_spec, updated module).
    '''
    if ip is None:
        module.fail_json(msg='ipaddr is required')

    if validate_ip_address(ip):
        # IPv4
        nios_type = NIOS_IPV4_FIXED_ADDRESS
        # Move ipaddr to ipv4addr param for WAPI
        module.params['ipv4addr'] = module.params.get('ipaddr')
        module.params['ipv6addr'] = None
        # Update arg spec mapping: use ipv4addr instead of ipaddr
        arg_spec['ipv4addr'] = dict(ib_req=True)
        if 'ipaddr' in arg_spec:
            del arg_spec['ipaddr']
    elif validate_ip_v6_address(ip):
        # IPv6
        nios_type = NIOS_IPV6_FIXED_ADDRESS
        module.params['ipv6addr'] = module.params.get('ipaddr')
        module.params['ipv4addr'] = None
        arg_spec['ipv6addr'] = dict(ib_req=True)
        if 'ipaddr' in arg_spec:
            del arg_spec['ipaddr']
    else:
        module.fail_json(msg='invalid IP address supplied for ipaddr: %s' % ip)

    return nios_type, arg_spec, module


def main():
    # Initial ib_spec includes ipaddr/mac/network as ib_req for early filter building
    option_spec = dict(
        name=dict(),
        num=dict(type='int'),
        value=dict(required=True),
        use_option=dict(type='bool', default=True),
        vendor_class=dict(default='DHCP')
    )

    ib_spec = dict(
        # Required identifiers/metadata
        name=dict(required=True),
        ipaddr=dict(required=True, ib_req=True, aliases=['ip']),
        mac=dict(required=True, ib_req=True),
        network=dict(required=True, ib_req=True),
        network_view=dict(default='default'),

        # Optional features
        options=dict(type='list', elements='dict', options=option_spec, transform=options),
        extattrs=dict(type='dict'),
        comment=dict(),
    )

    argument_spec = dict(
        provider=dict(required=True),
        state=dict(default='present', choices=['present', 'absent'])
    )

    argument_spec.update(ib_spec)
    argument_spec.update(WapiModule.provider_spec)

    module = AnsibleModule(argument_spec=argument_spec,
                           supports_check_mode=True)

    # Build pre-remap obj_filter from ib_req=True fields (ipaddr, mac, network)
    # as required by the PR. This is computed before address field remap.
    _ = dict((k, module.params[k]) for k, v in iteritems(ib_spec) if v.get('ib_req'))

    # Remap ipaddr -> ipv4addr/ipv6addr and choose the proper WAPI object type
    nios_type, ib_spec, module = validate_ip_addr_type(module.params.get('ipaddr'), ib_spec, module)

    # Now run the module against the appropriate object type
    wapi = WapiModule(module)
    result = wapi.run(nios_type, ib_spec)

    module.exit_json(**result)


if __name__ == '__main__':
    main()

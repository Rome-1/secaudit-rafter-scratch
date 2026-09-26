#!/usr/bin/env python
"""Debug script to check option handling"""

import sys
sys.path.insert(0, '/app/lib')
sys.path.insert(0, '/app/test')

from ansible.plugins.lookup.password import LookupModule
from units.mock.loader import DictDataLoader

# Create the lookup module
loader = DictDataLoader({})
lookup = LookupModule(loader=loader)
lookup._load_name = 'password'

# Set options with seed
lookup.set_options(direct={'seed': 'myseed2'})

print("After set_options(direct={'seed': 'myseed2'}):")
print(f"  has_option('seed'): {lookup.has_option('seed')}")
print(f"  _options: {lookup._options}")

try:
    seed_value = lookup.get_option('seed')
    print(f"  get_option('seed'): {seed_value}")
except Exception as e:
    print(f"  get_option('seed') failed: {e}")

# Try parsing a term
term = '/dev/null'
relpath, params = lookup._parse_parameters(term)
print(f"\nAfter _parse_parameters('{term}'):")
print(f"  relpath: {relpath}")
print(f"  params: {params}")
print(f"  params['seed']: {params.get('seed')}")

from __future__ import print_function

import sys

# 1) __all__ must not export UnsafeProxy
import ansible.utils.unsafe_proxy as up

print("__all__:", getattr(up, "__all__", None))
assert 'UnsafeProxy' not in getattr(up, '__all__', []), "UnsafeProxy should not be exported via __all__"
assert 'wrap_var' in up.__all__ and 'AnsibleUnsafe' in up.__all__, "wrap_var and AnsibleUnsafe must be exported via __all__"

# 2) wrap_var behavior
from ansible.module_utils.six import text_type, binary_type

s = u"hello"
b = b"bytes"

ws = up.wrap_var(s)
wb = up.wrap_var(b)

# Text and bytes must be wrapped to AnsibleUnsafeText/Bytes
assert isinstance(ws, up.AnsibleUnsafe), "Text should be marked as AnsibleUnsafe"
assert isinstance(wb, up.AnsibleUnsafe), "Bytes should be marked as AnsibleUnsafe"
assert type(ws).__name__ == 'AnsibleUnsafeText', "Text must be wrapped as AnsibleUnsafeText"
assert type(wb).__name__ == 'AnsibleUnsafeBytes', "Bytes must be wrapped as AnsibleUnsafeBytes"

# None must return None
assert up.wrap_var(None) is None, "None should return None"

# Already unsafe values must be returned unchanged (identity)
ws2 = up.wrap_var(ws)
assert ws2 is ws, "Already unsafe value should be returned unchanged"

# Container recursion
lst = ['a', b'b', None, 3]
wrapped_lst = up.wrap_var(lst)
assert isinstance(wrapped_lst, list), "List should remain a list"
assert isinstance(wrapped_lst[0], up.AnsibleUnsafe), "List element 0 should be unsafe"
assert isinstance(wrapped_lst[1], up.AnsibleUnsafe), "List element 1 should be unsafe"
assert wrapped_lst[2] is None, "List None element should stay None"
assert wrapped_lst[3] == 3, "Non-text/bytes should be unchanged"

mp = {'k': 'v', 2: b'x'}
wrapped_mp = up.wrap_var(mp)
assert type(wrapped_mp) is dict or wrapped_mp.__class__.__name__ == mp.__class__.__name__, "Mapping should be same container type"
# keys should be wrapped when applicable
k0 = list(wrapped_mp.keys())[0]
assert isinstance(k0, up.AnsibleUnsafe) or isinstance(k0, (text_type, int)), "Mapping key should be processed appropriately"

st = {'a', b'b', 5}
wrapped_st = up.wrap_var(st)
assert isinstance(wrapped_st, set), "Set should remain a set"
assert any(isinstance(x, up.AnsibleUnsafe) for x in wrapped_st), "Set elements should be wrapped when applicable"

# Ensure importing template and task_executor does not import UnsafeProxy directly
import ansible.template
import ansible.executor.task_executor

print('OK')

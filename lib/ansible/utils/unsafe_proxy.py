# PYTHON SOFTWARE FOUNDATION LICENSE VERSION 2
# --------------------------------------------
#
# 1. This LICENSE AGREEMENT is between the Python Software Foundation
# ("PSF"), and the Individual or Organization ("Licensee") accessing and
# otherwise using this software ("Python") in source or binary form and
# its associated documentation.
#
# 2. Subject to the terms and conditions of this License Agreement, PSF hereby
# grants Licensee a nonexclusive, royalty-free, world-wide license to reproduce,
# analyze, test, perform and/or display publicly, prepare derivative works,
# distribute, and otherwise use Python alone or in any derivative version,
# provided, however, that PSF's License Agreement and PSF's notice of copyright,
# i.e., "Copyright (c) 2001, 2002, 2003, 2004, 2005, 2006, 2007, 2008, 2009, 2010,
# 2011, 2012, 2013, 2014 Python Software Foundation; All Rights Reserved" are
# retained in Python alone or in any derivative version prepared by Licensee.
#
# 3. In the event Licensee prepares a derivative work that is based on
# or incorporates Python or any part thereof, and wants to make
# the derivative work available to others as provided herein, then
# Licensee hereby agrees to include in any such work a brief summary of
# the changes made to Python.
#
# 4. PSF is making Python available to Licensee on an "AS IS"
# basis.  PSF MAKES NO REPRESENTATIONS OR WARRANTIES, EXPRESS OR
# IMPLIED.  BY WAY OF EXAMPLE, BUT NOT LIMITATION, PSF MAKES NO AND
# DISCLAIMS ANY REPRESENTATION OR WARRANTY OF MERCHANTABILITY OR FITNESS
# FOR ANY PARTICULAR PURPOSE OR THAT THE USE OF PYTHON WILL NOT
# INFRINGE ANY THIRD PARTY RIGHTS.
#
# 5. PSF SHALL NOT BE LIABLE TO LICENSEE OR ANY OTHER USERS OF PYTHON
# FOR ANY INCIDENTAL, SPECIAL, OR CONSEQUENTIAL DAMAGES OR LOSS AS
# A RESULT OF MODIFYING, DISTRIBUTING, OR OTHERWISE USING PYTHON,
# OR ANY DERIVATIVE THEREOF, EVEN IF ADVISED OF THE POSSIBILITY THEREOF.
#
# 6. This License Agreement will automatically terminate upon a material
# breach of its terms and conditions.
#
# 7. Nothing in this License Agreement shall be deemed to create any
# relationship of agency, partnership, or joint venture between PSF and
# Licensee.  This License Agreement does not grant permission to use PSF
# trademarks or trade name in a trademark sense to endorse or promote
# products or services of Licensee, or any third party.
#
# 8. By copying, installing or otherwise using Python, Licensee
# agrees to be bound by the terms and conditions of this License
# Agreement.
#
# Original Python Recipe for Proxy:
# http://code.activestate.com/recipes/496741-object-proxying/
# Author: Tomer Filiba

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

from ansible.module_utils.six import string_types, text_type, binary_type
from ansible.module_utils._text import to_text
from ansible.module_utils.common._collections_compat import Mapping, MutableSequence, Set


__all__ = ['AnsibleUnsafe', 'wrap_var']


class AnsibleUnsafe(object):
    __UNSAFE__ = True


class AnsibleUnsafeText(text_type, AnsibleUnsafe):
    pass


class AnsibleUnsafeBytes(binary_type, AnsibleUnsafe):
    pass


class UnsafeProxy(object):
    def __new__(cls, obj, *args, **kwargs):
        # In our usage we should only receive unicode strings.
        # This conditional and conversion exists to sanity check the values
        # we're given but we may want to take it out for testing and sanitize
        # our input instead.
        if isinstance(obj, string_types) and not isinstance(obj, AnsibleUnsafeBytes):
            obj = AnsibleUnsafeText(to_text(obj, errors='surrogate_or_strict'))
        return obj


def _wrap_dict(v):
    # Rebuild mapping with wrapped keys and values, preserving container type
    try:
        items = list(v.items())
    except AttributeError:
        # Fallback for non-standard mappings without items()
        items = [(k, v[k]) for k in list(v.keys())]
    new_map = type(v)()
    for k, val in items:
        new_k = wrap_var(k)
        new_v = val if val is None else wrap_var(val)
        new_map[new_k] = new_v
    # Try to update in place when possible to preserve original instance
    try:
        v.clear()
        v.update(new_map)
        return v
    except Exception:
        return new_map


def _wrap_list(v):
    for idx, item in enumerate(v):
        if item is not None:
            v[idx] = wrap_var(item)
    return v


def _wrap_set(v):
    try:
        return type(v)(item if item is None else wrap_var(item) for item in v)
    except Exception:
        # Fallback to built-in set if constructor is not iterable-friendly
        return set(item if item is None else wrap_var(item) for item in v)


def wrap_var(v):
    """Single entry point to mark a value as unsafe.

    Behavior:
    - If v is already an AnsibleUnsafe instance, return it unchanged.
    - If v is a Mapping, MutableSequence, or Set, return the same container
      type with all contained elements recursively processed by wrap_var.
    - If v is binary_type (bytes), return AnsibleUnsafeBytes(v).
    - If v is text_type (unicode/str), return AnsibleUnsafeText(v).
    - If v is None, return None without wrapping.
    - For all other values, return as-is.
    """
    # Already unsafe? Leave as-is
    if isinstance(v, AnsibleUnsafe):
        return v

    # None remains None
    if v is None:
        return None

    # Recurse through containers
    if isinstance(v, Mapping):
        return _wrap_dict(v)
    elif isinstance(v, MutableSequence):
        return _wrap_list(v)
    elif isinstance(v, Set):
        return _wrap_set(v)

    # Wrap primitive text/bytes
    if isinstance(v, binary_type):
        return AnsibleUnsafeBytes(v)
    elif isinstance(v, string_types):
        return AnsibleUnsafeText(to_text(v, errors='surrogate_or_strict'))

    # Other types returned unchanged
    return v

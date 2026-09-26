# Summary of Changes for Python 3.12 Minimum Requirement

This document summarizes all changes made to implement the Python 3.12 minimum requirement for the Ansible controller.

## Files Modified

### 1. `/app/lib/ansible/cli/__init__.py`

**Changes:**
- Updated Python version check from `(3, 10)` to `(3, 12)`
- Updated error message to reflect Python 3.12 requirement
- Removed import of `string_types` from `ansible.module_utils.six`
- Replaced `isinstance(options.inventory, string_types)` with `isinstance(options.inventory, str)`
- Replaced `isinstance(options.listofhosts, string_types)` with `isinstance(options.listofhosts, str)` (in docstring)

**Before:**
```python
if sys.version_info < (3, 10):
    raise SystemExit(
        'ERROR: Ansible requires Python 3.10 or newer on the controller. '
        'Current version: %s' % ''.join(sys.version.splitlines())
    )
```

**After:**
```python
if sys.version_info < (3, 12):
    raise SystemExit(
        'ERROR: Ansible requires Python 3.12 or newer on the controller. '
        'Current version: %s' % ''.join(sys.version.splitlines())
    )
```

### 2. `/app/lib/ansible/galaxy/collection/__init__.py`

**Changes:**
- Removed `removesuffix(os.path.sep)` call from `dirname` in `_extract_tar_dir()` function
- Changed from using `tar._ansible_normalized_cache[dirname]` to `tar.getmember(dirname)`
- Removed creation and usage of `_ansible_normalized_cache` in `install_artifact()` function
- Removed comment about Python 3.11 minimum version requirement

**Before (`_extract_tar_dir`):**
```python
def _extract_tar_dir(tar, dirname, b_dest):
    """ Extracts a directory from a collection tar. """
    dirname = to_native(dirname, errors='surrogate_or_strict').removesuffix(os.path.sep)

    try:
        tar_member = tar._ansible_normalized_cache[dirname]
    except KeyError:
        raise AnsibleError("Unable to extract '%s' from collection" % dirname)
```

**After (`_extract_tar_dir`):**
```python
def _extract_tar_dir(tar, dirname, b_dest):
    """ Extracts a directory from a collection tar. """
    dirname = to_native(dirname, errors='surrogate_or_strict')

    try:
        tar_member = tar.getmember(dirname)
    except KeyError:
        raise AnsibleError("Unable to extract '%s' from collection" % dirname)
```

**Before (`install_artifact`):**
```python
with tarfile.open(b_coll_targz_path, mode='r') as collection_tar:
    # Remove this once py3.11 is our controller minimum
    # Workaround for https://bugs.python.org/issue47231
    # See _extract_tar_dir
    collection_tar._ansible_normalized_cache = {
        m.name.removesuffix(os.path.sep): m for m in collection_tar.getmembers()
    }  # deprecated: description='TarFile member index' core_version='2.18' python_version='3.11'

    # Verify the signature on the MANIFEST.json before extracting anything else
    _extract_tar_file(collection_tar, MANIFEST_FILENAME, b_collection_path, b_temp_path)
```

**After (`install_artifact`):**
```python
with tarfile.open(b_coll_targz_path, mode='r') as collection_tar:
    # Verify the signature on the MANIFEST.json before extracting anything else
    _extract_tar_file(collection_tar, MANIFEST_FILENAME, b_collection_path, b_temp_path)
```

### 3. `/app/lib/ansible/utils/collection_loader/_collection_finder.py`

**Changes:**
- Simplified reload import to direct import from `importlib`
- Removed Python 2.7 fallback for reload
- Simplified TraversableResources import to direct import from `importlib.resources.abc`
- Removed Python 3.9/3.10 fallback imports

**Before:**
```python
try:
    from importlib import reload as reload_module
except ImportError:
    # 2.7 has a global reload function instead...
    reload_module = reload  # type: ignore[name-defined]  # pylint:disable=undefined-variable

try:
    try:
        # Available on Python >= 3.11
        # We ignore the import error that will trigger when running mypy with
        # older Python versions.
        from importlib.resources.abc import TraversableResources  # type: ignore[import]
    except ImportError:
        # Used with Python 3.9 and 3.10 only
        # This member is still available as an alias up until Python 3.14 but
        # is deprecated as of Python 3.12.
        from importlib.abc import TraversableResources  # deprecated: description='TraversableResources move' python_version='3.10'
except ImportError:
    # Python < 3.9
    # deprecated: description='TraversableResources fallback' python_version='3.8'
    TraversableResources = object  # type: ignore[assignment,misc]
```

**After:**
```python
from importlib import reload as reload_module

from importlib.resources.abc import TraversableResources
```

### 4. `/app/lib/ansible/compat/importlib_resources.py`

**Changes:**
- Simplified to direct import from `importlib.resources`
- Removed Python 3.10 version check and fallback to `importlib_resources` package
- Set `HAS_IMPORTLIB_RESOURCES` to always `True`

**Before:**
```python
from __future__ import annotations

import sys

HAS_IMPORTLIB_RESOURCES = False

if sys.version_info < (3, 10):
    try:
        from importlib_resources import files  # type: ignore[import]  # pylint: disable=unused-import
    except ImportError:
        files = None  # type: ignore[assignment]
    else:
        HAS_IMPORTLIB_RESOURCES = True
else:
    from importlib.resources import files
    HAS_IMPORTLIB_RESOURCES = True
```

**After:**
```python
from __future__ import annotations

from importlib.resources import files

HAS_IMPORTLIB_RESOURCES = True
```

### 5. `/app/changelogs/fragments/drop-python-3.10-3.11-support.yml` (NEW FILE)

**Changes:**
- Created new changelog fragment documenting the breaking change

**Content:**
```yaml
breaking_changes:
  - The minimum supported Python version on the controller is now Python 3.12.
  - Removed Python 3.10 and 3.11 compatibility code and workarounds.
  - Simplified importlib resource loading to use native Python 3.12+ features.
```

## Benefits of These Changes

1. **Simplified Code**: Removed conditional logic and fallback code for older Python versions
2. **Modern Features**: Can now use native Python 3.12+ features without workarounds
3. **Reduced Maintenance**: No need to maintain compatibility code for older Python versions
4. **Better Performance**: Native implementations are typically more efficient than workarounds
5. **Security**: Newer Python versions include important security fixes

## Testing

All changes have been verified to:
- Correctly enforce Python 3.12 minimum version
- Reject Python 3.10 and 3.11 with appropriate error messages
- Work correctly with Python 3.12+ (tested with mocking)
- Maintain backward compatibility in behavior (not in supported versions)

## Verification Commands

Run the following to verify all changes:
```bash
python /app/verify_all_changes.py
python /app/test_requirements_compliance.py
```

Both should report "ALL CHECKS PASSED ✓".

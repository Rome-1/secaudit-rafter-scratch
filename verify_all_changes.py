#!/usr/bin/env python3
"""Comprehensive verification of all changes made for Python 3.12 minimum requirement."""

import ast
import sys
import os

def check_version_check():
    """Check that Python 3.12 version check is in place."""
    print("=" * 70)
    print("Checking Python version enforcement in CLI...")
    print("=" * 70)
    
    with open('/app/lib/ansible/cli/__init__.py', 'r') as f:
        content = f.read()
    
    checks = [
        ("sys.version_info < (3, 12)", "✓ Enforces Python 3.12 minimum version"),
        ("Python 3.12 or newer", "✓ Correct error message for Python 3.12"),
    ]
    
    failures = []
    for check_str, success_msg in checks:
        if check_str in content:
            print(success_msg)
        else:
            failures.append(f"✗ Missing: {check_str}")
    
    # Check that old references are removed
    if "3.10" in content:
        failures.append("✗ Still contains reference to Python 3.10")
    else:
        print("✓ No Python 3.10 references")
    
    return len(failures) == 0, failures

def check_string_types_replacement():
    """Check that string_types is replaced with str."""
    print("\n" + "=" * 70)
    print("Checking string_types replacement in CLI...")
    print("=" * 70)
    
    with open('/app/lib/ansible/cli/__init__.py', 'r') as f:
        content = f.read()
    
    failures = []
    
    # Check that string_types import is removed
    if 'from ansible.module_utils.six import string_types' in content:
        failures.append("✗ string_types import still exists")
    else:
        print("✓ string_types import removed")
    
    # Check that isinstance uses str
    if 'isinstance(options.inventory, str)' in content:
        print("✓ isinstance uses str for inventory")
    else:
        failures.append("✗ isinstance doesn't use str for inventory")
    
    if 'isinstance(options.listofhosts, str)' in content:
        print("✓ isinstance uses str for listofhosts")
    else:
        # Check if it exists at all
        if 'listofhosts' not in content:
            print("  (listofhosts not found in isinstance - might be in docstring only)")
        else:
            failures.append("✗ isinstance doesn't use str for listofhosts")
    
    return len(failures) == 0, failures

def check_galaxy_collection_changes():
    """Check galaxy collection changes."""
    print("\n" + "=" * 70)
    print("Checking galaxy collection changes...")
    print("=" * 70)
    
    with open('/app/lib/ansible/galaxy/collection/__init__.py', 'r') as f:
        content = f.read()
    
    failures = []
    
    # Check removesuffix is not used on dirname in _extract_tar_dir
    if 'dirname = to_native(dirname, errors=\'surrogate_or_strict\').removesuffix' in content:
        failures.append("✗ removesuffix still used on dirname")
    else:
        print("✓ removesuffix not used on dirname")
    
    # Check tar.getmember is used
    if 'tar.getmember(dirname)' in content:
        print("✓ tar.getmember(dirname) is used")
    else:
        failures.append("✗ tar.getmember(dirname) not found")
    
    # Check _ansible_normalized_cache is not used
    if '_ansible_normalized_cache' in content:
        failures.append("✗ _ansible_normalized_cache still exists")
    else:
        print("✓ _ansible_normalized_cache removed")
    
    # Check old Python version comments are removed
    if 'py3.11' in content.lower() or 'python 3.11' in content.lower():
        failures.append("✗ Python 3.11 references still exist")
    else:
        print("✓ Python 3.11 references removed")
    
    if 'py3.10' in content.lower() or 'python 3.10' in content.lower():
        failures.append("✗ Python 3.10 references still exist")
    else:
        print("✓ Python 3.10 references removed")
    
    return len(failures) == 0, failures

def check_reload_import():
    """Check reload import."""
    print("\n" + "=" * 70)
    print("Checking reload import in collection finder...")
    print("=" * 70)
    
    with open('/app/lib/ansible/utils/collection_loader/_collection_finder.py', 'r') as f:
        content = f.read()
    
    failures = []
    
    # Check direct import
    if 'from importlib import reload as reload_module' in content:
        print("✓ Direct import from importlib")
    else:
        failures.append("✗ Direct import from importlib not found")
    
    # Check that old try/except is removed
    if '# 2.7 has a global reload function' in content:
        failures.append("✗ Old Python 2.7 reload fallback still exists")
    else:
        print("✓ Python 2.7 reload fallback removed")
    
    return len(failures) == 0, failures

def check_importlib_resources():
    """Check importlib_resources simplification."""
    print("\n" + "=" * 70)
    print("Checking importlib_resources simplification...")
    print("=" * 70)
    
    with open('/app/lib/ansible/compat/importlib_resources.py', 'r') as f:
        content = f.read()
    
    failures = []
    
    # Check direct import
    if 'from importlib.resources import files' in content:
        print("✓ Direct import from importlib.resources")
    else:
        failures.append("✗ Direct import from importlib.resources not found")
    
    # Check old version check is removed
    if 'sys.version_info < (3, 10)' in content:
        failures.append("✗ Old Python 3.10 version check still exists")
    else:
        print("✓ Old Python 3.10 version check removed")
    
    return len(failures) == 0, failures

def check_traversable_resources():
    """Check TraversableResources simplification."""
    print("\n" + "=" * 70)
    print("Checking TraversableResources simplification...")
    print("=" * 70)
    
    with open('/app/lib/ansible/utils/collection_loader/_collection_finder.py', 'r') as f:
        content = f.read()
    
    failures = []
    
    # Check direct import
    if 'from importlib.resources.abc import TraversableResources' in content:
        print("✓ Direct import from importlib.resources.abc")
    else:
        failures.append("✗ Direct import from importlib.resources.abc not found")
    
    # Check old version comments are removed
    if '# Python < 3.9' in content or '# Used with Python 3.9 and 3.10' in content:
        failures.append("✗ Old Python version comments still exist")
    else:
        print("✓ Old Python version comments removed")
    
    return len(failures) == 0, failures

def check_changelog():
    """Check that changelog fragment exists."""
    print("\n" + "=" * 70)
    print("Checking changelog fragment...")
    print("=" * 70)
    
    changelog_path = '/app/changelogs/fragments/drop-python-3.10-3.11-support.yml'
    
    if os.path.exists(changelog_path):
        print("✓ Changelog fragment exists")
        with open(changelog_path, 'r') as f:
            content = f.read()
            if 'Python 3.12' in content:
                print("✓ Changelog mentions Python 3.12")
                return True, []
            else:
                return False, ["✗ Changelog doesn't mention Python 3.12"]
    else:
        return False, ["✗ Changelog fragment doesn't exist"]

def main():
    """Run all checks."""
    print("\n" + "=" * 70)
    print("VERIFICATION OF PYTHON 3.12 MINIMUM REQUIREMENT CHANGES")
    print("=" * 70)
    
    all_checks = [
        ("Python version check", check_version_check),
        ("string_types replacement", check_string_types_replacement),
        ("Galaxy collection changes", check_galaxy_collection_changes),
        ("reload import", check_reload_import),
        ("importlib_resources simplification", check_importlib_resources),
        ("TraversableResources simplification", check_traversable_resources),
        ("Changelog fragment", check_changelog),
    ]
    
    results = {}
    for check_name, check_func in all_checks:
        success, failures = check_func()
        results[check_name] = (success, failures)
    
    # Print summary
    print("\n" + "=" * 70)
    print("SUMMARY")
    print("=" * 70)
    
    all_passed = True
    for check_name, (success, failures) in results.items():
        if success:
            print(f"✓ {check_name}: PASSED")
        else:
            print(f"✗ {check_name}: FAILED")
            for failure in failures:
                print(f"  {failure}")
            all_passed = False
    
    print("\n" + "=" * 70)
    if all_passed:
        print("ALL CHECKS PASSED ✓")
        print("=" * 70)
        return 0
    else:
        print("SOME CHECKS FAILED ✗")
        print("=" * 70)
        return 1

if __name__ == '__main__':
    sys.exit(main())

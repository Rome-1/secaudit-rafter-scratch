#!/usr/bin/env python3

"""
Script to test the implementation of calendar editing controls restrictions.

This script verifies that the changes were correctly implemented according to the PR requirements.
"""

import os
import re

def check_file_contains_pattern(file_path, patterns):
    """Check if file contains all specified patterns."""
    try:
        with open(file_path, 'r') as f:
            content = f.read()
        
        results = {}
        for pattern_name, pattern in patterns.items():
            if isinstance(pattern, str):
                results[pattern_name] = pattern in content
            else:
                results[pattern_name] = bool(re.search(pattern, content, re.MULTILINE | re.DOTALL))
        
        return results
    except Exception as e:
        print(f"Error reading {file_path}: {e}")
        return None

def main():
    print("=== Testing Calendar Editing Controls Implementation ===")
    print()
    
    # Test CalendarMemberAndInvitationList.tsx changes
    print("1. Testing CalendarMemberAndInvitationList.tsx changes...")
    list_file = "/app/packages/components/containers/calendar/settings/CalendarMemberAndInvitationList.tsx"
    list_patterns = {
        "canEdit_prop_in_interface": "canEdit?: boolean;",
        "canEdit_default_parameter": "canEdit = true,",
        "canEdit_passed_to_member_row": "canEdit={canEdit}",
    }
    
    list_results = check_file_contains_pattern(list_file, list_patterns)
    if list_results:
        for check, passed in list_results.items():
            status = "✓ PASS" if passed else "✗ FAIL"
            print(f"  {check}: {status}")
    else:
        print("  ✗ FAIL: Could not read file")
    
    print()
    
    # Test CalendarMemberRow.tsx changes
    print("2. Testing CalendarMemberRow.tsx changes...")
    row_file = "/app/packages/components/containers/calendar/settings/CalendarMemberRow.tsx"
    row_patterns = {
        "canEdit_prop_in_row_interface": "canEdit?: boolean;",
        "canEdit_default_in_destructuring": "canEdit = true,",
        "disabled_permission_select": "disabled={!canEdit}",
    }
    
    row_results = check_file_contains_pattern(row_file, row_patterns)
    if row_results:
        for check, passed in row_results.items():
            status = "✓ PASS" if passed else "✗ FAIL"
            print(f"  {check}: {status}")
    else:
        print("  ✗ FAIL: Could not read file")
    
    print()
    
    # Check that delete buttons are not disabled (by checking no disabled prop is added)
    print("3. Testing that delete buttons remain enabled...")
    with open(row_file, 'r') as f:
        content = f.read()
    
    # Check that the delete button doesn't have disabled={!canEdit} or similar
    delete_button_section = content[content.find('<Button icon shape="ghost"'):content.find('</Button>') + 9]
    delete_not_disabled = 'disabled=' not in delete_button_section
    
    status = "✓ PASS" if delete_not_disabled else "✗ FAIL"
    print(f"  delete_button_not_disabled: {status}")
    
    delete_results = {"delete_button_not_disabled": delete_not_disabled}
    
    print()
    
    # Overall assessment
    all_checks = []
    if list_results:
        all_checks.extend(list_results.values())
    if row_results:
        all_checks.extend(row_results.values())
    if delete_results:
        all_checks.extend(delete_results.values())
    
    if all_checks and all(all_checks):
        print("🎉 ALL TESTS PASSED! The implementation meets the PR requirements.")
        return 0
    else:
        print("❌ SOME TESTS FAILED. Please review the implementation.")
        return 1

if __name__ == "__main__":
    exit(main())
#!/usr/bin/env python3
"""
Comprehensive test to verify the implementation meets all requirements
"""

import re

def test_requirement_1():
    """
    Requirement 1: The CalendarMemberAndInvitationList component should accept 
    a canEdit boolean prop to control edit permissions.
    """
    file_path = "/app/packages/components/containers/calendar/settings/CalendarMemberAndInvitationList.tsx"
    
    with open(file_path, 'r') as f:
        content = f.read()
    
    # Check interface has canEdit prop
    interface_match = re.search(r'interface MemberAndInvitationListProps.*?{.*?canEdit\?:\s*boolean', content, re.DOTALL)
    if not interface_match:
        return False, "canEdit prop not found in MemberAndInvitationListProps interface"
    
    # Check component accepts canEdit in props
    props_match = re.search(r'const CalendarMemberAndInvitationList.*?canEdit\s*=\s*true', content, re.DOTALL)
    if not props_match:
        return False, "canEdit not destructured with default value in component props"
    
    return True, "canEdit prop properly defined with default value of true"

def test_requirement_2():
    """
    Requirement 2: When canEdit is false, permission change buttons 
    (role/access level selectors) should be disabled.
    """
    file_path = "/app/packages/components/containers/calendar/settings/CalendarMemberRow.tsx"
    
    with open(file_path, 'r') as f:
        content = f.read()
    
    # Check that SelectTwo components have disabled={!canEdit}
    disabled_matches = re.findall(r'<SelectTwo[^>]*disabled=\{!canEdit\}', content)
    if len(disabled_matches) < 2:
        return False, f"Expected at least 2 SelectTwo components with disabled={{!canEdit}}, found {len(disabled_matches)}"
    
    return True, f"Found {len(disabled_matches)} SelectTwo components with disabled={{!canEdit}}"

def test_requirement_3():
    """
    Requirement 3: When canEdit is false, member removal actions should remain enabled.
    """
    file_path = "/app/packages/components/containers/calendar/settings/CalendarMemberRow.tsx"
    
    with open(file_path, 'r') as f:
        content = f.read()
    
    # Check that delete button doesn't have disabled prop based on canEdit
    # We look for the Button component that calls handleDelete
    button_match = re.search(r'<Button[^>]*onClick=\{handleDelete\}[^>]*>', content)
    if not button_match:
        return False, "Delete button not found"
    
    button_str = button_match.group(0)
    if 'disabled={!canEdit}' in button_str or 'disabled={canEdit}' in button_str:
        return False, "Delete button should not be disabled based on canEdit"
    
    return True, "Delete button remains enabled regardless of canEdit value"

def test_requirement_4():
    """
    Requirement 4: The component should properly handle both canEdit states 
    without affecting the display of existing member and invitation data.
    """
    list_file = "/app/packages/components/containers/calendar/settings/CalendarMemberAndInvitationList.tsx"
    row_file = "/app/packages/components/containers/calendar/settings/CalendarMemberRow.tsx"
    
    with open(list_file, 'r') as f:
        list_content = f.read()
    
    with open(row_file, 'r') as f:
        row_content = f.read()
    
    # Check that canEdit is passed to CalendarMemberRow in both places (members and invitations)
    canEdit_passes = re.findall(r'canEdit=\{canEdit\}', list_content)
    if len(canEdit_passes) < 2:
        return False, f"canEdit should be passed to CalendarMemberRow in at least 2 places, found {len(canEdit_passes)}"
    
    # Check that canEdit has a default value to maintain backward compatibility
    default_in_list = 'canEdit = true' in list_content
    default_in_row = 'canEdit = true' in row_content
    
    if not (default_in_list and default_in_row):
        return False, "canEdit should have default value of true in both components"
    
    return True, "canEdit prop properly handles both states with default value"

def run_all_tests():
    """Run all requirement tests"""
    tests = [
        ("Requirement 1: canEdit prop acceptance", test_requirement_1),
        ("Requirement 2: Permission buttons disabled when canEdit is false", test_requirement_2),
        ("Requirement 3: Delete actions remain enabled", test_requirement_3),
        ("Requirement 4: Proper handling of both canEdit states", test_requirement_4),
    ]
    
    print("Running comprehensive requirement tests...")
    print("=" * 70)
    
    all_passed = True
    for test_name, test_func in tests:
        try:
            passed, message = test_func()
            status = "✓ PASS" if passed else "✗ FAIL"
            print(f"\n{status}: {test_name}")
            print(f"  {message}")
            if not passed:
                all_passed = False
        except Exception as e:
            print(f"\n✗ ERROR: {test_name}")
            print(f"  Exception: {str(e)}")
            all_passed = False
    
    print("\n" + "=" * 70)
    if all_passed:
        print("✓ All requirements met successfully!")
    else:
        print("✗ Some requirements not met. Please review the failures above.")
    
    return all_passed

if __name__ == "__main__":
    run_all_tests()

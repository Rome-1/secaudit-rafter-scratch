#!/usr/bin/env python3
"""
Test edge cases and verify implementation details
"""

import re

def test_default_value():
    """Test that canEdit defaults to true for backward compatibility"""
    list_file = "/app/packages/components/containers/calendar/settings/CalendarMemberAndInvitationList.tsx"
    row_file = "/app/packages/components/containers/calendar/settings/CalendarMemberRow.tsx"
    
    with open(list_file, 'r') as f:
        list_content = f.read()
    
    with open(row_file, 'r') as f:
        row_content = f.read()
    
    # Check default value is true in both components
    list_has_default = re.search(r'canEdit\s*=\s*true', list_content)
    row_has_default = re.search(r'canEdit\s*=\s*true', row_content)
    
    if not list_has_default:
        return False, "CalendarMemberAndInvitationList should have canEdit = true as default"
    
    if not row_has_default:
        return False, "CalendarMemberRow should have canEdit = true as default"
    
    return True, "Both components have canEdit = true as default value"

def test_optional_prop():
    """Test that canEdit is marked as optional"""
    list_file = "/app/packages/components/containers/calendar/settings/CalendarMemberAndInvitationList.tsx"
    row_file = "/app/packages/components/containers/calendar/settings/CalendarMemberRow.tsx"
    
    with open(list_file, 'r') as f:
        list_content = f.read()
    
    with open(row_file, 'r') as f:
        row_content = f.read()
    
    # Check that canEdit? (optional) is used
    list_has_optional = re.search(r'canEdit\?\s*:\s*boolean', list_content)
    row_has_optional = re.search(r'canEdit\?\s*:\s*boolean', row_content)
    
    if not list_has_optional:
        return False, "CalendarMemberAndInvitationList should have canEdit?: boolean"
    
    if not row_has_optional:
        return False, "CalendarMemberRow should have canEdit?: boolean"
    
    return True, "Both components have canEdit as optional prop"

def test_disabled_logic():
    """Test that disabled is correctly set to !canEdit (NOT canEdit)"""
    row_file = "/app/packages/components/containers/calendar/settings/CalendarMemberRow.tsx"
    
    with open(row_file, 'r') as f:
        row_content = f.read()
    
    # Check for disabled={!canEdit}, not disabled={canEdit}
    correct_disabled = re.findall(r'disabled=\{!canEdit\}', row_content)
    incorrect_disabled = re.findall(r'disabled=\{canEdit\}(?!\})', row_content)
    
    if incorrect_disabled:
        return False, f"Found incorrect disabled={{canEdit}} usage: {len(incorrect_disabled)} times"
    
    if len(correct_disabled) < 2:
        return False, f"Expected at least 2 SelectTwo with disabled={{!canEdit}}, found {len(correct_disabled)}"
    
    return True, f"Disabled logic correctly uses !canEdit in {len(correct_disabled)} places"

def test_delete_not_disabled():
    """Test that delete button is not affected by canEdit"""
    row_file = "/app/packages/components/containers/calendar/settings/CalendarMemberRow.tsx"
    
    with open(row_file, 'r') as f:
        row_content = f.read()
    
    # Find the button that calls handleDelete
    delete_button_section = re.search(
        r'<Button[^>]*onClick=\{handleDelete\}[^>]*>.*?</Button>',
        row_content,
        re.DOTALL
    )
    
    if not delete_button_section:
        return False, "Could not find delete button"
    
    button_text = delete_button_section.group(0)
    
    # Ensure it doesn't have disabled prop based on canEdit
    if 'disabled={!canEdit}' in button_text or 'disabled={canEdit}' in button_text:
        return False, "Delete button should not have disabled prop based on canEdit"
    
    # Check that it only has loading disabled, not canEdit disabled
    if 'disabled=' in button_text and 'canEdit' in button_text:
        return False, "Delete button should not reference canEdit for disabled state"
    
    return True, "Delete button remains enabled regardless of canEdit"

def test_prop_passed_to_both_member_types():
    """Test that canEdit is passed to both member rows and invitation rows"""
    list_file = "/app/packages/components/containers/calendar/settings/CalendarMemberAndInvitationList.tsx"
    
    with open(list_file, 'r') as f:
        content = f.read()
    
    # Count how many times canEdit={canEdit} appears in CalendarMemberRow usage
    canEdit_passes = content.count('canEdit={canEdit}')
    
    if canEdit_passes < 2:
        return False, f"Expected canEdit to be passed at least 2 times (members and invitations), found {canEdit_passes}"
    
    # Verify members.map section has CalendarMemberRow with canEdit
    members_section = re.search(r'members\.map.*?return.*?</CalendarMemberRow>', content, re.DOTALL)
    if members_section and 'canEdit={canEdit}' not in members_section.group(0):
        return False, "canEdit not passed to CalendarMemberRow in members.map"
    
    # Verify invitations.map section has CalendarMemberRow with canEdit
    invitations_section = re.search(r'invitations\.map.*?return.*?</CalendarMemberRow>', content, re.DOTALL)
    if invitations_section and 'canEdit={canEdit}' not in invitations_section.group(0):
        return False, "canEdit not passed to CalendarMemberRow in invitations.map"
    
    return True, f"canEdit properly passed {canEdit_passes} times to member and invitation rows"

def test_backward_compatibility():
    """Test that existing usage without canEdit prop still works"""
    share_section = "/app/packages/components/containers/calendar/settings/CalendarShareSection.tsx"
    
    with open(share_section, 'r') as f:
        content = f.read()
    
    # Find the usage of CalendarMemberAndInvitationList
    usage = re.search(
        r'<CalendarMemberAndInvitationList[^>]*/>',
        content,
        re.DOTALL
    )
    
    if not usage:
        return False, "Could not find CalendarMemberAndInvitationList usage"
    
    usage_text = usage.group(0)
    
    # Verify it doesn't require canEdit prop (backward compatible)
    # The component should work without it
    has_required_props = all(
        prop in usage_text 
        for prop in ['members=', 'invitations=', 'calendarID=', 'onDeleteInvitation=', 'onDeleteMember=']
    )
    
    if not has_required_props:
        return False, "Existing usage missing required props"
    
    return True, "Existing usage without canEdit prop remains valid (backward compatible)"

def run_edge_case_tests():
    """Run all edge case tests"""
    tests = [
        ("Default value is true", test_default_value),
        ("canEdit is optional prop", test_optional_prop),
        ("Disabled logic uses !canEdit", test_disabled_logic),
        ("Delete button not affected by canEdit", test_delete_not_disabled),
        ("canEdit passed to both member types", test_prop_passed_to_both_member_types),
        ("Backward compatibility maintained", test_backward_compatibility),
    ]
    
    print("Running edge case tests...")
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
        print("✓ All edge cases handled correctly!")
    else:
        print("✗ Some edge cases not handled. Please review the failures above.")
    
    return all_passed

if __name__ == "__main__":
    run_edge_case_tests()

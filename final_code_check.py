#!/usr/bin/env python3
"""
Final code check to ensure all implementations are correct
"""

def check_implementation():
    errors = []
    warnings = []
    
    # Check CalendarMemberAndInvitationList.tsx
    print("Checking CalendarMemberAndInvitationList.tsx...")
    with open("/app/packages/components/containers/calendar/settings/CalendarMemberAndInvitationList.tsx", "r") as f:
        list_content = f.read()
    
    # 1. Interface should have canEdit?: boolean
    if "canEdit?: boolean;" not in list_content:
        errors.append("CalendarMemberAndInvitationList interface missing 'canEdit?: boolean;'")
    else:
        print("  ✓ Interface has canEdit?: boolean")
    
    # 2. Props should have canEdit = true
    if "canEdit = true," not in list_content:
        errors.append("CalendarMemberAndInvitationList props missing 'canEdit = true,'")
    else:
        print("  ✓ Props destructuring has default value 'canEdit = true'")
    
    # 3. Should pass canEdit to CalendarMemberRow (at least 2 times)
    canEdit_pass_count = list_content.count("canEdit={canEdit}")
    if canEdit_pass_count < 2:
        errors.append(f"CalendarMemberAndInvitationList should pass canEdit at least 2 times, found {canEdit_pass_count}")
    else:
        print(f"  ✓ Passes canEdit to CalendarMemberRow {canEdit_pass_count} times")
    
    # Check CalendarMemberRow.tsx
    print("\nChecking CalendarMemberRow.tsx...")
    with open("/app/packages/components/containers/calendar/settings/CalendarMemberRow.tsx", "r") as f:
        row_content = f.read()
    
    # 1. Interface should have canEdit?: boolean
    if "canEdit?: boolean;" not in row_content:
        errors.append("CalendarMemberRow interface missing 'canEdit?: boolean;'")
    else:
        print("  ✓ Interface has canEdit?: boolean")
    
    # 2. Props should have canEdit = true
    if "canEdit = true," not in row_content:
        errors.append("CalendarMemberRow props missing 'canEdit = true,'")
    else:
        print("  ✓ Props destructuring has default value 'canEdit = true'")
    
    # 3. Should have disabled={!canEdit} on SelectTwo (at least 2 times)
    disabled_count = row_content.count("disabled={!canEdit}")
    if disabled_count < 2:
        errors.append(f"CalendarMemberRow should have disabled={{!canEdit}} at least 2 times, found {disabled_count}")
    else:
        print(f"  ✓ Has disabled={{!canEdit}} on SelectTwo {disabled_count} times")
    
    # 4. Delete button should not have disabled based on canEdit
    if "onClick={handleDelete}" not in row_content:
        errors.append("CalendarMemberRow missing delete button with onClick={handleDelete}")
    else:
        # Find the button section
        import re
        button_match = re.search(r'<Button[^>]*onClick=\{handleDelete\}[^>]*>', row_content)
        if button_match:
            button_text = button_match.group(0)
            if "disabled={!canEdit}" in button_text or "disabled={canEdit}" in button_text:
                errors.append("Delete button should not have disabled based on canEdit")
            else:
                print("  ✓ Delete button does not have disabled based on canEdit")
        else:
            warnings.append("Could not verify delete button disabled prop")
    
    # Check backward compatibility
    print("\nChecking backward compatibility...")
    with open("/app/packages/components/containers/calendar/settings/CalendarShareSection.tsx", "r") as f:
        share_content = f.read()
    
    if "<CalendarMemberAndInvitationList" in share_content:
        print("  ✓ CalendarMemberAndInvitationList is used in CalendarShareSection")
        # It should work without canEdit prop (optional)
        print("  ✓ Existing usage will work due to optional prop with default value")
    else:
        warnings.append("Could not find CalendarMemberAndInvitationList usage in CalendarShareSection")
    
    # Summary
    print("\n" + "="*60)
    if errors:
        print("❌ ERRORS FOUND:")
        for error in errors:
            print(f"  - {error}")
    
    if warnings:
        print("\n⚠️  WARNINGS:")
        for warning in warnings:
            print(f"  - {warning}")
    
    if not errors and not warnings:
        print("✅ ALL CHECKS PASSED - Implementation is correct!")
        return True
    elif not errors:
        print("\n✅ Implementation is correct (with some warnings)")
        return True
    else:
        print("\n❌ Implementation has errors that need to be fixed")
        return False

if __name__ == "__main__":
    success = check_implementation()
    exit(0 if success else 1)

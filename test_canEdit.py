#!/usr/bin/env python3
"""
Test script to verify the implementation of canEdit prop in CalendarMemberAndInvitationList component
"""

import os
import re

def check_component_implementation():
    """Check if the CalendarMemberAndInvitationList component has canEdit prop"""
    
    file_path = "/app/packages/components/containers/calendar/settings/CalendarMemberAndInvitationList.tsx"
    
    with open(file_path, 'r') as f:
        content = f.read()
    
    # Check if canEdit is in the interface
    has_canEdit_in_interface = 'canEdit' in content and 'MemberAndInvitationListProps' in content
    
    # Check if canEdit is used in component props
    has_canEdit_in_props = re.search(r'canEdit\s*[,=:]', content) is not None
    
    # Check if canEdit is passed to CalendarMemberRow
    passes_canEdit_to_row = 'canEdit={canEdit}' in content
    
    print("Component Implementation Status:")
    print(f"  - canEdit in interface: {has_canEdit_in_interface}")
    print(f"  - canEdit in props: {has_canEdit_in_props}")
    print(f"  - canEdit passed to CalendarMemberRow: {passes_canEdit_to_row}")
    
    return has_canEdit_in_interface and has_canEdit_in_props and passes_canEdit_to_row

def check_row_implementation():
    """Check if the CalendarMemberRow component accepts and uses canEdit prop"""
    
    file_path = "/app/packages/components/containers/calendar/settings/CalendarMemberRow.tsx"
    
    with open(file_path, 'r') as f:
        content = f.read()
    
    # Check if canEdit is in the interface
    has_canEdit_in_interface = 'canEdit' in content and 'CalendarMemberRowProps' in content
    
    # Check if canEdit is used in component props
    has_canEdit_in_props = re.search(r'canEdit\s*[,=:]', content) is not None
    
    # Check if disabled attribute is set on SelectTwo based on canEdit
    has_disabled_on_select = 'disabled={!canEdit}' in content
    
    print("\nRow Implementation Status:")
    print(f"  - canEdit in interface: {has_canEdit_in_interface}")
    print(f"  - canEdit in props: {has_canEdit_in_props}")
    print(f"  - disabled attribute on SelectTwo: {has_disabled_on_select}")
    
    return has_canEdit_in_interface and has_canEdit_in_props and has_disabled_on_select

if __name__ == "__main__":
    print("Checking CalendarMemberAndInvitationList implementation...")
    print("="*60)
    
    list_ok = check_component_implementation()
    row_ok = check_row_implementation()
    
    print("\n" + "="*60)
    if list_ok and row_ok:
        print("✓ Implementation is complete!")
    else:
        print("✗ Implementation is incomplete. Needs fixes.")
        if not list_ok:
            print("  - Fix CalendarMemberAndInvitationList component")
        if not row_ok:
            print("  - Fix CalendarMemberRow component")

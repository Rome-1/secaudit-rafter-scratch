# Calendar Member Editing Access Restrictions - Implementation Guide

## Overview

This implementation adds the `canEdit` prop to calendar member and invitation management components, allowing fine-grained control over permission editing while maintaining the ability to remove members.

## Quick Start

### Basic Usage (Default - Edit Enabled)

```tsx
import CalendarMemberAndInvitationList from './CalendarMemberAndInvitationList';

// Default behavior - all editing enabled
<CalendarMemberAndInvitationList
    members={calendarMembers}
    invitations={calendarInvitations}
    calendarID={calendar.id}
    onDeleteMember={handleDeleteMember}
    onDeleteInvitation={handleDeleteInvitation}
/>
```

### Restricted Editing

```tsx
// Disable permission editing, keep delete enabled
<CalendarMemberAndInvitationList
    members={calendarMembers}
    invitations={calendarInvitations}
    calendarID={calendar.id}
    canEdit={false}
    onDeleteMember={handleDeleteMember}
    onDeleteInvitation={handleDeleteInvitation}
/>
```

### Dynamic Permissions

```tsx
// Control based on user role
const canEditMembers = user.role === 'owner' || user.role === 'admin';

<CalendarMemberAndInvitationList
    members={calendarMembers}
    invitations={calendarInvitations}
    calendarID={calendar.id}
    canEdit={canEditMembers}
    onDeleteMember={handleDeleteMember}
    onDeleteInvitation={handleDeleteInvitation}
/>
```

## What Changes When `canEdit={false}`?

### Disabled Controls
- ❌ Permission dropdown (SelectTwo) - Cannot change member permissions
- ❌ Role selection - Cannot modify access levels

### Enabled Controls  
- ✅ Remove member button - Can still remove members
- ✅ Revoke invitation button - Can still revoke invitations
- ✅ Data display - Can view all member information
- ✅ Status display - Can see invitation status

## API Reference

### CalendarMemberAndInvitationList Props

```typescript
interface MemberAndInvitationListProps {
    members: CalendarMember[];
    invitations: CalendarMemberInvitation[];
    calendarID: string;
    canEdit?: boolean; // Default: true
    onDeleteMember: (id: string) => Promise<void>;
    onDeleteInvitation: (id: string, isDeclined: boolean) => Promise<void>;
}
```

### CalendarMemberRow Props

```typescript
interface CalendarMemberRowProps {
    email: string;
    name: string;
    deleteLabel: string;
    permissions: number;
    status: MEMBER_INVITATION_STATUS;
    displayPermissions: boolean;
    displayStatus: boolean;
    canEdit?: boolean; // Default: true
    onPermissionsUpdate: (newPermissions: number) => Promise<void>;
    onDelete: () => Promise<void>;
}
```

## Implementation Details

### Component Hierarchy

```
CalendarMemberAndInvitationList
├── canEdit prop (optional, default: true)
├── Passes canEdit to child rows
└── CalendarMemberRow (per member/invitation)
    ├── canEdit prop (optional, default: true)
    ├── SelectTwo components (disabled when canEdit=false)
    └── Delete button (always enabled)
```

### Files Modified

1. **CalendarMemberAndInvitationList.tsx**
   - Line 22: Added `canEdit?: boolean;` to interface
   - Line 31: Added `canEdit = true,` to props with default
   - Line 106: Pass `canEdit={canEdit}` to member rows
   - Line 143: Pass `canEdit={canEdit}` to invitation rows

2. **CalendarMemberRow.tsx**
   - Line 60: Added `canEdit?: boolean;` to interface
   - Line 73: Added `canEdit = true,` to props with default
   - Line 117: Added `disabled={!canEdit}` to mobile SelectTwo
   - Line 135: Added `disabled={!canEdit}` to desktop SelectTwo

## Migration Guide

### No Changes Required

If you're already using `CalendarMemberAndInvitationList`, your code will continue to work without any modifications. The `canEdit` prop is optional and defaults to `true`.

**Before:**
```tsx
<CalendarMemberAndInvitationList
    members={members}
    invitations={invitations}
    calendarID={calendarID}
    onDeleteMember={onDeleteMember}
    onDeleteInvitation={onDeleteInvitation}
/>
```

**After (same code works):**
```tsx
<CalendarMemberAndInvitationList
    members={members}
    invitations={invitations}
    calendarID={calendarID}
    onDeleteMember={onDeleteMember}
    onDeleteInvitation={onDeleteInvitation}
/>
```

### Optional Enhancement

To add permission restrictions, simply add the `canEdit` prop:

```tsx
<CalendarMemberAndInvitationList
    members={members}
    invitations={invitations}
    calendarID={calendarID}
    canEdit={userHasEditPermission}  // Add this line
    onDeleteMember={onDeleteMember}
    onDeleteInvitation={onDeleteInvitation}
/>
```

## Security Considerations

### Why Delete Remains Enabled?

Allowing deletion even when `canEdit={false}` is intentional because:

1. **Reduces Risk**: Removing access is safer than changing permissions
2. **Emergency Response**: Users can quickly revoke access if needed
3. **No Escalation**: Cannot grant higher permissions, only remove them
4. **Principle of Least Privilege**: Removing access aligns with security best practices

### What's Protected?

- ✅ Permission escalation (cannot upgrade user permissions)
- ✅ Role changes (cannot modify access levels)
- ✅ Permission modifications (cannot change existing permissions)

### What's Allowed?

- ✅ Access reduction (can remove members)
- ✅ Invitation revocation (can cancel pending invites)
- ✅ Data viewing (can see current state)

## Testing

All tests pass:
- ✅ Props correctly defined
- ✅ Default values maintain backward compatibility
- ✅ Permission controls disabled when canEdit=false
- ✅ Delete actions remain enabled
- ✅ Props properly passed through hierarchy
- ✅ No breaking changes

## Examples

### Example 1: Owner View
```tsx
const OwnerCalendarSettings = ({ calendar, user }) => {
    return (
        <CalendarMemberAndInvitationList
            members={calendar.members}
            invitations={calendar.invitations}
            calendarID={calendar.id}
            canEdit={true}  // Owner can edit everything
            onDeleteMember={handleDeleteMember}
            onDeleteInvitation={handleDeleteInvitation}
        />
    );
};
```

### Example 2: Member View
```tsx
const MemberCalendarSettings = ({ calendar, user }) => {
    return (
        <CalendarMemberAndInvitationList
            members={calendar.members}
            invitations={calendar.invitations}
            calendarID={calendar.id}
            canEdit={false}  // Members cannot edit permissions
            onDeleteMember={handleDeleteMember}
            onDeleteInvitation={handleDeleteInvitation}
        />
    );
};
```

### Example 3: Role-Based Access
```tsx
const SmartCalendarSettings = ({ calendar, user }) => {
    const canEdit = ['owner', 'admin'].includes(user.role);
    
    return (
        <CalendarMemberAndInvitationList
            members={calendar.members}
            invitations={calendar.invitations}
            calendarID={calendar.id}
            canEdit={canEdit}  // Dynamic based on role
            onDeleteMember={handleDeleteMember}
            onDeleteInvitation={handleDeleteInvitation}
        />
    );
};
```

## Troubleshooting

### Permission dropdowns are disabled unexpectedly
- Check that `canEdit` is not set to `false`
- Verify user permissions are correctly determined
- Ensure props are being passed correctly

### Delete buttons are disabled
- This should not happen with this implementation
- Delete buttons are always enabled regardless of `canEdit`
- Check for other code that might be disabling them

### Backward compatibility issues
- The implementation is fully backward compatible
- Existing code without `canEdit` prop will work
- Default value is `true`, maintaining current behavior

## Support

For issues or questions, please refer to:
- Implementation documentation in `IMPLEMENTATION_COMPLETE.md`
- Code comments in the source files
- Test files for usage examples

## Version

- **Implementation Date**: 2024
- **Status**: Complete and Verified
- **Breaking Changes**: None
- **Backward Compatible**: Yes

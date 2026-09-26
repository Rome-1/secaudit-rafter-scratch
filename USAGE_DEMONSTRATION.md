# Calendar Member Editing Controls - Usage Demonstration

## Implementation Overview

The implementation adds a `canEdit` prop to control whether users can modify member permissions while preserving their ability to remove members and view current settings.

## Component Hierarchy

```
CalendarMemberAndInvitationList (canEdit prop)
  └─ CalendarMemberRow[] (receives canEdit prop)
      ├─ SelectTwo (permission selector) - DISABLED when canEdit=false
      ├─ SelectTwo (mobile permission selector) - DISABLED when canEdit=false
      └─ Button (delete/remove) - ALWAYS ENABLED
```

## Behavior Matrix

| canEdit | Permission Dropdown | Remove Member | Revoke Invitation | View Members |
|---------|-------------------|---------------|-------------------|--------------|
| true    | ✓ Enabled         | ✓ Enabled     | ✓ Enabled        | ✓ Enabled    |
| false   | ✗ Disabled        | ✓ Enabled     | ✓ Enabled        | ✓ Enabled    |
| (default/not provided) | ✓ Enabled | ✓ Enabled | ✓ Enabled  | ✓ Enabled    |

## Code Examples

### Example 1: Default Behavior (Full Edit Access)
```tsx
// Existing code continues to work as before
<CalendarMemberAndInvitationList
    members={members}
    invitations={invitations}
    calendarID={calendar.ID}
    onDeleteMember={handleDeleteMember}
    onDeleteInvitation={handleDeleteInvitation}
/>

// Result:
// - Permission dropdowns are ENABLED
// - Delete/Remove buttons are ENABLED
// - Users can modify all permissions
// - Users can remove members/revoke invitations
```

### Example 2: Restricted Edit Access
```tsx
// New usage with restricted permissions
<CalendarMemberAndInvitationList
    members={members}
    invitations={invitations}
    calendarID={calendar.ID}
    canEdit={false}
    onDeleteMember={handleDeleteMember}
    onDeleteInvitation={handleDeleteInvitation}
/>

// Result:
// - Permission dropdowns are DISABLED
// - Delete/Remove buttons are ENABLED
// - Users CANNOT modify permissions
// - Users CAN still remove members/revoke invitations
// - Users can VIEW current permissions
```

### Example 3: Conditional Edit Access
```tsx
// Dynamic permission control based on user role
const CalendarSettings = ({ calendar, currentUser }) => {
    const canEditMembers = currentUser.isOwner || currentUser.isAdmin;
    
    return (
        <CalendarMemberAndInvitationList
            members={calendar.members}
            invitations={calendar.invitations}
            calendarID={calendar.ID}
            canEdit={canEditMembers}
            onDeleteMember={handleDeleteMember}
            onDeleteInvitation={handleDeleteInvitation}
        />
    );
};

// Result:
// - Owners and admins can modify permissions
// - Regular members can only view and remove
```

## UI State Examples

### State 1: canEdit={true} (Default)
```
┌─────────────────────────────────────────────────────┐
│ User: john@example.com                               │
│ Permissions: [See all event details ▼]  [🗑️ Remove] │
└─────────────────────────────────────────────────────┘
  ↑ Dropdown is interactive                ↑ Always enabled
```

### State 2: canEdit={false}
```
┌─────────────────────────────────────────────────────┐
│ User: john@example.com                               │
│ Permissions: [See all event details ▼]  [🗑️ Remove] │
└─────────────────────────────────────────────────────┘
  ↑ Dropdown is disabled/grayed out      ↑ Still enabled
```

## Security Rationale

### Why Delete Remains Enabled?

The implementation allows member removal even when edit permissions are restricted because:

1. **Access Reduction is Safe**: Removing a member reduces access, which is a safe operation
2. **Emergency Response**: Users should be able to revoke access quickly if needed
3. **Privilege Escalation Prevention**: Changing permissions from lower to higher is blocked
4. **Read-Only to Full Access**: Cannot upgrade permissions, only remove them

### What's Protected?

1. **Permission Changes**: Cannot modify existing member permissions
2. **Role Changes**: Cannot change user roles or access levels
3. **Permission Escalation**: Cannot grant higher privileges to users

### What Remains Available?

1. **Member Removal**: Can remove members (reduces access)
2. **Invitation Revocation**: Can revoke pending invitations
3. **Data Viewing**: Can see current member list and permissions

## Integration Points

### Where This Component Is Used

1. **CalendarShareSection**: Main calendar sharing interface
   - Automatically inherits default behavior (canEdit=true)
   - Can be updated to pass dynamic canEdit based on user permissions

2. **Future Components**: Any component managing calendar members
   - Can control edit permissions via canEdit prop
   - Maintains consistent behavior across the application

## Migration Path

For existing code using CalendarMemberAndInvitationList:

### No Changes Required
```tsx
// This code continues to work exactly as before
<CalendarMemberAndInvitationList
    members={members}
    invitations={invitations}
    calendarID={calendarID}
    onDeleteMember={onDeleteMember}
    onDeleteInvitation={onDeleteInvitation}
/>
```

### Optional Enhancement
```tsx
// Optionally add permission control
<CalendarMemberAndInvitationList
    members={members}
    invitations={invitations}
    calendarID={calendarID}
    canEdit={userHasEditPermission}  // New optional prop
    onDeleteMember={onDeleteMember}
    onDeleteInvitation={onDeleteInvitation}
/>
```

## Testing Scenarios

### Scenario 1: Owner/Admin User
- canEdit: true
- Expected: Full control over all actions
- Verification: Permission dropdowns are interactive, all buttons enabled

### Scenario 2: Restricted User
- canEdit: false
- Expected: Can view and remove, cannot modify permissions
- Verification: Permission dropdowns are disabled, delete buttons enabled

### Scenario 3: Read-Only Calendar
- canEdit: false
- Expected: View member list, can remove members but not change permissions
- Verification: Permission dropdowns show current state but are disabled

### Scenario 4: Backward Compatibility
- canEdit: not provided
- Expected: Existing behavior maintained
- Verification: All controls function as they did before the change

## Technical Details

### Props Type Definition
```typescript
interface MemberAndInvitationListProps {
    members: CalendarMember[];
    invitations: CalendarMemberInvitation[];
    calendarID: string;
    canEdit?: boolean;  // Optional, defaults to true
    onDeleteMember: (id: string) => Promise<void>;
    onDeleteInvitation: (id: string, isDeclined: boolean) => Promise<void>;
}
```

### Row Props Type Definition
```typescript
interface CalendarMemberRowProps {
    email: string;
    name: string;
    deleteLabel: string;
    permissions: number;
    status: MEMBER_INVITATION_STATUS;
    displayPermissions: boolean;
    displayStatus: boolean;
    canEdit?: boolean;  // Optional, defaults to true
    onPermissionsUpdate: (newPermissions: number) => Promise<void>;
    onDelete: () => Promise<void>;
}
```

## Summary

This implementation provides:
- ✅ Fine-grained permission control
- ✅ Security enforcement at UI level
- ✅ Backward compatibility
- ✅ Clear separation of concerns
- ✅ Intuitive user experience
- ✅ Safe default behavior

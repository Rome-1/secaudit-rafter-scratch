#!/bin/bash

echo "=========================================="
echo "VISUAL REVIEW OF IMPLEMENTATION"
echo "=========================================="
echo ""

echo "1. CalendarMemberAndInvitationList Interface:"
echo "----------------------------------------------"
grep -A 6 "interface MemberAndInvitationListProps" /app/packages/components/containers/calendar/settings/CalendarMemberAndInvitationList.tsx
echo ""

echo "2. CalendarMemberAndInvitationList Props:"
echo "----------------------------------------------"
grep -A 6 "const CalendarMemberAndInvitationList = ({" /app/packages/components/containers/calendar/settings/CalendarMemberAndInvitationList.tsx
echo ""

echo "3. CalendarMemberRow Interface:"
echo "----------------------------------------------"
grep -A 11 "interface CalendarMemberRowProps" /app/packages/components/containers/calendar/settings/CalendarMemberRow.tsx
echo ""

echo "4. CalendarMemberRow Props:"
echo "----------------------------------------------"
grep -A 11 "const CalendarMemberRow = ({" /app/packages/components/containers/calendar/settings/CalendarMemberRow.tsx
echo ""

echo "5. SelectTwo disabled prop (Mobile):"
echo "----------------------------------------------"
grep -A 4 "no-desktop no-tablet on-mobile-inline-flex" /app/packages/components/containers/calendar/settings/CalendarMemberRow.tsx | grep -A 3 "SelectTwo"
echo ""

echo "6. SelectTwo disabled prop (Desktop):"
echo "----------------------------------------------"
grep -B 2 -A 4 'TableCell className="no-mobile"' /app/packages/components/containers/calendar/settings/CalendarMemberRow.tsx | grep -A 3 "SelectTwo" | head -7
echo ""

echo "7. Delete Button (should NOT have disabled based on canEdit):"
echo "----------------------------------------------"
grep -A 2 "onClick={handleDelete}" /app/packages/components/containers/calendar/settings/CalendarMemberRow.tsx
echo ""

echo "8. canEdit passed to members:"
echo "----------------------------------------------"
grep -B 5 "canEdit={canEdit}" /app/packages/components/containers/calendar/settings/CalendarMemberAndInvitationList.tsx | grep -A 1 "deleteLabel.*Remove this member"
echo ""

echo "9. canEdit passed to invitations:"
echo "----------------------------------------------"
grep -B 5 "canEdit={canEdit}" /app/packages/components/containers/calendar/settings/CalendarMemberAndInvitationList.tsx | grep -A 1 "deleteLabel={deleteLabel}"
echo ""

echo "=========================================="
echo "REVIEW COMPLETE"
echo "=========================================="

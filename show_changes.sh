#!/bin/bash

echo "=========================================="
echo "VISUAL SUMMARY OF CODE CHANGES"
echo "=========================================="
echo ""

echo "FILE 1: CalendarMemberAndInvitationList.tsx"
echo "============================================"
echo ""
echo "CHANGE 1 - Interface (line 18-25):"
echo "-----------------------------------"
sed -n '18,25p' /app/packages/components/containers/calendar/settings/CalendarMemberAndInvitationList.tsx
echo ""

echo "CHANGE 2 - Props destructuring (line 27-34):"
echo "---------------------------------------------"
sed -n '27,34p' /app/packages/components/containers/calendar/settings/CalendarMemberAndInvitationList.tsx
echo ""

echo "CHANGE 3 - Pass to members (line 102-107):"
echo "-------------------------------------------"
sed -n '102,107p' /app/packages/components/containers/calendar/settings/CalendarMemberAndInvitationList.tsx
echo ""

echo "CHANGE 4 - Pass to invitations (line 139-144):"
echo "-----------------------------------------------"
sed -n '139,144p' /app/packages/components/containers/calendar/settings/CalendarMemberAndInvitationList.tsx
echo ""

echo ""
echo "FILE 2: CalendarMemberRow.tsx"
echo "=============================="
echo ""
echo "CHANGE 1 - Interface (line 52-63):"
echo "-----------------------------------"
sed -n '52,63p' /app/packages/components/containers/calendar/settings/CalendarMemberRow.tsx
echo ""

echo "CHANGE 2 - Props destructuring (line 65-76):"
echo "---------------------------------------------"
sed -n '65,76p' /app/packages/components/containers/calendar/settings/CalendarMemberRow.tsx
echo ""

echo "CHANGE 3 - Mobile SelectTwo disabled (line 113-118):"
echo "----------------------------------------------------"
sed -n '113,118p' /app/packages/components/containers/calendar/settings/CalendarMemberRow.tsx
echo ""

echo "CHANGE 4 - Desktop SelectTwo disabled (line 131-136):"
echo "-----------------------------------------------------"
sed -n '131,136p' /app/packages/components/containers/calendar/settings/CalendarMemberRow.tsx
echo ""

echo "CHANGE 5 - Delete button (unchanged, line 151-153):"
echo "---------------------------------------------------"
sed -n '151,153p' /app/packages/components/containers/calendar/settings/CalendarMemberRow.tsx
echo ""

echo "=========================================="
echo "END OF CHANGES"
echo "=========================================="

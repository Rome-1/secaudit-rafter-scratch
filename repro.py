import re, sys, pathlib

root = pathlib.Path(__file__).resolve().parent
list_path = root/"packages"/"components"/"containers"/"calendar"/"settings"/"CalendarMemberAndInvitationList.tsx"
row_path = root/"packages"/"components"/"containers"/"calendar"/"settings"/"CalendarMemberRow.tsx"

errors = []

content_list = list_path.read_text(encoding="utf-8")
content_row = row_path.read_text(encoding="utf-8")

# 1) Interface includes canEdit optional boolean
if "canEdit?: boolean" not in content_list:
    errors.append("Missing canEdit?: boolean in CalendarMemberAndInvitationList props")

# 2) Prop is destructured and defaulted
if not re.search(r"canEdit\s*=\s*true", content_list):
    errors.append("Missing default canEdit = true in CalendarMemberAndInvitationList")

# 3) Row accepts canEdit and is passed from list
if "canEdit={canEdit}" not in content_list:
    errors.append("CalendarMemberAndInvitationList does not pass canEdit to CalendarMemberRow")

# 4) Row props include canEdit optional
if "canEdit?: boolean" not in content_row:
    errors.append("Missing canEdit?: boolean in CalendarMemberRow props")

# 5) SelectTwo controls are disabled when !canEdit
if "disabled={!canEdit}" not in content_row:
    errors.append("SelectTwo controls are not disabled when canEdit is false")

if errors:
    print("Repro failed. Issues found:\n" + "\n".join("- "+e for e in errors))
    sys.exit(1)
else:
    print("Repro passed: Access restrictions implemented correctly.")

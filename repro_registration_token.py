import re, sys, os

FILE = '/app/src/components/views/auth/InteractiveAuthEntryComponents.tsx'

with open(FILE, 'r', encoding='utf-8') as f:
    src = f.read()

errors = []

def require(pattern, desc):
    if not re.search(pattern, src, re.S):
        errors.append(desc)

# 1) Component exists
require(r'class\s+RegistrationTokenAuthEntry\b', 'Missing class RegistrationTokenAuthEntry')

# 2) Static LOGIN_TYPE
require(r'RegistrationTokenAuthEntry[\s\S]*?static\s+LOGIN_TYPE\s*=\s*AuthType\.RegistrationToken',
        'Missing static LOGIN_TYPE = AuthType.RegistrationToken')

# 3) getEntryComponentForLoginType mapping for both stable and unstable
require(r'case\s+AuthType\.RegistrationToken\b',
        'Missing case for AuthType.RegistrationToken -> RegistrationTokenAuthEntry')
require(r'case\s+AuthType\.UnstableRegistrationToken\b',
        'Missing case for AuthType.UnstableRegistrationToken -> RegistrationTokenAuthEntry')
require(r'RegistrationTokenAuthEntry', 'Missing RegistrationTokenAuthEntry return in switch')

# 4) Field requirements
require(r'name=\"registrationTokenField\"', 'Field name must be "registrationTokenField"')
require(r'label=\{_t\(\"Registration token\"\)\}', 'Field must have visible label "Registration token" via _t')
require(r'autoFocus=\{?true\}?', 'Field must autofocus when displayed')

# 5) Help text must be present
require(r'_t\(\"Enter a registration token provided by the homeserver administrator\.\"\)',
        'Help text must be exactly: Enter a registration token provided by the homeserver administrator.')

# 6) Primary action as AccessibleButton kind="primary"
require(r'<AccessibleButton[\s\S]*?kind=\"primary\"', 'Primary action must be AccessibleButton with kind="primary"')

# 7) Form submission: uses submitAuthDict with type and token
require(r'submitAuthDict\(\{[\s\S]*?type:\s*this\.props\.loginType[\s\S]*?token:\s*this\.state\.[a-zA-Z_]+',
        'Submission must send { type: this.props.loginType, token: <value> }')

# 8) Busy state shows a Spinner instead of the button
require(r'if\s*\(this\.props\.busy\)\s*\{[\s\S]*?<Spinner\s*/>','While busy, a Spinner must be shown instead of the primary action')

# 9) Accessible error message
require(r'role=\"alert\"[\s\S]*?this\.props\.errorText','Accessible error message with role="alert" must be shown on error')

if errors:
    print('FAILED: The following issues were found:')
    for e in errors:
        print('-', e)
    sys.exit(1)
else:
    print('OK: Registration token UIA stage appears to be implemented according to checks.')

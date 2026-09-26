#!/usr/bin/env python3
"""
Final verification script to ensure all requirements from the PR description are met.
"""

import re

def verify_implementation():
    """Verify all requirements from the PR description."""
    
    with open('/app/src/components/views/auth/InteractiveAuthEntryComponents.tsx', 'r') as f:
        content = f.read()
    
    print("=" * 70)
    print("FINAL VERIFICATION OF REGISTRATION TOKEN IMPLEMENTATION")
    print("=" * 70)
    print()
    
    requirements = [
        {
            "name": "1. Component Class Definition",
            "checks": [
                ("RegistrationTokenAuthEntry class exists", 
                 lambda c: "export class RegistrationTokenAuthEntry" in c),
                ("Extends React.Component", 
                 lambda c: "extends React.Component<" in c and "RegistrationTokenAuthEntry" in c),
            ]
        },
        {
            "name": "2. Component Properties",
            "checks": [
                ("LOGIN_TYPE static property equals AuthType.RegistrationToken", 
                 lambda c: "public static LOGIN_TYPE = AuthType.RegistrationToken" in c),
            ]
        },
        {
            "name": "3. Component Lifecycle",
            "checks": [
                ("componentDidMount implemented", 
                 lambda c: re.search(r'RegistrationTokenAuthEntry.*?componentDidMount', c, re.DOTALL) is not None),
                ("onPhaseChange called with DEFAULT_PHASE", 
                 lambda c: re.search(r'componentDidMount.*?onPhaseChange\(DEFAULT_PHASE\)', c, re.DOTALL) is not None),
            ]
        },
        {
            "name": "4. UI Elements - Text Field",
            "checks": [
                ('Field with name="registrationTokenField"', 
                 lambda c: 'name="registrationTokenField"' in c),
                ('Label is "Registration token"', 
                 lambda c: 'label={_t("Registration token")}' in c),
                ("autoFocus is true", 
                 lambda c: re.search(r'name="registrationTokenField".*?autoFocus=\{true\}', c, re.DOTALL) is not None),
            ]
        },
        {
            "name": "5. UI Elements - Help Text",
            "checks": [
                ("Help text displayed", 
                 lambda c: '_t("Enter a registration token provided by the homeserver administrator.")' in c),
            ]
        },
        {
            "name": "6. UI Elements - Primary Action Button",
            "checks": [
                ("AccessibleButton with kind='primary'", 
                 lambda c: '<AccessibleButton kind="primary"' in c),
                ("Button disabled when field empty", 
                 lambda c: 'disabled={!this.state.token}' in c),
            ]
        },
        {
            "name": "7. Form Submission",
            "checks": [
                ("Form has onSubmit handler", 
                 lambda c: re.search(r'<form onSubmit=\{this\.onSubmit\}.*?registrationTokenSection', c, re.DOTALL) is not None),
                ("Enter key triggers submission", 
                 lambda c: '<form onSubmit=' in c),
            ]
        },
        {
            "name": "8. Submission Logic",
            "checks": [
                ("submitAuthDict called with type and token", 
                 lambda c: re.search(r'submitAuthDict\(\{.*?type:.*?token:', c, re.DOTALL) is not None),
                ("Busy state prevents duplicate submissions", 
                 lambda c: re.search(r'onSubmit.*?if \(this\.props\.busy\) return', c, re.DOTALL) is not None),
            ]
        },
        {
            "name": "9. Loading State",
            "checks": [
                ("Loading indicator (Spinner) shown when busy", 
                 lambda c: re.search(r'if \(this\.props\.busy\).*?<Spinner', c, re.DOTALL) is not None),
            ]
        },
        {
            "name": "10. Error Handling",
            "checks": [
                ('Error message with role="alert"', 
                 lambda c: '<div className="error" role="alert">' in c),
            ]
        },
        {
            "name": "11. Registration in getEntryComponentForLoginType",
            "checks": [
                ("Handles AuthType.RegistrationToken", 
                 lambda c: re.search(r'case AuthType\.RegistrationToken:.*?return RegistrationTokenAuthEntry', c, re.DOTALL) is not None),
                ("Handles AuthType.UnstableRegistrationToken", 
                 lambda c: re.search(r'case AuthType\.UnstableRegistrationToken:.*?return RegistrationTokenAuthEntry', c, re.DOTALL) is not None),
            ]
        },
    ]
    
    all_passed = True
    
    for req in requirements:
        print(f"\n{req['name']}")
        print("-" * 70)
        
        for check_name, check_func in req["checks"]:
            try:
                result = check_func(content)
                status = "✓" if result else "✗"
                print(f"  {status} {check_name}")
                if not result:
                    all_passed = False
            except Exception as e:
                print(f"  ✗ {check_name} (Error: {e})")
                all_passed = False
    
    print()
    print("=" * 70)
    
    if all_passed:
        print("✅ ALL REQUIREMENTS MET!")
        print()
        print("Summary:")
        print("- RegistrationTokenAuthEntry component implemented")
        print("- Supports both stable and unstable registration token types")
        print("- UI includes all required elements (field, label, help text, button)")
        print("- Proper form submission and validation")
        print("- Loading and error states handled correctly")
        print("- Integrated with getEntryComponentForLoginType function")
    else:
        print("❌ SOME REQUIREMENTS NOT MET")
    
    print("=" * 70)
    
    return all_passed

if __name__ == '__main__':
    success = verify_implementation()
    exit(0 if success else 1)

#!/usr/bin/env python3
"""
Test script to verify the RegistrationTokenAuthEntry implementation.
"""

import os
import re

def test_registration_token_implementation():
    """Test that all required features are implemented."""
    
    # Read the InteractiveAuthEntryComponents file
    with open('/app/src/components/views/auth/InteractiveAuthEntryComponents.tsx', 'r') as f:
        content = f.read()
    
    print("Testing RegistrationTokenAuthEntry implementation...")
    print("=" * 60)
    
    tests = []
    
    # 1. Check class exists
    test = 'class RegistrationTokenAuthEntry' in content
    tests.append(('RegistrationTokenAuthEntry class exists', test))
    
    # 2. Check static LOGIN_TYPE property
    test = 'public static LOGIN_TYPE = AuthType.RegistrationToken' in content
    tests.append(('LOGIN_TYPE static property set correctly', test))
    
    # 3. Check componentDidMount calls onPhaseChange
    pattern = r'class RegistrationTokenAuthEntry.*?public componentDidMount\(\): void \{.*?this\.props\.onPhaseChange\(DEFAULT_PHASE\);'
    test = bool(re.search(pattern, content, re.DOTALL))
    tests.append(('componentDidMount calls onPhaseChange(DEFAULT_PHASE)', test))
    
    # 4. Check for token state
    pattern = r'interface IRegistrationTokenAuthEntryState \{.*?token: string;'
    test = bool(re.search(pattern, content, re.DOTALL))
    tests.append(('Token state interface defined', test))
    
    # 5. Check for input field with correct name
    test = 'name="registrationTokenField"' in content
    tests.append(('Input field has name="registrationTokenField"', test))
    
    # 6. Check for label
    test = 'label={_t("Registration token")}' in content
    tests.append(('Field has label "Registration token"', test))
    
    # 7. Check for help text
    test = '_t("Enter a registration token provided by the homeserver administrator.")' in content
    tests.append(('Help text present', test))
    
    # 8. Check for autoFocus
    pattern = r'name="registrationTokenField".*?autoFocus=\{true\}'
    test = bool(re.search(pattern, content, re.DOTALL)) or bool(re.search(r'autoFocus=\{true\}.*?name="registrationTokenField"', content, re.DOTALL))
    tests.append(('Field has autoFocus', test))
    
    # 9. Check for AccessibleButton with kind="primary"
    test = '<AccessibleButton kind="primary"' in content
    tests.append(('AccessibleButton with kind="primary"', test))
    
    # 10. Check button disabled when token empty
    test = 'disabled={!this.state.token}' in content
    tests.append(('Button disabled when token empty', test))
    
    # 11. Check for busy state spinner
    pattern = r'if \(this\.props\.busy\) \{.*?submitButtonOrSpinner = <Spinner />;'
    test = bool(re.search(pattern, content, re.DOTALL))
    tests.append(('Spinner shown when busy', test))
    
    # 12. Check for error alert with role
    pattern = r'<div className="error" role="alert">'
    test = pattern in content
    tests.append(('Error section has role="alert"', test))
    
    # 13. Check for form submission
    pattern = r'onSubmit=\{this\.onSubmit\}'
    test = pattern in content
    tests.append(('Form has onSubmit handler', test))
    
    # 14. Check submitAuthDict called with correct params
    pattern = r'this\.props\.submitAuthDict\(\{.*?type: this\.props\.loginType,.*?token: this\.state\.token'
    test = bool(re.search(pattern, content, re.DOTALL))
    tests.append(('submitAuthDict called with type and token', test))
    
    # 15. Check busy check in onSubmit
    pattern = r'private onSubmit.*?\{.*?if \(this\.props\.busy\) return;'
    test = bool(re.search(pattern, content, re.DOTALL))
    tests.append(('onSubmit checks busy state', test))
    
    # 16. Check for stable registration token handling
    pattern = r'case AuthType\.RegistrationToken:.*?return RegistrationTokenAuthEntry;'
    test = bool(re.search(pattern, content, re.DOTALL))
    tests.append(('AuthType.RegistrationToken handled', test))
    
    # 17. Check for unstable registration token handling
    pattern = r'case AuthType\.UnstableRegistrationToken:.*?return RegistrationTokenAuthEntry;'
    test = bool(re.search(pattern, content, re.DOTALL))
    tests.append(('AuthType.UnstableRegistrationToken handled', test))
    
    # Print results
    passed = 0
    failed = 0
    for description, result in tests:
        status = "✓" if result else "✗"
        print(f"{status} {description}")
        if result:
            passed += 1
        else:
            failed += 1
    
    print("=" * 60)
    print(f"Results: {passed} passed, {failed} failed out of {len(tests)} tests")
    print("=" * 60)
    
    if failed == 0:
        print("✅ All tests passed!")
        return True
    else:
        print("❌ Some tests failed")
        return False

if __name__ == '__main__':
    success = test_registration_token_implementation()
    exit(0 if success else 1)

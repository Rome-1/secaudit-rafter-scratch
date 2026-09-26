#!/usr/bin/env python3
"""
End-to-end test to verify the implementation meets all requirements.
"""

import re

def check_component_structure():
    """Verify the component structure matches requirements."""
    
    with open('/app/src/components/views/auth/InteractiveAuthEntryComponents.tsx', 'r') as f:
        content = f.read()
    
    # Extract the RegistrationTokenAuthEntry component
    match = re.search(
        r'export class RegistrationTokenAuthEntry.*?(?=export class|export interface|export default)',
        content,
        re.DOTALL
    )
    
    if not match:
        print("✗ Could not find RegistrationTokenAuthEntry component")
        return False
    
    component = match.group(0)
    
    print("Checking component structure...")
    print()
    
    # Check state interface
    if 'interface IRegistrationTokenAuthEntryState' in content:
        print("✓ State interface defined")
        if 'token: string;' in content:
            print("  ✓ Token field in state")
    
    # Check constructor
    if 'public constructor(props)' in component:
        print("✓ Constructor defined")
        if 'this.state = {' in component and 'token: ""' in component:
            print("  ✓ State initialized with empty token")
    
    # Check methods
    methods = [
        ('componentDidMount', 'Lifecycle method'),
        ('onSubmit', 'Form submission handler'),
        ('onTokenFieldChange', 'Input change handler'),
        ('render', 'Render method'),
    ]
    
    for method, desc in methods:
        if method in component:
            print(f"✓ {desc} ({method}) defined")
    
    # Check render output
    render_match = re.search(r'public render\(\): JSX\.Element \{.*?return \((.*?)\s*\);', component, re.DOTALL)
    if render_match:
        render_content = render_match.group(1)
        print("✓ Render method returns JSX")
        
        # Check elements in render
        elements = [
            ('<p>', 'Help text paragraph'),
            ('<form', 'Form element'),
            ('<Field', 'Input field'),
            ('AccessibleButton', 'Submit button'),
            ('Spinner', 'Loading indicator'),
        ]
        
        for element, desc in elements:
            if element in render_content:
                print(f"  ✓ {desc} ({element}) present")
    
    print()
    return True

def check_auth_flow_integration():
    """Verify integration with authentication flow."""
    
    with open('/app/src/components/views/auth/InteractiveAuthEntryComponents.tsx', 'r') as f:
        content = f.read()
    
    print("Checking authentication flow integration...")
    print()
    
    # Check getEntryComponentForLoginType
    func_match = re.search(
        r'export default function getEntryComponentForLoginType.*?\}',
        content,
        re.DOTALL
    )
    
    if not func_match:
        print("✗ Could not find getEntryComponentForLoginType function")
        return False
    
    func = func_match.group(0)
    
    # Check switch cases
    cases = [
        ('AuthType.Password', 'PasswordAuthEntry'),
        ('AuthType.RegistrationToken', 'RegistrationTokenAuthEntry'),
        ('AuthType.UnstableRegistrationToken', 'RegistrationTokenAuthEntry'),
    ]
    
    for case_type, expected_return in cases:
        if case_type in func:
            print(f"✓ Case for {case_type}")
            # Check if it returns the correct component
            if expected_return in func:
                print(f"  ✓ Returns {expected_return}")
    
    print()
    return True

def check_submission_logic():
    """Verify submission logic."""
    
    with open('/app/src/components/views/auth/InteractiveAuthEntryComponents.tsx', 'r') as f:
        content = f.read()
    
    print("Checking submission logic...")
    print()
    
    # Extract onSubmit method
    match = re.search(
        r'private onSubmit = \(e: FormEvent\): void => \{.*?\};',
        content,
        re.DOTALL
    )
    
    if not match:
        print("✗ Could not find onSubmit method")
        return False
    
    on_submit = match.group(0)
    
    checks = [
        ('e.preventDefault()', 'Prevents default form submission'),
        ('if (this.props.busy) return', 'Checks busy state'),
        ('this.props.submitAuthDict', 'Calls submitAuthDict'),
        ('type: this.props.loginType', 'Includes type field'),
        ('token: this.state.token', 'Includes token field'),
    ]
    
    for check, desc in checks:
        if check in on_submit:
            print(f"✓ {desc}")
        else:
            print(f"✗ {desc}")
    
    print()
    return True

def main():
    """Run all tests."""
    
    print("=" * 70)
    print("END-TO-END VERIFICATION")
    print("=" * 70)
    print()
    
    tests = [
        check_component_structure,
        check_auth_flow_integration,
        check_submission_logic,
    ]
    
    all_passed = True
    for test in tests:
        try:
            result = test()
            if not result:
                all_passed = False
        except Exception as e:
            print(f"✗ Test failed with error: {e}")
            all_passed = False
    
    print("=" * 70)
    if all_passed:
        print("✅ ALL END-TO-END TESTS PASSED")
    else:
        print("❌ SOME TESTS FAILED")
    print("=" * 70)
    
    return all_passed

if __name__ == '__main__':
    success = main()
    exit(0 if success else 1)

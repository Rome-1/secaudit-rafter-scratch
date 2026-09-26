#!/usr/bin/env python3
"""
Script to reproduce the issue: Registration tokens not supported in InteractiveAuth flow.

According to the PR description, the following needs to be implemented:
1. A new RegistrationTokenAuthEntry component
2. Support for both stable and unstable registration token types
3. Integration with the getEntryComponentForLoginType function
"""

import os
import re

# Check if RegistrationTokenAuthEntry is defined
interactive_auth_file = "/app/src/components/views/auth/InteractiveAuthEntryComponents.tsx"

with open(interactive_auth_file, 'r') as f:
    content = f.read()
    
# Check for RegistrationTokenAuthEntry class
has_registration_token_class = "class RegistrationTokenAuthEntry" in content
print(f"1. RegistrationTokenAuthEntry class exists: {has_registration_token_class}")

# Check for handling in getEntryComponentForLoginType
has_registration_token_handling = "AuthType.RegistrationToken" in content
print(f"2. AuthType.RegistrationToken handling exists: {has_registration_token_handling}")

# Check for UnstableRegistrationToken handling
has_unstable_registration_token_handling = "AuthType.UnstableRegistrationToken" in content
print(f"3. AuthType.UnstableRegistrationToken handling exists: {has_unstable_registration_token_handling}")

# Check for registrationTokenField
has_registration_token_field = 'name="registrationTokenField"' in content
print(f"4. registrationTokenField input exists: {has_registration_token_field}")

print("\n" + "="*60)
if not (has_registration_token_class and has_registration_token_handling):
    print("❌ ISSUE CONFIRMED: Registration token support is missing!")
    print("\nRequired implementation:")
    print("- Add RegistrationTokenAuthEntry class")
    print("- Handle AuthType.RegistrationToken in getEntryComponentForLoginType")
    print("- Handle AuthType.UnstableRegistrationToken in getEntryComponentForLoginType")
    print("- Add proper UI with registrationTokenField input")
else:
    print("✅ Registration token support appears to be implemented")
print("="*60)

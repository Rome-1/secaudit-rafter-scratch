#!/usr/bin/env python3
"""
Script to test if the CSS duplication issue exists.
We'll check:
1. If the duplicated CSS classes exist
2. If the new EncryptionCardButtons component doesn't exist
3. If the new mx_EncryptionCard_buttons CSS class doesn't exist
"""

import os
import sys

def check_file_contains(filepath, search_strings):
    """Check if file contains any of the search strings"""
    if not os.path.exists(filepath):
        return []
    
    with open(filepath, 'r') as f:
        content = f.read()
    
    found = []
    for s in search_strings:
        if s in content:
            found.append(s)
    return found

def main():
    issues = []
    
    # Check for duplicated CSS classes
    css_files = {
        '/app/res/css/views/settings/encryption/_ChangeRecoveryKey.pcss': ['mx_ChangeRecoveryKey_footer'],
        '/app/res/css/views/settings/encryption/_ResetIdentityPanel.pcss': ['mx_ResetIdentityPanel_footer']
    }
    
    print("Checking for duplicated CSS classes...")
    for file, classes in css_files.items():
        found = check_file_contains(file, classes)
        if found:
            print(f"✗ Found duplicated CSS in {file}: {', '.join(found)}")
            issues.append(f"Duplicated CSS class in {file}")
        else:
            print(f"✓ No duplicated CSS found in {file}")
    
    # Check if new mx_EncryptionCard_buttons class exists
    print("\nChecking for new unified CSS class...")
    encryption_card_css = '/app/res/css/views/settings/encryption/_EncryptionCard.pcss'
    if check_file_contains(encryption_card_css, ['mx_EncryptionCard_buttons']):
        print(f"✓ Found unified CSS class mx_EncryptionCard_buttons in {encryption_card_css}")
    else:
        print(f"✗ Missing unified CSS class mx_EncryptionCard_buttons in {encryption_card_css}")
        issues.append("Missing unified CSS class mx_EncryptionCard_buttons")
    
    # Check if EncryptionCardButtons component exists
    print("\nChecking for EncryptionCardButtons component...")
    component_file = '/app/src/components/views/settings/encryption/EncryptionCardButtons.tsx'
    if os.path.exists(component_file):
        print(f"✓ Found EncryptionCardButtons component at {component_file}")
    else:
        # Check if it's exported from EncryptionCard.tsx
        if check_file_contains('/app/src/components/views/settings/encryption/EncryptionCard.tsx', ['EncryptionCardButtons']):
            print("✓ Found EncryptionCardButtons component in EncryptionCard.tsx")
        else:
            print(f"✗ Missing EncryptionCardButtons component")
            issues.append("Missing EncryptionCardButtons component")
    
    # Check usage in components
    print("\nChecking component usage...")
    components = {
        '/app/src/components/views/settings/encryption/ChangeRecoveryKey.tsx': {
            'old': ['mx_ChangeRecoveryKey_footer'],
            'new': ['EncryptionCardButtons']
        },
        '/app/src/components/views/settings/encryption/ResetIdentityPanel.tsx': {
            'old': ['mx_ResetIdentityPanel_footer'],
            'new': ['EncryptionCardButtons']
        }
    }
    
    for file, patterns in components.items():
        old_found = check_file_contains(file, patterns['old'])
        new_found = check_file_contains(file, patterns['new'])
        
        if old_found and not new_found:
            print(f"✗ {file} still uses old classes: {', '.join(old_found)}")
            issues.append(f"{file} uses old CSS classes")
        elif new_found and not old_found:
            print(f"✓ {file} uses new EncryptionCardButtons component")
        else:
            print(f"⚠ {file} has mixed usage")
    
    print("\n" + "="*50)
    if issues:
        print(f"❌ Found {len(issues)} issues:")
        for issue in issues:
            print(f"  - {issue}")
        sys.exit(1)
    else:
        print("✅ All checks passed! CSS duplication has been resolved.")
        sys.exit(0)

if __name__ == "__main__":
    main()
#!/usr/bin/env python3

"""
Final verification script to ensure all PR requirements have been met.
"""

import os
import re

def verify_pr_requirements():
    """Verify all PR requirements have been fulfilled."""
    print("🔍 Final Verification of PR Requirements")
    print("=" * 50)
    
    requirements = {
        "unified_css_class": False,
        "exact_properties": False,
        "duplicated_classes_removed": False,
        "react_component_created": False,
        "component_accepts_children": False,
        "component_uses_correct_class": False,
        "three_change_recovery_key_replacements": False,
        "two_reset_identity_panel_replacements": False,
        "functionality_maintained": False
    }
    
    # 1. Check unified CSS class exists with exact properties
    encryption_card_css = "/app/res/css/views/settings/encryption/_EncryptionCard.pcss"
    with open(encryption_card_css, 'r') as f:
        content = f.read()
    
    if ".mx_EncryptionCard_buttons" in content:
        requirements["unified_css_class"] = True
        match = re.search(r'\.mx_EncryptionCard_buttons\s*\{([^}]+)\}', content, re.DOTALL)
        if match:
            rule = match.group(1)
            expected = [
                "display: flex;",
                "flex-direction: column;", 
                "gap: var(--cpd-space-4x);",
                "justify-content: center;"
            ]
            if all(prop.strip() in rule for prop in expected):
                requirements["exact_properties"] = True
    
    # 2. Check duplicated CSS classes are removed
    old_css_files = [
        "/app/res/css/views/settings/encryption/_ChangeRecoveryKey.pcss",
        "/app/res/css/views/settings/encryption/_ResetIdentityPanel.pcss"
    ]
    old_classes_removed = True
    for css_file in old_css_files:
        with open(css_file, 'r') as f:
            content = f.read()
        if "mx_ChangeRecoveryKey_footer" in content or "mx_ResetIdentityPanel_footer" in content:
            old_classes_removed = False
            break
    requirements["duplicated_classes_removed"] = old_classes_removed
    
    # 3. Check React component was created
    encryption_card_tsx = "/app/src/components/views/settings/encryption/EncryptionCard.tsx"
    with open(encryption_card_tsx, 'r') as f:
        content = f.read()
    
    if "export function EncryptionCardButtons" in content:
        requirements["react_component_created"] = True
        if "PropsWithChildren" in content and "{ children }" in content:
            requirements["component_accepts_children"] = True
        if 'className="mx_EncryptionCard_buttons"' in content:
            requirements["component_uses_correct_class"] = True
    
    # 4. Check replacements in component files
    change_recovery_key_tsx = "/app/src/components/views/settings/encryption/ChangeRecoveryKey.tsx"
    with open(change_recovery_key_tsx, 'r') as f:
        content = f.read()
    if content.count("<EncryptionCardButtons>") == 3:
        requirements["three_change_recovery_key_replacements"] = True
    
    reset_identity_panel_tsx = "/app/src/components/views/settings/encryption/ResetIdentityPanel.tsx"
    with open(reset_identity_panel_tsx, 'r') as f:
        content = f.read()
    if content.count("<EncryptionCardButtons>") == 1:
        requirements["two_reset_identity_panel_replacements"] = True
    
    # 5. Check functionality is maintained (buttons are still inside the components)
    functionality_checks = []
    
    # Check ChangeRecoveryKey maintains button structure
    change_key_patterns = [
        r'<EncryptionCardButtons>\s*<Button[^>]*onClick={onContinueClick}',
        r'<EncryptionCardButtons>\s*<Button[^>]*onClick={onConfirmClick}',
        r'<EncryptionCardButtons>\s*<Button[^>]*disabled={\!isKeyValid}'
    ]
    
    with open(change_recovery_key_tsx, 'r') as f:
        content = f.read()
    
    for pattern in change_key_patterns:
        if re.search(pattern, content, re.DOTALL):
            functionality_checks.append(True)
        else:
            functionality_checks.append(False)
    
    # Check ResetIdentityPanel maintains button structure  
    reset_pattern = r'<EncryptionCardButtons>\s*<Button[^>]*destructive={true}'
    with open(reset_identity_panel_tsx, 'r') as f:
        content = f.read()
    
    if re.search(reset_pattern, content, re.DOTALL):
        functionality_checks.append(True)
    else:
        functionality_checks.append(False)
    
    requirements["functionality_maintained"] = all(functionality_checks)
    
    # Print results
    print("\n📋 Requirement Checklist:")
    checklist = [
        ("✅ Create unified CSS class mx_EncryptionCard_buttons", requirements["unified_css_class"]),
        ("✅ CSS has exact properties (display: flex, flex-direction: column, gap: var(--cpd-space-4x), justify-content: center)", requirements["exact_properties"]),
        ("✅ Remove duplicated CSS classes mx_ChangeRecoveryKey_footer and mx_ResetIdentityPanel_footer", requirements["duplicated_classes_removed"]),
        ("✅ Create EncryptionCardButtons React component", requirements["react_component_created"]),
        ("✅ Component accepts children props", requirements["component_accepts_children"]),
        ("✅ Component renders with mx_EncryptionCard_buttons class", requirements["component_uses_correct_class"]),
        ("✅ Replace 3 instances in ChangeRecoveryKey component", requirements["three_change_recovery_key_replacements"]),
        ("✅ Replace 1 instance in ResetIdentityPanel component", requirements["two_reset_identity_panel_replacements"]),
        ("✅ Maintain all existing button functionality", requirements["functionality_maintained"])
    ]
    
    for desc, passed in checklist:
        status = "✅" if passed else "❌"
        print(f"{status} {desc.replace('✅ ', '')}")
    
    all_passed = all(requirements.values())
    print(f"\n🎯 Overall Status: {'✅ ALL REQUIREMENTS MET' if all_passed else '❌ SOME REQUIREMENTS NOT MET'}")
    
    return all_passed

def check_code_quality():
    """Check for code quality and best practices."""
    print("\n" + "=" * 50)
    print("🧹 Code Quality Checks")
    
    # Check for proper imports
    change_recovery = "/app/src/components/views/settings/encryption/ChangeRecoveryKey.tsx"
    reset_identity = "/app/src/components/views/settings/encryption/ResetIdentityPanel.tsx"
    
    for file_path in [change_recovery, reset_identity]:
        with open(file_path, 'r') as f:
            content = f.read()
        
        filename = os.path.basename(file_path)
        
        # Check proper import structure
        if "import { EncryptionCard, EncryptionCardButtons } from" in content:
            print(f"✅ {filename}: Proper named imports used")
        else:
            print(f"❌ {filename}: Import structure needs improvement")
        
        # Check no unused imports of old classes
        old_patterns = ["mx_ChangeRecoveryKey_footer", "mx_ResetIdentityPanel_footer"]
        has_old_refs = any(pattern in content for pattern in old_patterns)
        if not has_old_refs:
            print(f"✅ {filename}: No references to old CSS classes")
        else:
            print(f"❌ {filename}: Still contains references to old classes")

def main():
    success = verify_pr_requirements()
    check_code_quality()
    
    print("\n" + "=" * 50)
    if success:
        print("🎉 SUCCESS: All PR requirements have been successfully implemented!")
        print("📝 Summary of changes:")
        print("   • Created unified CSS class mx_EncryptionCard_buttons")
        print("   • Removed duplicated CSS classes")
        print("   • Created EncryptionCardButtons React component")
        print("   • Replaced all component-specific footer divs")
        print("   • Maintained all existing button functionality")
    else:
        print("❌ FAILURE: Some requirements are not met. Please review the checklist above.")
    
    return 0 if success else 1

if __name__ == "__main__":
    exit(main())
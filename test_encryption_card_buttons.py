#!/usr/bin/env python3

"""
Test script to verify that the EncryptionCardButtons component was implemented correctly
and all duplicated CSS has been consolidated.
"""

import os
import re

def check_css_consolidation():
    """Check that the CSS has been properly consolidated."""
    print("=== Testing CSS Consolidation ===\n")
    
    # Check that the new CSS class exists
    encryption_card_css = "/app/res/css/views/settings/encryption/_EncryptionCard.pcss"
    
    with open(encryption_card_css, 'r') as f:
        content = f.read()
    
    if ".mx_EncryptionCard_buttons" in content:
        print("✅ mx_EncryptionCard_buttons CSS class exists")
        
        # Extract the rule to verify properties
        match = re.search(r'\.mx_EncryptionCard_buttons\s*\{([^}]+)\}', content, re.DOTALL)
        if match:
            rule = match.group(1).strip()
            expected_props = [
                "display: flex",
                "flex-direction: column", 
                "gap: var(--cpd-space-4x)",
                "justify-content: center"
            ]
            
            all_props_present = all(prop in rule for prop in expected_props)
            if all_props_present:
                print("✅ All required CSS properties are present")
                print(f"   Rule: {rule.replace(chr(10), ' ')}")
            else:
                print("❌ Missing required CSS properties")
                print(f"   Expected: {expected_props}")
                print(f"   Found: {rule}")
    else:
        print("❌ mx_EncryptionCard_buttons CSS class not found")

def check_component_implementation():
    """Check that the React component was implemented correctly."""
    print("\n=== Testing Component Implementation ===\n")
    
    encryption_card_tsx = "/app/src/components/views/settings/encryption/EncryptionCard.tsx"
    
    with open(encryption_card_tsx, 'r') as f:
        content = f.read()
    
    if "export function EncryptionCardButtons" in content:
        print("✅ EncryptionCardButtons component is exported")
        
        # Check the implementation
        if 'return <div className="mx_EncryptionCard_buttons">{children}</div>' in content:
            print("✅ Component uses correct CSS class")
        else:
            print("❌ Component does not use correct CSS class")
            
        if "PropsWithChildren" in content:
            print("✅ Component accepts children props")
        else:
            print("❌ Component does not properly accept children")
    else:
        print("❌ EncryptionCardButtons component not found")

def check_usage_replacement():
    """Check that all old class usages have been replaced."""
    print("\n=== Testing Usage Replacement ===\n")
    
    files_to_check = [
        "/app/src/components/views/settings/encryption/ChangeRecoveryKey.tsx",
        "/app/src/components/views/settings/encryption/ResetIdentityPanel.tsx"
    ]
    
    total_component_usage = 0
    
    for file_path in files_to_check:
        with open(file_path, 'r') as f:
            content = f.read()
        
        # Check import
        if "EncryptionCardButtons" in content and "import" in content:
            print(f"✅ {os.path.basename(file_path)}: EncryptionCardButtons is imported")
        else:
            print(f"❌ {os.path.basename(file_path)}: EncryptionCardButtons not imported")
        
        # Count usage
        component_usage = content.count("<EncryptionCardButtons>")
        total_component_usage += component_usage
        if component_usage > 0:
            print(f"✅ {os.path.basename(file_path)}: {component_usage} usage(s) of EncryptionCardButtons")
        else:
            print(f"❌ {os.path.basename(file_path)}: No usage of EncryptionCardButtons")
    
    print(f"\n📊 Total EncryptionCardButtons usage: {total_component_usage}")
    
    # Should be 4 total (3 in ChangeRecoveryKey + 1 in ResetIdentityPanel)
    if total_component_usage == 4:
        print("✅ Expected number of component usages found")
    else:
        print(f"❌ Expected 4 usages, found {total_component_usage}")

def check_cleanup():
    """Check that old CSS classes have been completely removed."""
    print("\n=== Testing Cleanup ===\n")
    
    old_classes = ["mx_ChangeRecoveryKey_footer", "mx_ResetIdentityPanel_footer"]
    
    # Check CSS files
    css_files = [
        "/app/res/css/views/settings/encryption/_ChangeRecoveryKey.pcss",
        "/app/res/css/views/settings/encryption/_ResetIdentityPanel.pcss"
    ]
    
    for css_file in css_files:
        with open(css_file, 'r') as f:
            content = f.read()
        
        old_classes_found = [cls for cls in old_classes if cls in content]
        if old_classes_found:
            print(f"❌ {os.path.basename(css_file)}: Still contains {old_classes_found}")
        else:
            print(f"✅ {os.path.basename(css_file)}: Old CSS classes removed")
    
    # Check TSX files
    tsx_files = [
        "/app/src/components/views/settings/encryption/ChangeRecoveryKey.tsx",
        "/app/src/components/views/settings/encryption/ResetIdentityPanel.tsx"
    ]
    
    for tsx_file in tsx_files:
        with open(tsx_file, 'r') as f:
            content = f.read()
        
        old_classes_found = [cls for cls in old_classes if cls in content]
        if old_classes_found:
            print(f"❌ {os.path.basename(tsx_file)}: Still contains {old_classes_found}")
        else:
            print(f"✅ {os.path.basename(tsx_file)}: Old CSS class references removed")

def main():
    print("🧪 Testing Encryption Settings Button Consolidation")
    print("=" * 60 + "\n")
    
    check_css_consolidation()
    check_component_implementation()
    check_usage_replacement()
    check_cleanup()
    
    print("\n" + "=" * 60)
    print("🎉 Test completed! All checks should show ✅ for successful implementation.")

if __name__ == "__main__":
    main()
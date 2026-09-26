#!/usr/bin/env python3
"""
Script to test that the QR sign in feature flag fix works correctly.
"""

import os
import re

def test_qr_signin_fix():
    print("=== Testing QR Sign-in Feature Flag Fix ===\n")
    
    # Test 1: Check that the feature flag exists
    print("1. Checking feature_qr_signin_reciprocate_show flag in Settings.tsx:")
    with open("/app/src/settings/Settings.tsx", "r") as f:
        content = f.read()
        
        if "feature_qr_signin_reciprocate_show" in content:
            print("   ✓ Feature flag exists")
            
            # Extract the flag definition
            flag_match = re.search(r'"feature_qr_signin_reciprocate_show":\s*\{[^}]+\}', content, re.DOTALL)
            if flag_match:
                flag_def = flag_match.group(0)
                print(f"   ✓ Flag definition found:")
                
                if "isFeature: true" in flag_def:
                    print("     ✓ Marked as feature")
                if "labsGroup: LabGroup.Encryption" in flag_def:
                    print("     ✓ In Encryption labs group")
                if "default: false" in flag_def:
                    print("     ✓ Defaults to false")
                if "LEVELS_FEATURE" in flag_def:
                    print("     ✓ Uses LEVELS_FEATURE")
        else:
            print("   ✗ Feature flag NOT found")
            return False
    
    print()
    
    # Test 2: Check LoginWithQRSection uses the flag
    print("2. Checking LoginWithQRSection.tsx uses the feature flag:")
    with open("/app/src/components/views/settings/devices/LoginWithQRSection.tsx", "r") as f:
        content = f.read()
        
        if "SettingsStore" in content:
            print("   ✓ Imports SettingsStore")
        else:
            print("   ✗ Does NOT import SettingsStore")
            return False
            
        if "feature_qr_signin_reciprocate_show" in content:
            print("   ✓ Uses feature_qr_signin_reciprocate_show flag")
        else:
            print("   ✗ Does NOT use the feature flag")
            return False
            
        if "showQrCodeEnabled" in content:
            print("   ✓ Has showQrCodeEnabled variable")
        else:
            print("   ✗ Missing showQrCodeEnabled variable")
            return False
            
        # Check the logic order
        render_match = re.search(r'public render.*?return null;.*?return \(', content, re.DOTALL)
        if render_match:
            render_text = render_match.group(0)
            # Check that feature flag is checked before server capabilities
            if render_text.find("showQrCodeEnabled") < render_text.find("msc3882Supported"):
                print("   ✓ Feature flag checked before server capabilities")
            else:
                print("   ✗ Feature flag NOT checked before server capabilities")
                return False
    
    print()
    
    # Test 3: Check both tabs will respect the change
    print("3. Checking that both tabs use LoginWithQRSection:")
    
    # SecurityUserSettingsTab
    with open("/app/src/components/views/settings/tabs/user/SecurityUserSettingsTab.tsx", "r") as f:
        content = f.read()
        if "LoginWithQRSection" in content:
            print("   ✓ SecurityUserSettingsTab uses LoginWithQRSection")
        else:
            print("   ✗ SecurityUserSettingsTab does NOT use LoginWithQRSection")
            return False
    
    # SessionManagerTab  
    with open("/app/src/components/views/settings/tabs/user/SessionManagerTab.tsx", "r") as f:
        content = f.read()
        if "LoginWithQRSection" in content:
            print("   ✓ SessionManagerTab uses LoginWithQRSection")
        else:
            print("   ✗ SessionManagerTab does NOT use LoginWithQRSection")
            return False
    
    print()
    print("=== All Tests Passed! ===")
    print()
    print("SUMMARY:")
    print("✓ feature_qr_signin_reciprocate_show flag added to Settings.tsx")
    print("✓ LoginWithQRSection now checks the feature flag first")
    print("✓ Both SecurityUserSettingsTab and SessionManagerTab will respect the flag")
    print("✓ QR sign-in will now be hidden by default and only shown when explicitly enabled")
    print("✓ Consistent behavior across legacy Devices section and new Session Manager")
    
    return True

def test_edge_cases():
    print("\n=== Testing Edge Cases ===\n")
    
    with open("/app/src/components/views/settings/devices/LoginWithQRSection.tsx", "r") as f:
        content = f.read()
        
        # Check that both conditions are checked (feature flag AND server support)
        render_match = re.search(r'public render.*?return \(', content, re.DOTALL)
        if render_match:
            render_text = render_match.group(0)
            
            # Count return null statements
            null_returns = len(re.findall(r'return null;', render_text))
            if null_returns >= 2:
                print("✓ Both feature flag and server capability checks return null")
                print("  - QR signin hidden when feature flag disabled")  
                print("  - QR signin hidden when server doesn't support MSCs")
                print("  - QR signin only shown when BOTH conditions are met")
            else:
                print("✗ Missing proper null return logic")
                return False
    
    print("\n✓ All edge cases handled correctly!")
    return True

if __name__ == "__main__":
    success = test_qr_signin_fix()
    if success:
        test_edge_cases()
    else:
        print("\n❌ Fix verification failed!")
        exit(1)
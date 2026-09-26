#!/usr/bin/env python3
"""
Script to reproduce the QR sign in visibility issue.
This script will check the current implementation to see if QR sign in 
is shown even when the feature flag is not enabled.
"""

import os
import re

def analyze_qr_signin_implementation():
    print("=== Analyzing QR Sign-in Implementation ===\n")
    
    # Check LoginWithQRSection.tsx
    print("1. Checking LoginWithQRSection.tsx:")
    with open("/app/src/components/views/settings/devices/LoginWithQRSection.tsx", "r") as f:
        content = f.read()
        
        # Check if it uses feature flags
        if "SettingsStore" in content:
            print("   ✓ Uses SettingsStore")
        else:
            print("   ✗ Does NOT use SettingsStore")
            
        if "feature_qr_signin" in content:
            print("   ✓ Uses QR signin feature flag")
        else:
            print("   ✗ Does NOT use QR signin feature flag")
            
        # Check what determines visibility
        render_method = re.search(r'public render.*?return null;.*?return \(.*?\);', content, re.DOTALL)
        if render_method:
            method_text = render_method.group(0)
            print(f"   Current visibility logic: Checks MSC3882 and MSC3886 support only")
        
    print()
    
    # Check SecurityUserSettingsTab.tsx
    print("2. Checking SecurityUserSettingsTab.tsx:")
    with open("/app/src/components/views/settings/tabs/user/SecurityUserSettingsTab.tsx", "r") as f:
        content = f.read()
        
        # Check if it uses feature flags for QR
        if "feature_qr_signin" in content:
            print("   ✓ Uses QR signin feature flag")
        else:
            print("   ✗ Does NOT use QR signin feature flag")
            
        # Check if LoginWithQRSection is conditionally rendered
        if "LoginWithQRSection" in content:
            print("   ✓ Renders LoginWithQRSection")
            # Check if it's conditional
            if re.search(r'SettingsStore\.getValue.*LoginWithQRSection', content, re.DOTALL):
                print("   ✓ Conditionally renders based on settings")
            else:
                print("   ✗ Renders unconditionally (only depends on useNewSessionManager)")
    
    print()
    
    # Check SessionManagerTab.tsx  
    print("3. Checking SessionManagerTab.tsx:")
    with open("/app/src/components/views/settings/tabs/user/SessionManagerTab.tsx", "r") as f:
        content = f.read()
        
        if "feature_qr_signin" in content:
            print("   ✓ Uses QR signin feature flag")
        else:
            print("   ✗ Does NOT use QR signin feature flag")
            
        if "LoginWithQRSection" in content:
            print("   ✓ Renders LoginWithQRSection")
            if re.search(r'SettingsStore\.getValue.*LoginWithQRSection', content, re.DOTALL):
                print("   ✓ Conditionally renders based on settings")
            else:
                print("   ✗ Renders unconditionally")
    
    print()
    
    # Check Settings.tsx for existing QR flags
    print("4. Checking Settings.tsx for QR-related flags:")
    with open("/app/src/settings/Settings.tsx", "r") as f:
        content = f.read()
        
        qr_settings = re.findall(r'"[^"]*qr[^"]*".*?{[^}]+}', content, re.IGNORECASE | re.DOTALL)
        if qr_settings:
            print(f"   Found {len(qr_settings)} QR-related settings:")
            for setting in qr_settings:
                print(f"     - {setting[:50]}...")
        else:
            print("   ✗ No QR-related feature flags found")
    
    print("\n=== Summary ===")
    print("ISSUE: QR Sign-in is currently visible based only on homeserver capabilities,")
    print("not on any feature flag. This means it shows up even when not intended.")
    print("\nNEEDED:")
    print("1. Add 'feature_qr_signin_reciprocate_show' flag to Settings.tsx")  
    print("2. Modify LoginWithQRSection to check this flag")
    print("3. Ensure both SecurityUserSettingsTab and SessionManagerTab respect the flag")

if __name__ == "__main__":
    analyze_qr_signin_implementation()
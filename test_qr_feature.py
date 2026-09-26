#!/usr/bin/env python3
"""
Test script to verify QR sign-in feature behavior.
This script simulates the issue described in the PR where QR sign-in
is visible even when unsupported.
"""

import re
import os

def check_feature_flag_exists():
    """Check if feature_qr_signin_reciprocate_show exists in Settings.tsx"""
    settings_file = '/app/src/settings/Settings.tsx'
    with open(settings_file, 'r') as f:
        content = f.read()
        if 'feature_qr_signin_reciprocate_show' in content:
            print("✓ Feature flag 'feature_qr_signin_reciprocate_show' exists in Settings.tsx")
            return True
        else:
            print("✗ Feature flag 'feature_qr_signin_reciprocate_show' NOT found in Settings.tsx")
            return False

def check_login_with_qr_section():
    """Check if LoginWithQRSection checks for the feature flag"""
    login_qr_file = '/app/src/components/views/settings/devices/LoginWithQRSection.tsx'
    with open(login_qr_file, 'r') as f:
        content = f.read()
        
        # Check if SettingsStore is imported
        if 'SettingsStore' in content:
            print("✓ SettingsStore is imported in LoginWithQRSection.tsx")
        else:
            print("✗ SettingsStore is NOT imported in LoginWithQRSection.tsx")
            
        # Check if feature flag is checked
        if 'feature_qr_signin_reciprocate_show' in content:
            print("✓ Feature flag 'feature_qr_signin_reciprocate_show' is checked in LoginWithQRSection.tsx")
            return True
        else:
            print("✗ Feature flag 'feature_qr_signin_reciprocate_show' is NOT checked in LoginWithQRSection.tsx")
            return False

def check_security_settings_tab():
    """Check if SecurityUserSettingsTab checks for the feature flag"""
    security_tab_file = '/app/src/components/views/settings/tabs/user/SecurityUserSettingsTab.tsx'
    with open(security_tab_file, 'r') as f:
        content = f.read()
        
        # Check if the feature flag is used when rendering LoginWithQRSection
        lines = content.split('\n')
        for i, line in enumerate(lines):
            if 'LoginWithQRSection' in line and 'onShowQr' in line:
                print(f"Found LoginWithQRSection usage at line {i+1}: {line.strip()}")
                # Check if there's conditional rendering
                context_start = max(0, i-5)
                context_end = min(len(lines), i+5)
                context = '\n'.join(lines[context_start:context_end])
                if 'feature_qr_signin_reciprocate_show' in context or 'SettingsStore.getValue' in context:
                    print("✓ LoginWithQRSection is conditionally rendered based on feature flag")
                    return True
                else:
                    print("✗ LoginWithQRSection is NOT conditionally rendered based on feature flag")
                    return False
    return False

def check_session_manager_tab():
    """Check if SessionManagerTab checks for the feature flag"""
    session_tab_file = '/app/src/components/views/settings/tabs/user/SessionManagerTab.tsx'
    with open(session_tab_file, 'r') as f:
        content = f.read()
        
        # Check if the feature flag is used when rendering LoginWithQRSection
        lines = content.split('\n')
        for i, line in enumerate(lines):
            if 'LoginWithQRSection' in line and 'onShowQr' in line:
                print(f"Found LoginWithQRSection usage at line {i+1}: {line.strip()}")
                # Check if there's conditional rendering
                context_start = max(0, i-5)
                context_end = min(len(lines), i+5)
                context = '\n'.join(lines[context_start:context_end])
                if 'feature_qr_signin_reciprocate_show' in context or 'SettingsStore.getValue' in context:
                    print("✓ LoginWithQRSection is conditionally rendered based on feature flag")
                    return True
                else:
                    print("✗ LoginWithQRSection is NOT conditionally rendered based on feature flag")
                    return False
    return False

def main():
    print("=" * 60)
    print("QR Sign-in Feature Flag Verification")
    print("=" * 60)
    
    results = []
    
    print("\n1. Checking Settings.tsx for feature flag definition...")
    results.append(check_feature_flag_exists())
    
    print("\n2. Checking LoginWithQRSection.tsx...")
    results.append(check_login_with_qr_section())
    
    print("\n3. Checking SecurityUserSettingsTab.tsx...")
    results.append(check_security_settings_tab())
    
    print("\n4. Checking SessionManagerTab.tsx...")
    results.append(check_session_manager_tab())
    
    print("\n" + "=" * 60)
    if all(results):
        print("✓ All checks passed! QR sign-in is properly gated.")
    else:
        print("✗ Some checks failed. QR sign-in is NOT properly gated.")
        print("\nRequired changes:")
        if not results[0]:
            print("- Add 'feature_qr_signin_reciprocate_show' feature flag to Settings.tsx")
        if not results[1]:
            print("- Update LoginWithQRSection to check the feature flag")
        if not results[2]:
            print("- Update SecurityUserSettingsTab to conditionally render LoginWithQRSection")
        if not results[3]:
            print("- Update SessionManagerTab to conditionally render LoginWithQRSection")
    print("=" * 60)

if __name__ == "__main__":
    main()
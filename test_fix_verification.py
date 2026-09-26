#!/usr/bin/env python3
"""
Verification script to test that the authentication bypass vulnerability is fixed.

This script simulates the exact scenario described in the PR:
- Send GET request to /rest/ping.view 
- Use parameters: v=1.16.1&c=test&u=nonexistentuser
- No password or token credentials provided
- Should return authentication failure (not success)
"""

import json
import urllib.request
import urllib.parse
import xml.etree.ElementTree as ET
from urllib.error import HTTPError

def test_authentication_bypass_fix():
    """Test that the authentication bypass vulnerability is fixed."""
    
    # Simulate the exact scenario from the PR description
    base_url = "http://localhost:4533"  # Default Navidrome URL
    endpoint = "/rest/ping.view"
    
    # Parameters exactly as described in the PR
    params = {
        'v': '1.16.1',
        'c': 'test', 
        'u': 'nonexistentuser',
        'f': 'xml'  # Use XML format to easily check for error codes
    }
    
    url = base_url + endpoint + '?' + urllib.parse.urlencode(params)
    
    print("🔒 Testing Authentication Bypass Fix")
    print("=" * 50)
    print(f"URL: {url}")
    print(f"Username: nonexistentuser (non-existent)")
    print(f"Credentials: None provided")
    print()
    
    try:
        response = urllib.request.urlopen(url, timeout=10)
        response_data = response.read().decode('utf-8')
        status_code = response.getcode()
        
        print(f"❌ HTTP Status: {status_code}")
        print(f"❌ Response Body: {response_data}")
        
        # Parse XML response to check for Subsonic error
        try:
            root = ET.fromstring(response_data)
            status = root.get('status')
            
            if status == 'failed':
                # Check if it's an authentication error (code 40)
                error_elem = root.find('error')
                if error_elem is not None:
                    error_code = error_elem.get('code')
                    error_message = error_elem.get('message')
                    
                    if error_code == '40':
                        print(f"✅ SUCCESS: Authentication properly rejected!")
                        print(f"   Error Code: {error_code} (Authentication Failure)")
                        print(f"   Message: {error_message}")
                        return True
                    else:
                        print(f"❓ UNEXPECTED: Different error code: {error_code}")
                        print(f"   Message: {error_message}")
                        return False
            elif status == 'ok':
                print(f"❌ VULNERABILITY: Request succeeded when it should have failed!")
                print(f"   Status: {status}")
                return False
            else:
                print(f"❓ UNEXPECTED: Unknown status: {status}")
                return False
                
        except ET.ParseError:
            print("❓ UNEXPECTED: Could not parse XML response")
            return False
            
    except HTTPError as e:
        # HTTP error responses might also indicate proper authentication failure
        status_code = e.code
        response_data = e.read().decode('utf-8')
        
        print(f"HTTP Status: {status_code}")
        print(f"Response: {response_data}")
        
        if status_code in [401, 403]:
            print("✅ SUCCESS: HTTP-level authentication failure (expected)")
            return True
        else:
            print(f"❓ UNEXPECTED: HTTP error {status_code}")
            return False
            
    except Exception as e:
        print(f"❌ ERROR: {str(e)}")
        print("   (This might be normal if Navidrome is not running)")
        return None

if __name__ == '__main__':
    result = test_authentication_bypass_fix()
    
    if result is True:
        print("\n🎉 VULNERABILITY FIXED: Authentication bypass vulnerability is resolved!")
        exit(0)
    elif result is False:
        print("\n⚠️  VULNERABILITY STILL EXISTS: Authentication bypass vulnerability detected!")
        exit(1) 
    else:
        print("\n❓ TEST INCONCLUSIVE: Could not determine vulnerability status")
        exit(2)
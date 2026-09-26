import requests

# Configurations - Adjust these as necessary
target_url = "http://localhost:4567/admin/uploads/category-picture"  # Example URL
file_path = "/app/invalid_image.txt"  # Path to an invalid image file to simulate the error

# Attempt to upload
files = {'files': open(file_path, 'rb')}
params = { 'params': '{"cid": 1}' }

try:
    response = requests.post(target_url, files=files, data=params)
    
    print("Status Code:", response.status_code)
    print("Response JSON:", response.json())
    
    if response.status_code == 200 and "error" in response.json():
        print("Issue replicated: Received HTTP 200 for an error scenario.")
    else:
        print("Did not replicate the issue correctly or it has been resolved.")

except Exception as e:
    print("Error occurred:", e)
finally:
    if 'files' in locals():
        files['files'].close()
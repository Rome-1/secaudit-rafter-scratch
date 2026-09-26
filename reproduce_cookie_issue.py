import requests

def test_cookie_persistence():
    s = requests.Session()
    r = s.get('http://httpbin.org/redirect/1', cookies={'Hi': 'There'})
    
    print("Testing cookie in final request:")
    try:
        print(f"Cookie header: {r.request.headers['Cookie']}")
    except KeyError:
        print("ERROR: Cookie header not found in final request!")
    
    print("\nTesting cookie in redirect history:")
    try:
        print(f"Cookie header in first request: {r.history[0].request.headers['Cookie']}")
    except KeyError:
        print("ERROR: Cookie header not found in first request!")

if __name__ == "__main__":
    test_cookie_persistence()
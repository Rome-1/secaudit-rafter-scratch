import requests

def test_multiple_cookies():
    s = requests.Session()
    r = s.get('http://httpbin.org/redirect/1', cookies={'Hi': 'There', 'Another': 'Cookie'})
    
    print("Testing multiple cookies in final request:")
    try:
        print(f"Cookie header: {r.request.headers['Cookie']}")
    except KeyError:
        print("ERROR: Cookie header not found in final request!")
    
    print("\nTesting multiple cookies in redirect history:")
    try:
        print(f"Cookie header in first request: {r.history[0].request.headers['Cookie']}")
    except KeyError:
        print("ERROR: Cookie header not found in first request!")

def test_session_and_request_cookies():
    s = requests.Session()
    s.cookies.update({'Session': 'Cookie'})
    r = s.get('http://httpbin.org/redirect/1', cookies={'Request': 'Cookie'})
    
    print("\nTesting session + request cookies in final request:")
    try:
        print(f"Cookie header: {r.request.headers['Cookie']}")
    except KeyError:
        print("ERROR: Cookie header not found in final request!")
    
    print("\nTesting session + request cookies in redirect history:")
    try:
        print(f"Cookie header in first request: {r.history[0].request.headers['Cookie']}")
    except KeyError:
        print("ERROR: Cookie header not found in first request!")

def test_empty_cookies():
    s = requests.Session()
    r = s.get('http://httpbin.org/redirect/1', cookies={})
    
    print("\nTesting empty cookies dict:")
    try:
        print(f"Cookie header: {r.request.headers['Cookie']}")
    except KeyError:
        print("No Cookie header found (expected for empty cookies)")

if __name__ == "__main__":
    test_multiple_cookies()
    test_session_and_request_cookies()
    test_empty_cookies()
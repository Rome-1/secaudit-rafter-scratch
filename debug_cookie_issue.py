#!/usr/bin/env python
"""Debug script to understand the cookie issue."""

import requests

def debug_cookie_persistence():
    """Debug the cookie persistence issue."""
    
    print("=== Debugging cookie persistence ===")
    
    # Create a session
    s = requests.Session()
    
    # Make a request with cookies to a redirect endpoint
    print("Making request to redirect endpoint with cookies...")
    r = s.get('http://httpbin.org/redirect/1', cookies={'foo': 'bar'})
    
    print("Final response URL:", r.url)
    print("Request headers:", dict(r.request.headers))
    print("History length:", len(r.history))
    
    if r.history:
        print("First request headers:", dict(r.history[0].request.headers))
        print("First request URL:", r.history[0].request.url)
    
    # Check if cookies are in the headers
    if 'Cookie' in r.request.headers:
        print("Cookie header in final request:", r.request.headers['Cookie'])
    else:
        print("No Cookie header in final request")
        
    if r.history and 'Cookie' in r.history[0].request.headers:
        print("Cookie header in first request:", r.history[0].request.headers['Cookie'])
    else:
        print("No Cookie header in first request")

if __name__ == '__main__':
    debug_cookie_persistence()
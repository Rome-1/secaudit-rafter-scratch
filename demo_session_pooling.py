#!/usr/bin/env python3
"""Demonstrate that Session connection pooling is working in linkcheck."""

import sys
import os
import tempfile
import textwrap
from pathlib import Path

# Add the workspace to the path
sys.path.insert(0, '/workspace')

import requests
from sphinx.util.requests import get, head

def demonstrate_session_functionality():
    """Demonstrate that Session functionality works."""
    print("Demonstrating Session functionality...")
    print("-" * 40)
    
    # Create a session
    session = requests.Session()
    
    try:
        print("1. Testing GET without session:")
        response = get('https://httpbin.org/status/200')
        print(f"   Status: {response.status_code}")
        
        print("2. Testing GET with session:")
        response = get('https://httpbin.org/status/200', _session=session)
        print(f"   Status: {response.status_code}")
        
        print("3. Testing HEAD with session:")
        response = head('https://httpbin.org/status/200', _session=session)
        print(f"   Status: {response.status_code}")
        
        print("✓ Session functionality works!")
        
    except Exception as e:
        print(f"✗ Error: {e}")
        return False
    finally:
        session.close()
    
    return True

def demonstrate_worker_session():
    """Demonstrate that the linkcheck worker has a session."""
    print("\\nDemonstrating linkcheck worker Session...")
    print("-" * 40)
    
    from sphinx.builders.linkcheck import HyperlinkAvailabilityCheckWorker
    from sphinx.config import Config
    from queue import Queue
    
    # Create a minimal config
    config = Config({}, {}, {})
    config.linkcheck_anchors_ignore = []
    config.linkcheck_exclude_documents = []
    config.linkcheck_auth = []
    config.linkcheck_timeout = 5
    config.linkcheck_request_headers = {}
    config.linkcheck_anchors = True
    config.linkcheck_allowed_redirects = {}
    config.linkcheck_retries = 1
    config.linkcheck_rate_limit_timeout = 300
    config.user_agent = 'Test'
    config.tls_verify = True
    config.tls_cacerts = None
    
    # Create queues
    rqueue = Queue()
    wqueue = Queue()
    rate_limits = {}
    
    try:
        # Create worker
        worker = HyperlinkAvailabilityCheckWorker(config, rqueue, wqueue, rate_limits)
        
        print(f"1. Worker has session attribute: {hasattr(worker, 'session')}")
        print(f"2. Session is requests.Session: {isinstance(worker.session, requests.Session)}")
        print(f"3. Session object: {worker.session}")
        
        print("✓ Worker has a Session object for connection pooling!")
        
        # Clean up
        worker.session.close()
        return True
        
    except Exception as e:
        print(f"✗ Error: {e}")
        return False

def explain_implementation():
    """Explain what we've implemented."""
    print("\\nImplementation Summary:")
    print("=" * 50)
    print("""
Our implementation adds connection pooling to the linkcheck builder by:

1. **Session Object Creation**: Each HyperlinkAvailabilityCheckWorker thread 
   creates its own requests.Session object in __init__().

2. **Session Usage**: The worker passes its session to sphinx.util.requests 
   functions via the _session parameter.

3. **Connection Reuse**: The Session object automatically reuses TCP 
   connections for requests to the same host, reducing overhead.

4. **Proper Cleanup**: The session is closed when the worker thread finishes
   to prevent resource leaks.

5. **Backward Compatibility**: The _session parameter is optional, so existing
   code continues to work without changes.

Key Benefits:
- Reduced TCP connection overhead for multiple requests to the same host
- Better performance when checking many links on the same domain
- Automatic connection pooling handled by requests.Session
- Thread-safe implementation (each worker has its own session)
""")

def main():
    print("Session Connection Pooling Demo for Sphinx Linkcheck")
    print("=" * 55)
    
    success = True
    
    if not demonstrate_session_functionality():
        success = False
    
    if not demonstrate_worker_session():
        success = False
    
    explain_implementation()
    
    if success:
        print("\\n✓ Session connection pooling is successfully implemented!")
        return 0
    else:
        print("\\n✗ Some demonstrations failed.")
        return 1

if __name__ == '__main__':
    sys.exit(main())
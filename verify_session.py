#!/usr/bin/env python3
"""Verify that Session functionality is working in linkcheck."""

import sys
import requests

# Add the workspace to the path
sys.path.insert(0, '/workspace')

from sphinx.util.requests import get, head
from sphinx.builders.linkcheck import HyperlinkAvailabilityCheckWorker
from sphinx.config import Config
from queue import Queue

def test_session_parameter():
    """Test that the _session parameter works in sphinx.util.requests functions."""
    print("Testing Session parameter in sphinx.util.requests...")
    
    session = requests.Session()
    
    try:
        # Test GET without session
        response = get('https://httpbin.org/status/200')
        print(f"GET without session: {response.status_code}")
        
        # Test GET with session
        response = get('https://httpbin.org/status/200', _session=session)
        print(f"GET with session: {response.status_code}")
        
        # Test HEAD with session
        response = head('https://httpbin.org/status/200', _session=session)
        print(f"HEAD with session: {response.status_code}")
        
        print("✓ Session parameter works correctly!")
        return True
        
    except Exception as e:
        print(f"✗ Error: {e}")
        return False
    finally:
        session.close()

def test_worker_session():
    """Test that the linkcheck worker has a session object."""
    print("Testing linkcheck worker Session object...")
    
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
        
        # Check that the worker has a session
        if not hasattr(worker, 'session'):
            print("✗ Worker does not have a session attribute")
            return False
            
        if not isinstance(worker.session, requests.Session):
            print("✗ Worker session is not a requests.Session object")
            return False
        
        print("✓ Worker has a Session object!")
        
        # Clean up
        worker.session.close()
        return True
        
    except Exception as e:
        print(f"✗ Error: {e}")
        return False

def main():
    print("Verifying Session functionality in linkcheck...")
    print("=" * 50)
    
    success = True
    
    if not test_session_parameter():
        success = False
    
    print()
    
    if not test_worker_session():
        success = False
    
    print()
    
    if success:
        print("✓ All tests passed! Session functionality is working correctly.")
        return 0
    else:
        print("✗ Some tests failed.")
        return 1

if __name__ == '__main__':
    sys.exit(main())
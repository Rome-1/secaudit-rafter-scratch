#!/usr/bin/env python3

"""
Test script to verify CSRF cookie validation behavior.
This tests the specific issue described in the GitHub issue.
"""

import os
import sys
import django
from django.conf import settings
from django.test import SimpleTestCase
from django.http import HttpRequest
from django.middleware.csrf import CsrfViewMiddleware

# Configure Django settings
if not settings.configured:
    settings.configure(
        DEBUG=True,
        SECRET_KEY='test-secret-key',
        CSRF_COOKIE_NAME='csrftoken',
        CSRF_HEADER_NAME='HTTP_X_CSRFTOKEN',
        MIDDLEWARE=[
            'django.middleware.csrf.CsrfViewMiddleware',
        ],
        USE_TZ=True,
    )

django.setup()


class TestingHttpRequest(HttpRequest):
    """Custom HttpRequest for testing."""
    
    def __init__(self):
        super().__init__()
        self.META = {}
        self.method = 'GET'
        
    def is_secure(self):
        return False


def post_form_view(request):
    """Simple view for testing POST requests."""
    from django.http import HttpResponse
    return HttpResponse("OK")


class TestCsrfCookieValidation(SimpleTestCase):
    """Test CSRF cookie validation behavior."""
    
    def test_malformed_cookie_token_rejected_in_process_view(self):
        """
        Test that a malformed CSRF cookie token is rejected in process_view()
        rather than being silently replaced with a new token.
        """
        # Create a POST request with a malformed CSRF cookie (64 chars with invalid chars)
        req = TestingHttpRequest()
        req.method = 'POST'
        req.COOKIES[settings.CSRF_COOKIE_NAME] = 'a' * 63 + '!'  # 64 chars, last one invalid
        req.POST = {'csrfmiddlewaretoken': 'some-token'}
        
        mw = CsrfViewMiddleware(post_form_view)
        
        # process_request should handle the invalid cookie gracefully
        mw.process_request(req)
        
        # process_view should reject the request due to malformed cookie
        with self.assertLogs('django.security.csrf', 'WARNING') as cm:
            resp = mw.process_view(req, post_form_view, (), {})
        
        # Should return a 403 response
        self.assertEqual(resp.status_code, 403)
        
        # Should log the specific reason for rejection
        log_message = cm.records[0].getMessage()
        self.assertIn('CSRF cookie has invalid characters', log_message)
        
    def test_malformed_cookie_token_length_rejected_in_process_view(self):
        """
        Test that a CSRF cookie token with incorrect length is rejected in process_view().
        """
        # Create a POST request with a CSRF cookie of wrong length
        req = TestingHttpRequest()
        req.method = 'POST'
        req.COOKIES[settings.CSRF_COOKIE_NAME] = 'short'  # Too short
        req.POST = {'csrfmiddlewaretoken': 'some-token'}
        
        mw = CsrfViewMiddleware(post_form_view)
        
        # process_request should handle the invalid cookie gracefully
        mw.process_request(req)
        
        # process_view should reject the request due to malformed cookie
        with self.assertLogs('django.security.csrf', 'WARNING') as cm:
            resp = mw.process_view(req, post_form_view, (), {})
        
        # Should return a 403 response
        self.assertEqual(resp.status_code, 403)
        
        # Should log the specific reason for rejection
        log_message = cm.records[0].getMessage()
        self.assertIn('CSRF cookie has incorrect length', log_message)
        
    def test_valid_cookie_token_still_works(self):
        """
        Test that valid CSRF cookie tokens still work correctly.
        """
        # Create a valid CSRF token
        from django.middleware.csrf import _get_new_csrf_token
        valid_token = _get_new_csrf_token()
        
        # Create a POST request with valid CSRF cookie and matching request token
        req = TestingHttpRequest()
        req.method = 'POST'
        req.COOKIES[settings.CSRF_COOKIE_NAME] = valid_token
        req.POST = {'csrfmiddlewaretoken': valid_token}
        
        mw = CsrfViewMiddleware(post_form_view)
        
        # process_request should work fine
        mw.process_request(req)
        
        # process_view should accept the request
        resp = mw.process_view(req, post_form_view, (), {})
        
        # Should return None (meaning request is accepted)
        self.assertIsNone(resp)
        
    def test_get_request_with_malformed_cookie_still_works(self):
        """
        Test that GET requests with malformed cookies still work (they get new tokens).
        """
        # Create a GET request with a malformed CSRF cookie
        req = TestingHttpRequest()
        req.method = 'GET'
        req.COOKIES[settings.CSRF_COOKIE_NAME] = 'invalid-token!'
        
        mw = CsrfViewMiddleware(post_form_view)
        
        # process_request should handle the invalid cookie gracefully
        mw.process_request(req)
        
        # Should have generated a new token
        self.assertIn('CSRF_COOKIE', req.META)
        self.assertNotEqual(req.META['CSRF_COOKIE'], 'invalid-token!')
        
        # process_view should accept GET requests
        resp = mw.process_view(req, post_form_view, (), {})
        self.assertIsNone(resp)


if __name__ == '__main__':
    import unittest
    unittest.main()
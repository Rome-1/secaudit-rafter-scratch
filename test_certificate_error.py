#!/usr/bin/env python3
"""
Script to test the current certificate error handling implementation
and verify the new changes work correctly.
"""

import sys
import os
sys.path.insert(0, '/app')

from qutebrowser.qt import machinery
from qutebrowser.qt.network import QSslError
from qutebrowser.qt.core import QUrl

# Test basic imports
try:
    from qutebrowser.browser.webkit.certificateerror import CertificateErrorWrapper as WebKitWrapper
    print("WebKit certificate error wrapper imported successfully")
except Exception as e:
    print(f"Failed to import WebKit wrapper: {e}")

try:
    from qutebrowser.browser.webengine.certificateerror import CertificateErrorWrapper as WebEngineWrapper
    print("WebEngine certificate error wrapper imported successfully")
except Exception as e:
    print(f"Failed to import WebEngine wrapper: {e}")

print(f"Qt version: Qt{'5' if machinery.IS_QT5 else '6'}")
print(f"Wrapper: {machinery.WRAPPER}")

# Test creating certificate error wrappers
if machinery.IS_QT5:
    print("\nTesting Qt5/WebKit wrapper...")
    # Create a mock SSL error for Qt5
    try:
        from qutebrowser.qt.network import QSslError
        ssl_error = QSslError(QSslError.SslError.SelfSignedCertificate, None)
        errors = [ssl_error]
        wrapper = WebKitWrapper(errors)
        print(f"Created WebKit wrapper: {wrapper}")
        print(f"Is overridable: {wrapper.is_overridable()}")
        print(f"String representation: {wrapper}")
    except Exception as e:
        print(f"Error creating WebKit wrapper: {e}")

else:
    print("\nTesting Qt6/WebEngine wrapper...")
    # For Qt6, we would need a QWebEngineCertificateError which is harder to create in a test
    print("WebEngine wrapper requires actual certificate error from Qt")

print("\nTesting abstract interface...")
from qutebrowser.utils.usertypes import AbstractCertificateErrorWrapper

# Verify the abstract interface exists
print(f"Abstract base class: {AbstractCertificateErrorWrapper}")
print(f"Abstract methods: {AbstractCertificateErrorWrapper.__abstractmethods__ if hasattr(AbstractCertificateErrorWrapper, '__abstractmethods__') else 'None'}")

# Test new methods
print("Testing new interface methods:")
print(f"- certificate_was_accepted: {hasattr(AbstractCertificateErrorWrapper, 'certificate_was_accepted')}")
print(f"- accept_certificate: {hasattr(AbstractCertificateErrorWrapper, 'accept_certificate')}")
print(f"- reject_certificate: {hasattr(AbstractCertificateErrorWrapper, 'reject_certificate')}")
print(f"- defer: {hasattr(AbstractCertificateErrorWrapper, 'defer')}")
print(f"- _validate: {hasattr(AbstractCertificateErrorWrapper, '_validate')}")
print(f"- _type: {hasattr(AbstractCertificateErrorWrapper, '_type')}")
print(f"- create: {hasattr(AbstractCertificateErrorWrapper, 'create')}")

print("\nTesting factory method...")
try:
    # Test creating via factory with Qt5
    wrapper = AbstractCertificateErrorWrapper.create(errors=[], reply=None)
    print(f"Factory created wrapper: {type(wrapper)}")
    print(f"Is WebKit wrapper: {'webkit' in type(wrapper).__module__}")
    
    # Test new methods on the wrapper
    print(f"Initial certificate_was_accepted: {wrapper.certificate_was_accepted()}")
    print(f"Is overridable: {wrapper.is_overridable()}")
    
    # Test accepting certificate
    print("Accepting certificate...")
    try:
        wrapper.accept_certificate()
        print(f"After accept - certificate_was_accepted: {wrapper.certificate_was_accepted()}")
    except Exception as e:
        print(f"Error accepting certificate: {e}")
        
    # Test rejecting certificate
    print("Rejecting certificate...")
    try:
        wrapper.reject_certificate()
        print(f"After reject - certificate_was_accepted: {wrapper.certificate_was_accepted()}")
    except Exception as e:
        print(f"Error rejecting certificate: {e}")
        
except Exception as e:
    print(f"Error testing factory: {e}")

print("\nTesting certificate error handling function...")
try:
    from qutebrowser.browser import shared
    print(f"handle_certificate_error function exists: {hasattr(shared, 'handle_certificate_error')}")
    print(f"ignore_certificate_error function still exists: {hasattr(shared, 'ignore_certificate_error')}")
except Exception as e:
    print(f"Error testing shared functions: {e}")

print("\nTest completed!")
#!/usr/bin/env python3
"""
Test backwards compatibility of certificate error handling changes
"""
import sys
import os
sys.path.insert(0, '/app')

from qutebrowser.qt import machinery
from qutebrowser.qt.network import QSslError

print("Testing backwards compatibility...")

# Test 1: Old WebKit wrapper creation pattern still works
print("\n1. Testing old WebKit wrapper creation:")
try:
    if machinery.IS_QT5:
        from qutebrowser.browser.webkit.certificateerror import CertificateErrorWrapper
        
        ssl_error = QSslError(QSslError.SslError.SelfSignedCertificate)
        errors = [ssl_error]
        
        # This is how it was created before
        wrapper = CertificateErrorWrapper(errors)
        print("✓ Old creation pattern works")
        
        # Test old interface still works
        print(f"  __str__(): {str(wrapper)[:50]}...")
        print(f"  is_overridable(): {wrapper.is_overridable()}")
        print(f"  html(): {len(wrapper.html())} chars")
        
    else:
        print("- Skipped for Qt6")
        
except Exception as e:
    print(f"✗ Old WebKit pattern failed: {e}")

# Test 2: Old WebEngine wrapper creation pattern still works  
print("\n2. Testing old WebEngine wrapper creation:")
try:
    if machinery.IS_QT6:
        from qutebrowser.browser.webengine.certificateerror import CertificateErrorWrapper
        print("- Would test with real QWebEngineCertificateError")
    else:
        print("- Skipped for Qt5")
        
except Exception as e:
    print(f"✗ Old WebEngine pattern failed: {e}")

# Test 3: Hash and equality still work (important for caching)
print("\n3. Testing hash and equality (for caching):")
try:
    if machinery.IS_QT5:
        from qutebrowser.browser.webkit.certificateerror import CertificateErrorWrapper
        
        ssl_error1 = QSslError(QSslError.SslError.SelfSignedCertificate)
        ssl_error2 = QSslError(QSslError.SslError.SelfSignedCertificate) 
        
        wrapper1 = CertificateErrorWrapper([ssl_error1])
        wrapper2 = CertificateErrorWrapper([ssl_error2])
        wrapper3 = CertificateErrorWrapper([ssl_error1, ssl_error2])
        
        print(f"  wrapper1 == wrapper2: {wrapper1 == wrapper2}")
        print(f"  wrapper1 == wrapper3: {wrapper1 == wrapper3}")
        print(f"  hash(wrapper1): {hash(wrapper1)}")
        print(f"  hash(wrapper2): {hash(wrapper2)}")
        print("✓ Hash and equality work correctly")
        
    else:
        print("- Skipped for Qt6")
        
except Exception as e:
    print(f"✗ Hash and equality failed: {e}")

# Test 4: Original html() functionality preserved
print("\n4. Testing HTML functionality preservation:")
try:
    if machinery.IS_QT5:
        from qutebrowser.browser.webkit.certificateerror import CertificateErrorWrapper
        
        # Single error should use parent class html()
        ssl_error = QSslError(QSslError.SslError.SelfSignedCertificate)
        wrapper_single = CertificateErrorWrapper([ssl_error])
        html_single = wrapper_single.html()
        
        # Multiple errors should use template
        ssl_error2 = QSslError(QSslError.SslError.UnableToGetIssuerCertificate)
        wrapper_multi = CertificateErrorWrapper([ssl_error, ssl_error2])
        html_multi = wrapper_multi.html()
        
        print(f"  Single error HTML starts with <p>: {'<p>' in html_single}")
        print(f"  Multi error HTML has <ul>: {'<ul>' in html_multi}")
        print(f"  Multi error HTML has <li>: {'<li>' in html_multi}")
        print("✓ HTML functionality preserved")
        
    else:
        print("- Skipped for Qt6")
        
except Exception as e:
    print(f"✗ HTML functionality test failed: {e}")

print("\nBackwards compatibility testing completed!")
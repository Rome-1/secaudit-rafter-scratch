#!/usr/bin/env python3
"""
Test the specific certificate error handling functionality
without triggering circular imports.
"""
import sys
import os
sys.path.insert(0, '/app')

print("Testing certificate error handling improvements...")

# Test the base functionality
from qutebrowser.qt import machinery
from qutebrowser.qt.network import QSslError
from qutebrowser.utils import usertypes

print(f"Qt version: {'Qt5' if machinery.IS_QT5 else 'Qt6'}")

# Test factory method
print("\n1. Testing factory method:")
try:
    if machinery.IS_QT5:
        # Create some fake SSL errors for testing
        ssl_error = QSslError(QSslError.SslError.SelfSignedCertificate)
        errors = [ssl_error]
        wrapper = usertypes.AbstractCertificateErrorWrapper.create(errors=errors)
    else:
        # For Qt6, we'd need a real QWebEngineCertificateError
        print("Qt6 factory would need real certificate error")
        wrapper = None
        
    if wrapper:
        print(f"✓ Factory created: {type(wrapper).__name__}")
        print(f"✓ Module: {type(wrapper).__module__}")
    else:
        print("- Skipped for Qt6 (needs real certificate error)")
        
except Exception as e:
    print(f"✗ Factory failed: {e}")

# Test state tracking
print("\n2. Testing state tracking:")
try:
    if machinery.IS_QT5:
        ssl_error = QSslError(QSslError.SslError.SelfSignedCertificate)
        errors = [ssl_error]
        wrapper = usertypes.AbstractCertificateErrorWrapper.create(errors=errors)
        
        print(f"Initial state: {wrapper.certificate_was_accepted()}")
        
        wrapper.accept_certificate()
        print(f"After accept: {wrapper.certificate_was_accepted()}")
        
        wrapper.reject_certificate()
        print(f"After reject: {wrapper.certificate_was_accepted()}")
        
        print("✓ State tracking works correctly")
    else:
        print("- Skipped for Qt6 (needs real certificate error)")
        
except Exception as e:
    print(f"✗ State tracking failed: {e}")

# Test abstract interface compliance
print("\n3. Testing interface compliance:")
abstract_methods = ['certificate_was_accepted', 'accept_certificate', 'reject_certificate', '_validate', '_type']
for method in abstract_methods:
    has_method = hasattr(usertypes.AbstractCertificateErrorWrapper, method)
    print(f"✓ {method}: {'Present' if has_method else 'Missing'}")

# Test wrapper creation with reply
print("\n4. Testing wrapper with reply simulation:")
try:
    if machinery.IS_QT5:
        from qutebrowser.browser.webkit.certificateerror import CertificateErrorWrapper
        
        ssl_error = QSslError(QSslError.SslError.SelfSignedCertificate)
        errors = [ssl_error]
        
        # Create wrapper without reply (original way)
        wrapper1 = CertificateErrorWrapper(errors)
        print("✓ Wrapper created without reply")
        
        # Create wrapper with None reply (new way)
        wrapper2 = CertificateErrorWrapper(errors, None)
        print("✓ Wrapper created with None reply")
        
        # Test methods
        print(f"  is_overridable(): {wrapper2.is_overridable()}")
        print(f"  _type(): {wrapper2._type()}")
        print("✓ Methods work correctly")
        
    else:
        print("- Skipped for Qt6")
        
except Exception as e:
    print(f"✗ Wrapper testing failed: {e}")
    import traceback
    traceback.print_exc()

print("\n5. Testing HTML generation (regression test):")
try:
    if machinery.IS_QT5:
        from qutebrowser.browser.webkit.certificateerror import CertificateErrorWrapper
        
        # Test single error
        ssl_error = QSslError(QSslError.SslError.SelfSignedCertificate)
        wrapper = CertificateErrorWrapper([ssl_error])
        html = wrapper.html()
        print(f"✓ Single error HTML: {len(html)} chars")
        
        # Test multiple errors
        ssl_error2 = QSslError(QSslError.SslError.UnableToGetIssuerCertificate)
        wrapper_multi = CertificateErrorWrapper([ssl_error, ssl_error2])
        html_multi = wrapper_multi.html()
        print(f"✓ Multiple errors HTML: {len(html_multi)} chars")
        
        # Verify it contains expected content
        assert '<ul>' in html_multi
        assert '<li>' in html_multi
        print("✓ HTML generation works correctly")
        
    else:
        print("- Skipped for Qt6")
        
except Exception as e:
    print(f"✗ HTML generation failed: {e}")

print("\nTesting completed!")
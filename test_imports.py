#!/usr/bin/env python3
"""
Test basic imports to make sure there are no circular import issues
"""
import sys
import os
sys.path.insert(0, '/app')

print("Testing basic imports...")

try:
    from qutebrowser.qt import machinery
    print(f"✓ Qt machinery: {machinery.WRAPPER}")
except Exception as e:
    print(f"✗ Qt machinery failed: {e}")
    sys.exit(1)

try:
    from qutebrowser.utils import usertypes
    print("✓ usertypes imported")
except Exception as e:
    print(f"✗ usertypes failed: {e}")
    sys.exit(1)

try:
    from qutebrowser.browser.webkit.certificateerror import CertificateErrorWrapper as WebKitWrapper
    print("✓ WebKit certificate wrapper imported")
except Exception as e:
    print(f"✗ WebKit wrapper failed: {e}")

try:
    from qutebrowser.browser.webengine.certificateerror import CertificateErrorWrapper as WebEngineWrapper
    print("✓ WebEngine certificate wrapper imported")
except Exception as e:
    print(f"✗ WebEngine wrapper failed: {e}")

try:
    from qutebrowser.utils.message import confirm_async
    print("✓ confirm_async imported")
except Exception as e:
    print(f"✗ confirm_async failed: {e}")

print("\nTesting factory method creation...")
try:
    wrapper = usertypes.AbstractCertificateErrorWrapper.create(errors=[], reply=None)
    print(f"✓ Factory created: {type(wrapper).__name__}")
    
    # Test state tracking
    print(f"  Initial state: accepted={wrapper.certificate_was_accepted()}")
    wrapper.accept_certificate()
    print(f"  After accept: accepted={wrapper.certificate_was_accepted()}")
    wrapper.reject_certificate() 
    print(f"  After reject: accepted={wrapper.certificate_was_accepted()}")
    
except Exception as e:
    print(f"✗ Factory test failed: {e}")
    import traceback
    traceback.print_exc()

print("\nAll basic tests completed!")
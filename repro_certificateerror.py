from qutebrowser.browser.webkit.certificateerror import CertificateErrorWrapper

class FakeError:
    def __init__(self, msg):
        self._msg = msg
    def errorString(self):
        return self._msg

# Should accept a named reply kwarg without using it
wrapper_single = CertificateErrorWrapper(errors=[FakeError('Escaping test: <>')], reply=object())
print('SINGLE:\n', wrapper_single.html())

wrapper_multi = CertificateErrorWrapper(errors=[FakeError('Err1 <>'), FakeError('Err2 <>')], reply=None)
print('MULTI:\n', wrapper_multi.html())

# vim: ft=python fileencoding=utf-8 sts=4 sw=4 et:

# Copyright 2016-2021 Florian Bruhin (The Compiler) <mail@qutebrowser.org>
#
# This file is part of qutebrowser.
#
# qutebrowser is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# qutebrowser is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with qutebrowser.  If not, see <https://www.gnu.org/licenses/>.

"""Wrapper over a QWebEngineCertificateError."""

from qutebrowser.qt.core import QUrl
from qutebrowser.qt.webenginecore import QWebEngineCertificateError
from qutebrowser.qt import machinery

from qutebrowser.utils import usertypes, utils, debug


class CertificateErrorWrapper(usertypes.AbstractCertificateErrorWrapper):

    """A wrapper over a QWebEngineCertificateError."""

    def __init__(self, error: QWebEngineCertificateError) -> None:
        super().__init__()
        self._error = error
        self.ignore = False

    def __str__(self) -> str:
        return self._error.errorDescription()

    def __repr__(self) -> str:
        return utils.get_repr(
            self,
            error=debug.qenum_key(QWebEngineCertificateError, self._error.error()),
            string=str(self))

    def url(self) -> QUrl:
        return self._error.url()

    def is_overridable(self) -> bool:
        return self._error.isOverridable()

    def _validate(self) -> None:
        """Validate the certificate decision by setting ignore flag if accepted."""
        self.ignore = self._accepted is True

    def _type(self) -> str:
        """Get the error type description."""
        return debug.qenum_key(QWebEngineCertificateError, self._error.error())

    def accept_certificate(self) -> None:
        """Accept the certificate error."""
        super().accept_certificate()

    def reject_certificate(self) -> None:
        """Reject the certificate error."""
        super().reject_certificate()

    def defer(self) -> None:
        """Defer the certificate decision (supported in Qt6/WebEngine)."""
        # WebEngine supports deferral - we just don't set the ignore flag yet
        pass

    @classmethod 
    def create(cls, errors=None, reply=None, error=None):
        """Factory method to create appropriate wrapper based on Qt version."""
        if machinery.IS_QT6:
            # For Qt6/WebEngine, we use QWebEngineCertificateError
            if error is not None:
                return cls(error)
            else:
                raise ValueError("Qt6 requires a QWebEngineCertificateError")
        else:
            # For Qt5/WebKit, we would use the WebKit wrapper
            from qutebrowser.browser.webkit.certificateerror import CertificateErrorWrapper as WebKitWrapper
            if errors is None:
                errors = []
            return WebKitWrapper(errors, reply)

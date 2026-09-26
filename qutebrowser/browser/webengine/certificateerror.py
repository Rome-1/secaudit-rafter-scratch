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

"""Wrapper over a QWebEngineCertificateError.

This module provides a base CertificateErrorWrapper as well as Qt-version
specific wrappers and a small factory to construct the correct wrapper.
"""

from qutebrowser.qt.core import QUrl
from qutebrowser.qt.webenginecore import QWebEngineCertificateError
from qutebrowser.qt import machinery

from qutebrowser.utils import usertypes, utils, debug


class CertificateErrorWrapper(usertypes.AbstractCertificateErrorWrapper):

    """A wrapper over a QWebEngineCertificateError.

    This class stores the Qt error object and provides Qt5/Qt6 specific
    behavior via dedicated subclasses created by the factory below.
    """

    def __init__(self, error: QWebEngineCertificateError) -> None:
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


class CertificateErrorWrapperQt5(CertificateErrorWrapper):

    """Qt5-specific certificate error wrapper.

    Qt5 exposes acceptCertificate/rejectCertificate on the error object.
    """

    def accept_certificate(self) -> None:  # type: ignore[override]
        super().accept_certificate()
        try:
            self._error.acceptCertificate()
        except Exception:
            # Fall back silently if not available (e.g. when running with Qt6)
            pass

    def reject_certificate(self) -> None:  # type: ignore[override]
        super().reject_certificate()
        try:
            self._error.rejectCertificate()
        except Exception:
            pass

    def defer(self) -> None:  # type: ignore[override]
        # Qt5 supports deferring the decision
        try:
            self._error.defer()
        except Exception as e:
            raise usertypes.UndeferrableError(str(e))


class CertificateErrorWrapperQt6(CertificateErrorWrapper):

    """Qt6-specific certificate error wrapper.

    Qt6 doesn't provide deferral in the same way and we rely on return value
    of certificateError; expose the same API for consistency.
    """

    def accept_certificate(self) -> None:  # type: ignore[override]
        super().accept_certificate()
        # Qt6 doesn't expose accept/reject on the error object in PyQt in the
        # same way; we only track the state locally.

    def reject_certificate(self) -> None:  # type: ignore[override]
        super().reject_certificate()

    def defer(self) -> None:  # type: ignore[override]
        raise usertypes.UndeferrableError(
            "Deferring certificate errors is not supported with Qt6")


def create(error: QWebEngineCertificateError) -> CertificateErrorWrapper:
    """Create a certificate error wrapper suitable for the current Qt.

    Args:
        error: The QWebEngineCertificateError instance from Qt.

    Returns:
        A CertificateErrorWrapper subclass appropriate for the Qt version.
    """
    if machinery.IS_QT5:
        return CertificateErrorWrapperQt5(error)
    else:
        return CertificateErrorWrapperQt6(error)

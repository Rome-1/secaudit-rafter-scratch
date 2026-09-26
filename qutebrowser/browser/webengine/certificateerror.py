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


class CertificateErrorWrapperQt5(CertificateErrorWrapper):
    """Qt5-specific certificate error wrapper."""

    def defer(self) -> None:
        """Defer the certificate decision.
        
        Raises:
            UndeferrableError: Qt5 does not support deferring certificate decisions.
        """
        raise usertypes.UndeferrableError("Qt5 does not support deferring certificate decisions")


class CertificateErrorWrapperQt6(CertificateErrorWrapper):
    """Qt6-specific certificate error wrapper."""

    def defer(self) -> None:
        """Defer the certificate decision for Qt6.
        
        In Qt6, we can defer the certificate decision.
        """
        # Qt6 supports deferred certificate decisions
        pass


def create(error: QWebEngineCertificateError) -> CertificateErrorWrapper:
    """Create the appropriate certificate error wrapper based on Qt version.
    
    Args:
        error: The QWebEngineCertificateError to wrap.
        
    Returns:
        CertificateErrorWrapperQt5 or CertificateErrorWrapperQt6 based on Qt version.
    """
    if machinery.IS_QT5:
        return CertificateErrorWrapperQt5(error)
    elif machinery.IS_QT6:
        return CertificateErrorWrapperQt6(error)
    else:
        # Fallback to base class if version cannot be determined
        return CertificateErrorWrapper(error)

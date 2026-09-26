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

from qutebrowser.qt import qt_api
from qutebrowser.qt.core import QUrl
from qutebrowser.qt.webenginecore import QWebEngineCertificateError

from qutebrowser.utils import usertypes, utils, debug


class Qt5CertificateErrorWrapper(usertypes.AbstractCertificateErrorWrapper):

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
            error=debug.qenum_key(QWebEngineCertificateError,
                                  self._error.error()),
            string=str(self))

    def _type(self):
        return (self._error.error(), self.url().host(), self.url().port())

    def url(self) -> QUrl:
        return self._error.url()

    def is_overridable(self) -> bool:
        return self._error.isOverridable()

    def is_deferrable(self) -> bool:
        # Deferring was added in Qt 5.11
        return qt_api.QT_VERSION_TUPLE >= (5, 11)

    def accept_certificate(self):
        super().accept_certificate()
        self.ignore = True

    def reject_certificate(self):
        super().reject_certificate()
        self.ignore = False


class Qt6CertificateErrorWrapper(usertypes.AbstractCertificateErrorWrapper):
    def __init__(self, error):
        super().__init__()
        self._error = error

    def __str__(self):
        return self._error.errorDescription()

    def __repr__(self) -> str:
        return utils.get_repr(
            self,
            error=debug.qenum_key(QWebEngineCertificateError,
                                  self._error.error()),
            string=str(self))

    def _type(self):
        return (self._error.error(), self.url().host(), self.url().port())

    def url(self) -> QUrl:
        return self._error.url()

    def is_overridable(self) -> bool:
        return self._error.isOverridable()

    def is_deferrable(self) -> bool:
        return True

    def accept_certificate(self):
        super().accept_certificate()
        self._error.acceptCertificate()

    def reject_certificate(self):
        super().reject_certificate()
        self._error.rejectCertificate()


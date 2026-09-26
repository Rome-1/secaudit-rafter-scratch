# vim: ft=python fileencoding=utf-8 sts=4 sw=4 et:

# Copyright 2023 The qutebrowser Authors
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

"""Unified handling for certificate errors."""
from qutebrowser.browser import JSEvalResult, javascript
from qutebrowser.utils import message, usertypes
from qutebrowser.config import config


def handle_certificate_error(err_wrapper: usertypes.AbstractCertificateErrorWrapper):
    """Handle a certificate error.
    Args:
        err_wrapper: The wrapper for the certificate error.
    """
    if not err_wrapper.is_overridable():
        message.error("Unoverridable certificate error for {}: {}".format(
            err_wrapper.url().toDisplayString(), err_wrapper))
        err_wrapper.reject_certificate()
        return

    # Check if we already have a decision for this certificate
    if err_wrapper._type() in javascript.get_known_hosts_manager()._accepted_certs:
        err_wrapper.accept_certificate()
        return
    if err_wrapper._type() in javascript.get_known_hosts_manager()._rejected_certs:
        err_wrapper.reject_certificate()
        return

    # Deferrable errors get a non-blocking prompt
    if err_wrapper.is_deferrable():
        def cb(ok):
            if ok:
                err_wrapper.accept_certificate()
                javascript.get_known_hosts_manager()._accepted_certs.add(
                    err_wrapper._type())
            else:
                err_wrapper.reject_certificate()
                javascript.get_known_hosts_manager()._rejected_certs.add(
                    err_wrapper._type())
        message.confirm_async(
            "Accept certificate for {}?".format(
                err_wrapper.url().toDisplayString()),
            cb,
            html=err_wrapper.html()
        )
        return

    # Non-deferrable errors get a blocking prompt
    question = usertypes.Question()
    question.mode = usertypes.PromptMode.yesno
    question.title = "Certificate error"
    question.html = "Certificate error for <b>{}</b>:<br/>{}".format(
        err_wrapper.url().toDisplayString(), err_wrapper.html())
    question.load_url = err_wrapper.url()

    def _on_answered(answer):
        if answer:
            err_wrapper.accept_certificate()
            javascript.get_known_hosts_manager()._accepted_certs.add(
                err_wrapper._type())
        else:
            err_wrapper.reject_certificate()
            javascript.get_known_hosts_manager()._rejected_certs.add(
                err_wrapper._type())

    question.answered.connect(_on_answered)
    config.instance.prompt_raise(question)

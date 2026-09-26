#!/usr/bin/env python
"""
Test script to verify that autocomplete attributes appear in the rendered HTML output.
"""
import os
import sys
import django
from django.conf import settings

# Configure Django settings
if not settings.configured:
    settings.configure(
        DEBUG=True,
        DATABASES={
            'default': {
                'ENGINE': 'django.db.backends.sqlite3',
                'NAME': ':memory:',
            }
        },
        INSTALLED_APPS=[
            'django.contrib.auth',
            'django.contrib.contenttypes',
        ],
        SECRET_KEY='test-secret-key',
        USE_TZ=True,
    )

django.setup()

from django.contrib.auth.forms import (
    UserCreationForm, AuthenticationForm, PasswordResetForm,
    SetPasswordForm, PasswordChangeForm, AdminPasswordChangeForm
)
from django.contrib.auth.models import User


def test_html_output():
    """Test that autocomplete attributes appear in rendered HTML"""
    print("Testing HTML output for autocomplete attributes...")
    print("=" * 60)
    
    # Test UserCreationForm
    form = UserCreationForm()
    html = str(form)
    print("UserCreationForm HTML contains:")
    if 'autocomplete="username"' in html:
        print("  - autocomplete=\"username\" for username field")
    if 'autocomplete="new-password"' in html:
        print("  - autocomplete=\"new-password\" for password fields")
    
    # Test AuthenticationForm
    form = AuthenticationForm()
    html = str(form)
    print("\nAuthenticationForm HTML contains:")
    if 'autocomplete="username"' in html:
        print("  - autocomplete=\"username\" for username field")
    if 'autocomplete="current-password"' in html:
        print("  - autocomplete=\"current-password\" for password field")
    
    # Test PasswordResetForm
    form = PasswordResetForm()
    html = str(form)
    print("\nPasswordResetForm HTML contains:")
    if 'autocomplete="email"' in html:
        print("  - autocomplete=\"email\" for email field")
    
    # Test SetPasswordForm
    user = User(username='testuser')
    form = SetPasswordForm(user)
    html = str(form)
    print("\nSetPasswordForm HTML contains:")
    if 'autocomplete="new-password"' in html:
        print("  - autocomplete=\"new-password\" for password fields")
    
    # Test PasswordChangeForm
    form = PasswordChangeForm(user)
    html = str(form)
    print("\nPasswordChangeForm HTML contains:")
    if 'autocomplete="current-password"' in html:
        print("  - autocomplete=\"current-password\" for old password field")
    if 'autocomplete="new-password"' in html:
        print("  - autocomplete=\"new-password\" for new password fields")
    
    # Test AdminPasswordChangeForm
    form = AdminPasswordChangeForm(user)
    html = str(form)
    print("\nAdminPasswordChangeForm HTML contains:")
    if 'autocomplete="new-password"' in html:
        print("  - autocomplete=\"new-password\" for password fields")
    
    print("\n" + "=" * 60)
    print("HTML output test completed!")


if __name__ == '__main__':
    test_html_output()
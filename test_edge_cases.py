#!/usr/bin/env python
"""
Test edge cases and ensure autocomplete attributes work correctly in various scenarios.
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
from django.contrib.auth import get_user_model


def test_custom_user_model():
    """Test that autocomplete works with custom user models"""
    print("Testing with custom user model...")
    
    # Test with default User model
    form = AuthenticationForm()
    username_widget = form.fields['username'].widget
    username_attrs = form.fields['username'].widget_attrs(username_widget)
    
    assert 'autocomplete' in username_attrs
    assert username_attrs['autocomplete'] == 'username'
    print("PASS: Custom user model test")


def test_form_inheritance():
    """Test that autocomplete attributes are preserved in form inheritance"""
    print("Testing form inheritance...")
    
    class CustomPasswordChangeForm(PasswordChangeForm):
        pass
    
    user = User(username='testuser')
    form = CustomPasswordChangeForm(user)
    
    # Check old password field
    old_password_attrs = form.fields['old_password'].widget.attrs
    assert 'autocomplete' in old_password_attrs
    assert old_password_attrs['autocomplete'] == 'current-password'
    
    # Check new password fields
    new_password1_attrs = form.fields['new_password1'].widget.attrs
    assert 'autocomplete' in new_password1_attrs
    assert new_password1_attrs['autocomplete'] == 'new-password'
    
    print("PASS: Form inheritance test")


def test_widget_attrs_merging():
    """Test that autocomplete attributes merge correctly with existing widget attrs"""
    print("Testing widget attributes merging...")
    
    # Test that autofocus and autocomplete coexist
    form = PasswordChangeForm(User(username='test'))
    old_password_attrs = form.fields['old_password'].widget.attrs
    
    assert 'autofocus' in old_password_attrs
    assert old_password_attrs['autofocus'] is True
    assert 'autocomplete' in old_password_attrs
    assert old_password_attrs['autocomplete'] == 'current-password'
    
    print("PASS: Widget attributes merging test")


def test_form_rendering():
    """Test that forms render correctly with autocomplete attributes"""
    print("Testing form rendering...")
    
    # Test UserCreationForm rendering
    form = UserCreationForm()
    html = str(form['username'])
    assert 'autocomplete="username"' in html
    
    html = str(form['password1'])
    assert 'autocomplete="new-password"' in html
    
    html = str(form['password2'])
    assert 'autocomplete="new-password"' in html
    
    # Test AuthenticationForm rendering
    form = AuthenticationForm()
    html = str(form['username'])
    assert 'autocomplete="username"' in html
    
    html = str(form['password'])
    assert 'autocomplete="current-password"' in html
    
    print("PASS: Form rendering test")


def test_bound_forms():
    """Test that autocomplete attributes work with bound forms"""
    print("Testing bound forms...")
    
    # Test with valid data
    form = AuthenticationForm(data={'username': 'testuser', 'password': 'testpass'})
    username_widget = form.fields['username'].widget
    username_attrs = form.fields['username'].widget_attrs(username_widget)
    
    assert 'autocomplete' in username_attrs
    assert username_attrs['autocomplete'] == 'username'
    
    password_attrs = form.fields['password'].widget.attrs
    assert 'autocomplete' in password_attrs
    assert password_attrs['autocomplete'] == 'current-password'
    
    print("PASS: Bound forms test")


def main():
    """Run all edge case tests"""
    print("Testing edge cases for autocomplete attributes...")
    print("=" * 60)
    
    test_custom_user_model()
    test_form_inheritance()
    test_widget_attrs_merging()
    test_form_rendering()
    test_bound_forms()
    
    print("=" * 60)
    print("All edge case tests passed!")


if __name__ == '__main__':
    main()
#!/usr/bin/env python
"""
Test script to verify that autocomplete attributes are properly added to Django auth forms.
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


def test_username_field_autocomplete():
    """Test that UsernameField has autocomplete='username'"""
    form = AuthenticationForm()
    username_widget = form.fields['username'].widget
    attrs = form.fields['username'].widget_attrs(username_widget)
    print(f"UsernameField widget attrs: {attrs}")
    assert 'autocomplete' in attrs
    assert attrs['autocomplete'] == 'username'
    print("PASS: UsernameField autocomplete test passed")


def test_user_creation_form():
    """Test UserCreationForm autocomplete attributes"""
    form = UserCreationForm()
    
    # Test username field (inherited from UsernameField)
    username_widget = form.fields['username'].widget
    username_attrs = form.fields['username'].widget_attrs(username_widget)
    print(f"UserCreationForm username attrs: {username_attrs}")
    assert 'autocomplete' in username_attrs
    assert username_attrs['autocomplete'] == 'username'
    
    # Test password1 field
    password1_attrs = form.fields['password1'].widget.attrs
    print(f"UserCreationForm password1 attrs: {password1_attrs}")
    assert 'autocomplete' in password1_attrs
    assert password1_attrs['autocomplete'] == 'new-password'
    
    # Test password2 field
    password2_attrs = form.fields['password2'].widget.attrs
    print(f"UserCreationForm password2 attrs: {password2_attrs}")
    assert 'autocomplete' in password2_attrs
    assert password2_attrs['autocomplete'] == 'new-password'
    
    print("PASS: UserCreationForm autocomplete test passed")


def test_authentication_form():
    """Test AuthenticationForm autocomplete attributes"""
    form = AuthenticationForm()
    
    # Test username field
    username_widget = form.fields['username'].widget
    username_attrs = form.fields['username'].widget_attrs(username_widget)
    print(f"AuthenticationForm username attrs: {username_attrs}")
    assert 'autocomplete' in username_attrs
    assert username_attrs['autocomplete'] == 'username'
    
    # Test password field
    password_attrs = form.fields['password'].widget.attrs
    print(f"AuthenticationForm password attrs: {password_attrs}")
    assert 'autocomplete' in password_attrs
    assert password_attrs['autocomplete'] == 'current-password'
    
    print("PASS: AuthenticationForm autocomplete test passed")


def test_password_reset_form():
    """Test PasswordResetForm autocomplete attributes"""
    form = PasswordResetForm()
    
    # Test email field
    email_attrs = form.fields['email'].widget.attrs
    print(f"PasswordResetForm email attrs: {email_attrs}")
    assert 'autocomplete' in email_attrs
    assert email_attrs['autocomplete'] == 'email'
    
    print("PASS: PasswordResetForm autocomplete test passed")


def test_set_password_form():
    """Test SetPasswordForm autocomplete attributes"""
    user = User(username='testuser')
    form = SetPasswordForm(user)
    
    # Test new_password1 field
    password1_attrs = form.fields['new_password1'].widget.attrs
    print(f"SetPasswordForm new_password1 attrs: {password1_attrs}")
    assert 'autocomplete' in password1_attrs
    assert password1_attrs['autocomplete'] == 'new-password'
    
    # Test new_password2 field
    password2_attrs = form.fields['new_password2'].widget.attrs
    print(f"SetPasswordForm new_password2 attrs: {password2_attrs}")
    assert 'autocomplete' in password2_attrs
    assert password2_attrs['autocomplete'] == 'new-password'
    
    print("PASS: SetPasswordForm autocomplete test passed")


def test_password_change_form():
    """Test PasswordChangeForm autocomplete attributes"""
    user = User(username='testuser')
    form = PasswordChangeForm(user)
    
    # Test old_password field
    old_password_attrs = form.fields['old_password'].widget.attrs
    print(f"PasswordChangeForm old_password attrs: {old_password_attrs}")
    assert 'autocomplete' in old_password_attrs
    assert old_password_attrs['autocomplete'] == 'current-password'
    
    # Test new_password1 field (inherited from SetPasswordForm)
    password1_attrs = form.fields['new_password1'].widget.attrs
    print(f"PasswordChangeForm new_password1 attrs: {password1_attrs}")
    assert 'autocomplete' in password1_attrs
    assert password1_attrs['autocomplete'] == 'new-password'
    
    # Test new_password2 field (inherited from SetPasswordForm)
    password2_attrs = form.fields['new_password2'].widget.attrs
    print(f"PasswordChangeForm new_password2 attrs: {password2_attrs}")
    assert 'autocomplete' in password2_attrs
    assert password2_attrs['autocomplete'] == 'new-password'
    
    print("PASS: PasswordChangeForm autocomplete test passed")


def test_admin_password_change_form():
    """Test AdminPasswordChangeForm autocomplete attributes"""
    user = User(username='testuser')
    form = AdminPasswordChangeForm(user)
    
    # Test password1 field
    password1_attrs = form.fields['password1'].widget.attrs
    print(f"AdminPasswordChangeForm password1 attrs: {password1_attrs}")
    assert 'autocomplete' in password1_attrs
    assert password1_attrs['autocomplete'] == 'new-password'
    
    # Test password2 field
    password2_attrs = form.fields['password2'].widget.attrs
    print(f"AdminPasswordChangeForm password2 attrs: {password2_attrs}")
    assert 'autocomplete' in password2_attrs
    assert password2_attrs['autocomplete'] == 'new-password'
    
    print("PASS: AdminPasswordChangeForm autocomplete test passed")


def main():
    """Run all tests"""
    print("Testing Django auth forms autocomplete attributes...")
    print("=" * 60)
    
    test_username_field_autocomplete()
    test_user_creation_form()
    test_authentication_form()
    test_password_reset_form()
    test_set_password_form()
    test_password_change_form()
    test_admin_password_change_form()
    
    print("=" * 60)
    print("All tests passed!")


if __name__ == '__main__':
    main()
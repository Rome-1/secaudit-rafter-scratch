#!/usr/bin/env python
"""Test script to verify autocomplete attributes in auth forms."""
import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'django.conf.global_settings')
from django.conf import settings
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
            'django.contrib.contenttypes',
            'django.contrib.auth',
        ],
        SECRET_KEY='test-secret-key',
        USE_TZ=True,
    )
    django.setup()

from django.contrib.auth.forms import (
    UsernameField, UserCreationForm, AuthenticationForm,
    PasswordResetForm, SetPasswordForm, PasswordChangeForm,
    AdminPasswordChangeForm
)
from django.contrib.auth.models import User

def test_autocomplete_attributes():
    """Test that autocomplete attributes are present in forms."""
    print("Testing autocomplete attributes in auth forms...\n")
    
    # Test UsernameField
    print("1. Testing UsernameField:")
    field = UsernameField()
    widget = field.widget
    attrs = field.widget_attrs(widget)
    print(f"   widget_attrs: {attrs}")
    print(f"   Has autocomplete='username': {'autocomplete' in attrs and attrs['autocomplete'] == 'username'}")
    
    # Test UserCreationForm
    print("\n2. Testing UserCreationForm:")
    form = UserCreationForm()
    password1_attrs = form.fields['password1'].widget.attrs
    password2_attrs = form.fields['password2'].widget.attrs
    print(f"   password1 attrs: {password1_attrs}")
    print(f"   password2 attrs: {password2_attrs}")
    print(f"   password1 has autocomplete='new-password': {'autocomplete' in password1_attrs and password1_attrs['autocomplete'] == 'new-password'}")
    print(f"   password2 has autocomplete='new-password': {'autocomplete' in password2_attrs and password2_attrs['autocomplete'] == 'new-password'}")
    
    # Test AuthenticationForm
    print("\n3. Testing AuthenticationForm:")
    form = AuthenticationForm()
    username_widget = form.fields['username'].widget
    username_attrs = form.fields['username'].widget_attrs(username_widget)
    password_attrs = form.fields['password'].widget.attrs
    print(f"   username widget_attrs: {username_attrs}")
    print(f"   password attrs: {password_attrs}")
    print(f"   username has autocomplete='username': {'autocomplete' in username_attrs and username_attrs['autocomplete'] == 'username'}")
    print(f"   password has autocomplete='current-password': {'autocomplete' in password_attrs and password_attrs['autocomplete'] == 'current-password'}")
    
    # Test PasswordResetForm
    print("\n4. Testing PasswordResetForm:")
    form = PasswordResetForm()
    email_attrs = form.fields['email'].widget.attrs
    print(f"   email attrs: {email_attrs}")
    print(f"   email has autocomplete='email': {'autocomplete' in email_attrs and email_attrs['autocomplete'] == 'email'}")
    
    # Test SetPasswordForm
    print("\n5. Testing SetPasswordForm:")
    user = User(username='testuser')
    form = SetPasswordForm(user)
    new_password1_attrs = form.fields['new_password1'].widget.attrs
    new_password2_attrs = form.fields['new_password2'].widget.attrs
    print(f"   new_password1 attrs: {new_password1_attrs}")
    print(f"   new_password2 attrs: {new_password2_attrs}")
    print(f"   new_password1 has autocomplete='new-password': {'autocomplete' in new_password1_attrs and new_password1_attrs['autocomplete'] == 'new-password'}")
    print(f"   new_password2 has autocomplete='new-password': {'autocomplete' in new_password2_attrs and new_password2_attrs['autocomplete'] == 'new-password'}")
    
    # Test PasswordChangeForm
    print("\n6. Testing PasswordChangeForm:")
    form = PasswordChangeForm(user)
    old_password_attrs = form.fields['old_password'].widget.attrs
    new_password1_attrs = form.fields['new_password1'].widget.attrs
    new_password2_attrs = form.fields['new_password2'].widget.attrs
    print(f"   old_password attrs: {old_password_attrs}")
    print(f"   new_password1 attrs: {new_password1_attrs}")
    print(f"   new_password2 attrs: {new_password2_attrs}")
    print(f"   old_password has autocomplete='current-password': {'autocomplete' in old_password_attrs and old_password_attrs['autocomplete'] == 'current-password'}")
    print(f"   new_password1 has autocomplete='new-password': {'autocomplete' in new_password1_attrs and new_password1_attrs['autocomplete'] == 'new-password'}")
    print(f"   new_password2 has autocomplete='new-password': {'autocomplete' in new_password2_attrs and new_password2_attrs['autocomplete'] == 'new-password'}")
    
    # Test AdminPasswordChangeForm
    print("\n7. Testing AdminPasswordChangeForm:")
    form = AdminPasswordChangeForm(user)
    password1_attrs = form.fields['password1'].widget.attrs
    password2_attrs = form.fields['password2'].widget.attrs
    print(f"   password1 attrs: {password1_attrs}")
    print(f"   password2 attrs: {password2_attrs}")
    print(f"   password1 has autocomplete='new-password': {'autocomplete' in password1_attrs and password1_attrs['autocomplete'] == 'new-password'}")
    print(f"   password2 has autocomplete='new-password': {'autocomplete' in password2_attrs and password2_attrs['autocomplete'] == 'new-password'}")

if __name__ == '__main__':
    test_autocomplete_attributes()

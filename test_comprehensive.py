#!/usr/bin/env python
"""Comprehensive test of autocomplete attributes."""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'django.conf.global_settings')
from django.conf import settings
if not settings.configured:
    settings.configure(
        DEBUG=True,
        DATABASES={'default': {'ENGINE': 'django.db.backends.sqlite3', 'NAME': ':memory:'}},
        INSTALLED_APPS=['django.contrib.contenttypes', 'django.contrib.auth'],
        SECRET_KEY='test-secret-key',
        USE_TZ=True,
    )
    django.setup()

from django.contrib.auth.forms import (
    UserCreationForm, AuthenticationForm, PasswordResetForm,
    SetPasswordForm, PasswordChangeForm, AdminPasswordChangeForm
)
from django.contrib.auth.models import User

def test_form(form_class, form_name, expected_attrs, *args, **kwargs):
    """Test a form for expected autocomplete attributes."""
    print(f"\nTesting {form_name}:")
    form = form_class(*args, **kwargs)
    html = str(form)
    
    all_found = True
    for field_name, expected_value in expected_attrs.items():
        attr_string = f'autocomplete="{expected_value}"'
        found = attr_string in html
        status = "[PASS]" if found else "[FAIL]"
        print(f"  {status} Field '{field_name}' has {attr_string}: {found}")
        if not found:
            all_found = False
    
    return all_found

# Run tests
print("=" * 60)
print("COMPREHENSIVE AUTOCOMPLETE ATTRIBUTE TESTS")
print("=" * 60)

user = User(username='testuser')
all_tests_passed = True

# Test each form
all_tests_passed &= test_form(
    UserCreationForm, "UserCreationForm",
    {'username': 'username', 'password1': 'new-password', 'password2': 'new-password'}
)

all_tests_passed &= test_form(
    AuthenticationForm, "AuthenticationForm",
    {'username': 'username', 'password': 'current-password'}
)

all_tests_passed &= test_form(
    PasswordResetForm, "PasswordResetForm",
    {'email': 'email'}
)

all_tests_passed &= test_form(
    SetPasswordForm, "SetPasswordForm",
    {'new_password1': 'new-password', 'new_password2': 'new-password'},
    user
)

all_tests_passed &= test_form(
    PasswordChangeForm, "PasswordChangeForm",
    {'old_password': 'current-password', 'new_password1': 'new-password', 'new_password2': 'new-password'},
    user
)

all_tests_passed &= test_form(
    AdminPasswordChangeForm, "AdminPasswordChangeForm",
    {'password1': 'new-password', 'password2': 'new-password'},
    user
)

print("\n" + "=" * 60)
if all_tests_passed:
    print("ALL TESTS PASSED!")
else:
    print("SOME TESTS FAILED!")
print("=" * 60)

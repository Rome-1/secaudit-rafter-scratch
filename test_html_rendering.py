#!/usr/bin/env python
"""Test that autocomplete attributes appear in rendered HTML."""
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
    UserCreationForm, AuthenticationForm,
    PasswordResetForm, SetPasswordForm, PasswordChangeForm,
    AdminPasswordChangeForm
)
from django.contrib.auth.models import User

def test_html_rendering():
    """Test that autocomplete attributes appear in rendered HTML."""
    print("Testing HTML rendering of autocomplete attributes...\n")
    
    # Test UserCreationForm
    print("1. UserCreationForm:")
    form = UserCreationForm()
    html = str(form)
    username_attr = 'autocomplete="username"'
    new_password_attr = 'autocomplete="new-password"'
    print(f"   Contains {username_attr}: {username_attr in html}")
    print(f"   Contains {new_password_attr}: {new_password_attr in html}")
    print(f"   Count of {new_password_attr}: {html.count(new_password_attr)}")
    
    # Test AuthenticationForm
    print("\n2. AuthenticationForm:")
    form = AuthenticationForm()
    html = str(form)
    current_password_attr = 'autocomplete="current-password"'
    print(f"   Contains {username_attr}: {username_attr in html}")
    print(f"   Contains {current_password_attr}: {current_password_attr in html}")
    
    # Test PasswordResetForm
    print("\n3. PasswordResetForm:")
    form = PasswordResetForm()
    html = str(form)
    email_attr = 'autocomplete="email"'
    print(f"   Contains {email_attr}: {email_attr in html}")
    
    # Test SetPasswordForm
    print("\n4. SetPasswordForm:")
    user = User(username='testuser')
    form = SetPasswordForm(user)
    html = str(form)
    print(f"   Contains {new_password_attr}: {new_password_attr in html}")
    print(f"   Count of {new_password_attr}: {html.count(new_password_attr)}")
    
    # Test PasswordChangeForm
    print("\n5. PasswordChangeForm:")
    form = PasswordChangeForm(user)
    html = str(form)
    print(f"   Contains {current_password_attr}: {current_password_attr in html}")
    print(f"   Contains {new_password_attr}: {new_password_attr in html}")
    print(f"   Count of {new_password_attr}: {html.count(new_password_attr)}")
    
    # Test AdminPasswordChangeForm
    print("\n6. AdminPasswordChangeForm:")
    form = AdminPasswordChangeForm(user)
    html = str(form)
    print(f"   Contains {new_password_attr}: {new_password_attr in html}")
    print(f"   Count of {new_password_attr}: {html.count(new_password_attr)}")

if __name__ == '__main__':
    test_html_rendering()

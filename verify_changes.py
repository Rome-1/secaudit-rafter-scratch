#!/usr/bin/env python
"""Verify all changes are correctly applied."""

with open('/testbed/django/contrib/auth/forms.py', 'r') as f:
    content = f.read()

checks = [
    ("UsernameField has autocomplete='username'", "attrs['autocomplete'] = 'username'" in content),
    ("UserCreationForm password1 has autocomplete='new-password'", 
     "widget=forms.PasswordInput(attrs={'autocomplete': 'new-password'})" in content and 
     'label=_("Password")' in content),
    ("UserCreationForm password2 has autocomplete='new-password'", 
     'label=_("Password confirmation")' in content and 
     "widget=forms.PasswordInput(attrs={'autocomplete': 'new-password'})" in content),
    ("AuthenticationForm password has autocomplete='current-password'", 
     "widget=forms.PasswordInput(attrs={'autocomplete': 'current-password'})" in content),
    ("PasswordResetForm email has autocomplete='email'", 
     "widget=forms.EmailInput(attrs={'autocomplete': 'email'})" in content),
    ("SetPasswordForm new_password1 has autocomplete='new-password'", 
     'label=_("New password")' in content and 
     "widget=forms.PasswordInput(attrs={'autocomplete': 'new-password'})" in content),
    ("SetPasswordForm new_password2 has autocomplete='new-password'", 
     'label=_("New password confirmation")' in content and 
     "widget=forms.PasswordInput(attrs={'autocomplete': 'new-password'})" in content),
    ("PasswordChangeForm old_password has autocomplete='current-password'", 
     "widget=forms.PasswordInput(attrs={'autofocus': True, 'autocomplete': 'current-password'})" in content),
    ("AdminPasswordChangeForm password1 has autocomplete='new-password'", 
     "widget=forms.PasswordInput(attrs={'autofocus': True, 'autocomplete': 'new-password'})" in content),
    ("AdminPasswordChangeForm password2 has autocomplete='new-password'", 
     'label=_("Password (again)")' in content and 
     "widget=forms.PasswordInput(attrs={'autocomplete': 'new-password'})" in content),
]

print("Verification of changes:\n")
all_passed = True
for description, check in checks:
    status = "[PASS]" if check else "[FAIL]"
    print(f"{status} {description}")
    if not check:
        all_passed = False

print(f"\n{'All checks passed!' if all_passed else 'Some checks failed!'}")

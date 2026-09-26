#!/usr/bin/env python
"""Apply autocomplete attribute changes to auth forms."""

with open('/testbed/django/contrib/auth/forms.py', 'r') as f:
    content = f.read()

# 1. Update UsernameField.widget_attrs to add autocomplete='username'
old_widget_attrs = """    def widget_attrs(self, widget):
        attrs = super().widget_attrs(widget)
        attrs['autocapitalize'] = 'none'
        return attrs"""

new_widget_attrs = """    def widget_attrs(self, widget):
        attrs = super().widget_attrs(widget)
        attrs['autocapitalize'] = 'none'
        attrs['autocomplete'] = 'username'
        return attrs"""

content = content.replace(old_widget_attrs, new_widget_attrs)

# 2. Update UserCreationForm password fields to add autocomplete='new-password'
old_password1 = """    password1 = forms.CharField(
        label=_("Password"),
        strip=False,
        widget=forms.PasswordInput,
        help_text=password_validation.password_validators_help_text_html(),
    )"""

new_password1 = """    password1 = forms.CharField(
        label=_("Password"),
        strip=False,
        widget=forms.PasswordInput(attrs={'autocomplete': 'new-password'}),
        help_text=password_validation.password_validators_help_text_html(),
    )"""

content = content.replace(old_password1, new_password1)

old_password2 = """    password2 = forms.CharField(
        label=_("Password confirmation"),
        widget=forms.PasswordInput,
        strip=False,
        help_text=_("Enter the same password as before, for verification."),
    )"""

new_password2 = """    password2 = forms.CharField(
        label=_("Password confirmation"),
        widget=forms.PasswordInput(attrs={'autocomplete': 'new-password'}),
        strip=False,
        help_text=_("Enter the same password as before, for verification."),
    )"""

content = content.replace(old_password2, new_password2)

# 3. Update AuthenticationForm password field to add autocomplete='current-password'
old_auth_password = """    password = forms.CharField(
        label=_("Password"),
        strip=False,
        widget=forms.PasswordInput,
    )"""

new_auth_password = """    password = forms.CharField(
        label=_("Password"),
        strip=False,
        widget=forms.PasswordInput(attrs={'autocomplete': 'current-password'}),
    )"""

content = content.replace(old_auth_password, new_auth_password)

# 4. Update PasswordResetForm email field to add autocomplete='email'
old_email = """class PasswordResetForm(forms.Form):
    email = forms.EmailField(label=_("Email"), max_length=254)"""

new_email = """class PasswordResetForm(forms.Form):
    email = forms.EmailField(
        label=_("Email"),
        max_length=254,
        widget=forms.EmailInput(attrs={'autocomplete': 'email'})
    )"""

content = content.replace(old_email, new_email)

# 5. Update SetPasswordForm password fields to add autocomplete='new-password'
old_new_password1 = """    new_password1 = forms.CharField(
        label=_("New password"),
        widget=forms.PasswordInput,
        strip=False,
        help_text=password_validation.password_validators_help_text_html(),
    )"""

new_new_password1 = """    new_password1 = forms.CharField(
        label=_("New password"),
        widget=forms.PasswordInput(attrs={'autocomplete': 'new-password'}),
        strip=False,
        help_text=password_validation.password_validators_help_text_html(),
    )"""

content = content.replace(old_new_password1, new_new_password1)

old_new_password2 = """    new_password2 = forms.CharField(
        label=_("New password confirmation"),
        strip=False,
        widget=forms.PasswordInput,
    )"""

new_new_password2 = """    new_password2 = forms.CharField(
        label=_("New password confirmation"),
        strip=False,
        widget=forms.PasswordInput(attrs={'autocomplete': 'new-password'}),
    )"""

content = content.replace(old_new_password2, new_new_password2)

# 6. Update PasswordChangeForm old_password field to add autocomplete='current-password'
old_old_password = """    old_password = forms.CharField(
        label=_("Old password"),
        strip=False,
        widget=forms.PasswordInput(attrs={'autofocus': True}),
    )"""

new_old_password = """    old_password = forms.CharField(
        label=_("Old password"),
        strip=False,
        widget=forms.PasswordInput(attrs={'autofocus': True, 'autocomplete': 'current-password'}),
    )"""

content = content.replace(old_old_password, new_old_password)

# 7. Update AdminPasswordChangeForm password fields to add autocomplete='new-password'
old_admin_password1 = """    password1 = forms.CharField(
        label=_("Password"),
        widget=forms.PasswordInput(attrs={'autofocus': True}),
        strip=False,
        help_text=password_validation.password_validators_help_text_html(),
    )"""

new_admin_password1 = """    password1 = forms.CharField(
        label=_("Password"),
        widget=forms.PasswordInput(attrs={'autofocus': True, 'autocomplete': 'new-password'}),
        strip=False,
        help_text=password_validation.password_validators_help_text_html(),
    )"""

content = content.replace(old_admin_password1, new_admin_password1)

old_admin_password2 = """    password2 = forms.CharField(
        label=_("Password (again)"),
        widget=forms.PasswordInput,
        strip=False,
        help_text=_("Enter the same password as before, for verification."),
    )"""

new_admin_password2 = """    password2 = forms.CharField(
        label=_("Password (again)"),
        widget=forms.PasswordInput(attrs={'autocomplete': 'new-password'}),
        strip=False,
        help_text=_("Enter the same password as before, for verification."),
    )"""

content = content.replace(old_admin_password2, new_admin_password2)

# Write the updated content
with open('/testbed/django/contrib/auth/forms.py', 'w') as f:
    f.write(content)

print("Changes applied successfully!")

import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'test_settings')

# Create a minimal settings module
with open('test_settings.py', 'w') as f:
    f.write("""
# Set SECRET_KEY to a valid value
DEBUG = True
SECRET_KEY = 'my-secret-key'
""")

# Try to initialize Django settings
from django.conf import settings
print("Settings initialized successfully!")

# Try to access a setting that's not SECRET_KEY
print(f"DEBUG = {settings.DEBUG}")

# Now try to access SECRET_KEY
try:
    print(f"SECRET_KEY = {settings.SECRET_KEY}")
except Exception as e:
    print(f"Error accessing SECRET_KEY: {e}")
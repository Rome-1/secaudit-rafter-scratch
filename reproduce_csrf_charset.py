import django
from django.conf import settings
from django.http import HttpRequest, HttpResponseForbidden
from django.views.csrf import csrf_failure
from django.template import Engine, Template, Context

# Configure minimal Django settings
settings.configure(
    DEBUG=True,
    SECRET_KEY='dummy',
    DEFAULT_CHARSET='iso-8859-1',
    INSTALLED_APPS=[],
    MIDDLEWARE=[]
)

# Initialize Django
django.setup()

# Create a custom template with UTF-8 characters
CUSTOM_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>CSRF Error</title>
</head>
<body>
    <h1>CSRF Error with UTF-8: ñ á é í ó ú</h1>
    <p>Special characters: 漢字 русский عربي</p>
</body>
</html>
"""

def test_csrf_charset():
    # Create a dummy request
    request = HttpRequest()
    
    # Create a custom template
    template = Engine().from_string(CUSTOM_TEMPLATE)
    
    # Get the response from csrf_failure view with default template
    response = csrf_failure(request, reason="Test CSRF failure")
    
    # Create a new response with our custom template to test UTF-8 handling
    custom_response = HttpResponseForbidden(template.render(Context({})), content_type="text/html; charset=utf-8")
    
    print("Default CSRF response Content-Type:", response['Content-Type'])
    print("Custom template response Content-Type:", custom_response['Content-Type'])
    print("\nCustom template response content:")
    print(custom_response.content.decode('utf-8'))

if __name__ == '__main__':
    test_csrf_charset()
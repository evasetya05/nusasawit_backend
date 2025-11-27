"""
WSGI config for HRManagement project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/3.1/howto/deployment/wsgi/
"""

import os
import sys

# Add the project directory to the Python path
project_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if project_path not in sys.path:
    sys.path.append(project_path)

# Set the Django settings module explicitly
os.environ['DJANGO_SETTINGS_MODULE'] = 'config.settings.production'

# Debug output
print("Python version:", sys.version)
print("Python path:", sys.path)
print("DJANGO_SETTINGS_MODULE:", os.environ.get('DJANGO_SETTINGS_MODULE'))

try:
    from django.core.wsgi import get_wsgi_application
    application = get_wsgi_application()
    print("WSGI application loaded successfully")
except Exception as e:
    print("Error loading WSGI application:", str(e))
    raise

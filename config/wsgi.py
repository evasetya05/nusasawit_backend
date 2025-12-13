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

# The DJANGO_SETTINGS_MODULE is set by the Phusion Passenger entry point (passenger_wsgi.py)

from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()

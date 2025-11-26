import os
import sys

# Path ke project Django Anda
PROJECT_HOME = '/home/sdmporta/nusasawit'

# Tambahkan path project ke sys.path
if PROJECT_HOME not in sys.path:
    sys.path.insert(0, PROJECT_HOME)

# Tentukan settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'nusasawit.settings.production')

# Import WSGI Django
from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()

import sys, os

# Tambahkan path project
sys.path.insert(0, '/home/sdmporta/nusasawit')

# Set environment variable ke settings.py yang benar
os.environ['DJANGO_SETTINGS_MODULE'] = 'nusasawit.settings.production'

# Aktifkan virtualenv
activate_this = '/home/sdmporta/virtualenv/nusasawit/3.11/bin/activate_this.py'
with open(activate_this) as file_:
    exec(file_.read(), dict(__file__=activate_this))

# Jalankan WSGI
from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()

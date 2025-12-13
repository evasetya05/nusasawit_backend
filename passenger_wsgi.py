import os
import sys

# Tambahkan path proyek ke sys.path agar Django dapat menemukan modul pengaturan.
# __file__ akan merujuk ke file ini (passenger_wsgi.py),
# dan os.path.dirname(__file__) akan menjadi direktori root proyek Anda.
sys.path.insert(0, os.path.dirname(__file__))

# Atur variabel lingkungan DJANGO_SETTINGS_MODULE untuk menunjuk ke file pengaturan produksi.
# Ini memberitahu Django untuk menggunakan konfigurasi untuk lingkungan produksi.
os.environ['DJANGO_SETTINGS_MODULE'] = 'config.settings.production'

# Impor objek aplikasi WSGI dari file wsgi.py proyek Anda.
# Phusion Passenger akan mencari variabel bernama 'application' secara default.
from config.wsgi import application

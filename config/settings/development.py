from .base import *

DEBUG = True
ALLOWED_HOSTS = []

# Database untuk development (PostgreSQL)
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'nusasawit_db',   # nama database sesuai PostgreSQL
        'USER': 'eva',             # owner database
        'PASSWORD': 'toor',        # ganti dengan password user eva
        'HOST': 'localhost',
        'PORT': '5432',
    }
}

# Email console backend
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

EMAIL_HOST_USER = 'dummy@example.com'
EMAIL_HOST_PASSWORD = 'dummy'  # bisa kosong juga



INTERNAL_IPS = ['127.0.0.1']

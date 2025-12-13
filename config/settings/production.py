from .base import *
from decouple import config

DEBUG = False
ALLOWED_HOSTS = ['nusasawit.com', 'www.nusasawit.com']

# PostgreSQL
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'sdmporta_nusasawit',
        'USER': 'sdmporta_nusasawit_user',
        'PASSWORD': '@Pontianak123',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}

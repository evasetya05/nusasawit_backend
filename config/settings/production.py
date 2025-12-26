from .base import *
from decouple import config
import os

DEBUG = True
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


STATIC_URL = '/static/'
STATIC_ROOT = '/home/sdmporta/nusasawit.com/staticfiles'

MEDIA_URL = '/media/'
MEDIA_ROOT = '/home/sdmporta/nusasawit.com/media'

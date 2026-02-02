from .base import *
from decouple import config
import os

DEBUG = True
ALLOWED_HOSTS = ['127.0.0.1', 'nusasawit.com', 'www.nusasawit.com']

# PostgreSQL
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'sdmporta_nusasawit',
        'USER': 'sdmporta_nusasawit_user',
        'PASSWORD': '@Pontianak123',
        'HOST': '127.0.0.1',
        'PORT': '5432',
    }
}


STATIC_URL = '/static/'
STATIC_ROOT = '/home/sdmporta/nusasawit.com/staticfiles'

MEDIA_URL = '/media/'
MEDIA_ROOT = '/home/sdmporta/nusasawit.com/media'

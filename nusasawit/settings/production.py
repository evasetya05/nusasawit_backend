from .base import *

DEBUG = True

ALLOWED_HOSTS = ["nusasawit.sdmportabel.com", "www.nusasawit.sdmportabel.com"]

CORS_ALLOW_ALL_ORIGINS = True

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'sdmport_nusasawit',
        'USER': 'sdmport_nusasawit_user',
        'PASSWORD': '@Pontianak123',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}


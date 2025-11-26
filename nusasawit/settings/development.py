from .base import *

DEBUG = True

ALLOWED_HOSTS = ["127.0.0.1", "localhost", "192.168.18.13"]

CORS_ALLOW_ALL_ORIGINS = True

DATABASES = {
   'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'nusasawit_backend',
        'USER': 'eva',
        'PASSWORD': 'toor',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}
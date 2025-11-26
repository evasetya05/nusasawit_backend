from .base import *

DEBUG = True

ALLOWED_HOSTS = ["nusasawit.sdmportabel.com", "www.nusasawit.sdmportabel.com"]

CORS_ALLOW_ALL_ORIGINS = True

# Tambahkan ini agar WSGI dan URLConf dikenali
ROOT_URLCONF = 'nusasawit.urls'
WSGI_APPLICATION = 'nusasawit.wsgi.application'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'sdmporta_sdmport_nusasawit',
        'USER': 'sdmporta_sdmport_nusasawit_user',
        'PASSWORD': '@Pontianak123',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}



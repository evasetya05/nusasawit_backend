from .base import *
from decouple import config

DEBUG = False
ALLOWED_HOSTS = ['nusasawit.sdmportabel.com', 'www.nusasawit.sdmportabel.com']

# PostgreSQL
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
# Static files production
STATIC_ROOT = config('STATIC_ROOT', default=os.path.join(BASE_DIR, 'staticfiles'))

# Email production
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = config('EMAIL_HOST')
EMAIL_USE_TLS = config('EMAIL_USE_TLS', cast=bool)
EMAIL_USE_SSL = config('EMAIL_USE_SSL', cast=bool)
EMAIL_PORT = config('EMAIL_PORT', cast=int)
EMAIL_HOST_USER = config('EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD = config('EMAIL_HOST_PASSWORD')
DEFAULT_FROM_EMAIL = EMAIL_HOST_USER

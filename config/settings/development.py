from .base import *

DEBUG = True
ALLOWED_HOSTS = ['127.0.0.1', 'localhost']

# Database untuk development (PostgreSQL)
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

# Email console backend
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

EMAIL_HOST_USER = 'dummy@example.com'
EMAIL_HOST_PASSWORD = 'dummy'  # bisa kosong juga



# Disable debug toolbar for API testing
DEBUG_TOOLBAR = False
INTERNAL_IPS = []

STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
STATICFILES_DIRS = [os.path.join(BASE_DIR, 'static')]
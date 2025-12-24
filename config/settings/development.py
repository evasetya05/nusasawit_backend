from .base import *

DEBUG = True
ALLOWED_HOSTS = ['127.0.0.1', 'localhost']

# Database untuk development (PostgreSQL)
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'nusasawit_db',   # nama database sesuai PostgreSQL
        'USER': 'eva',             # owner database
        'PASSWORD': 'abc',        # ganti dengan password user eva
        'HOST': 'localhost',
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
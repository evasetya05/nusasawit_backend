import os
from pathlib import Path
from django.urls import reverse_lazy

# Base directory
BASE_DIR = Path(__file__).resolve().parent.parent.parent

# Secret key
# SECRET_KEY = 'replace_this'
# SECURITY WARNING: keep the secret key used in production secret!
# It's recommended to load this from an environment variable.
SECRET_KEY = os.environ.get('DJANGO_SECRET_KEY', 'django-insecure-fallback-key-for-c75e0c6b')

APP_SECRET_KEY = "NUSA-APP-KEY-15c9f3fd8c8943f8a3bcd871df1b6f49"


# Installed apps
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.humanize',

    'debug_toolbar',
    'django_registration',
    'ckeditor',
    'ckeditor_uploader',
    'widget_tweaks',
    'crispy_forms',
    'crispy_bootstrap4',

    'apps.account',
    'apps.core',
    'apps.extras.vacancy',
    'apps.extras.job',
    'apps.extras.psychometric',
    'apps.extras.blog',
    'apps.extras.legal',
    'apps.extras.syarat_ketentuan',
    'apps.modules.m1planning',
    'apps.modules.m2recruit',
    'apps.modules.m3onboarding',
    'apps.modules.kinerja4',
    'apps.modules.learning5',
    'apps.modules.compensation6',
    'apps.modules.compliance7',
    'apps.modules.ir8',
    'apps.modules.m9improvement',
    'apps.modules.area',
    'apps.modules.inbox',

    'api.tips', 
    'api.mitra_borongan', 
    'api.consultation',
    'api.sertifikasi',
    'api.user_flutter',
    'api.pasar',
    'api.petunjuk',
    'api.waypoint',
]

# Crispy Forms Configuration
CRISPY_TEMPLATE_PACK = 'bootstrap4'

# Middleware
MIDDLEWARE = [
    'debug_toolbar.middleware.DebugToolbarMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

# URL and WSGI
ROOT_URLCONF = 'config.urls'
WSGI_APPLICATION = 'config.wsgi.application'

# Templates
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

# Password validators
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# Localization
LANGUAGE_CODE = 'en'
LANGUAGES = (
    ('id', 'Indonesian'),
    ('en', 'English'),
)
LOCALE_PATHS = (os.path.join(BASE_DIR, 'locale'),)
TIME_ZONE = 'Asia/Jakarta'
USE_I18N = True
USE_L10N = True
USE_TZ = True

# Static and media files

STATIC_URL = '/static/'
# STATIC_ROOT should be defined in production.py
# STATIC_ROOT = '/home/sdmporta/nusasawit.com/staticfiles'

STATICFILES_DIRS = [os.path.join(BASE_DIR, 'static')]

MEDIA_URL = '/media/'
# MEDIA_ROOT should be defined in production.py
# MEDIA_ROOT = '/home/sdmporta/nusasawit.com/media'


# Auth
AUTH_USER_MODEL = 'account.SystemUser'
LOGIN_REDIRECT_URL = reverse_lazy('index')
LOGOUT_REDIRECT_URL = reverse_lazy('index')

ACCOUNT_ACTIVATION_DAYS = 7
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# CKEditor
CKEDITOR_CONFIGS = {
    'default': {
        'toolbar': 'Full',
        'extraPlugins': 'uploadimage',
        'filebrowserUploadUrl': '/ckeditor/upload/',
    },
}
CKEDITOR_UPLOAD_PATH = "uploads/"
CKEDITOR_IMAGE_BACKEND = "pillow"
CKEDITOR_ALLOW_NONIMAGE_FILES = False

# Email defaults (development)
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
EMAIL_HOST = 'localhost'
EMAIL_PORT = 25
EMAIL_USE_TLS = False
EMAIL_HOST_USER = 'dummy@example.com'
EMAIL_HOST_PASSWORD = ''

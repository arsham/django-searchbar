import os
BASE_DIR = os.path.dirname(os.path.dirname(__file__))
SECRET_KEY = 'kjuiyhgwkjfygwruig389o7tgo87gfheirgo3e8574o3g8i4gfui'
DEBUG = True
TEMPLATE_DEBUG = True
ALLOWED_HOSTS = []

INSTALLED_APPS = (
    'django.contrib.sessions',
    'django.contrib.messages',
)

MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
)

ROOT_URLCONF = 'django_searchbar.urls'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    }
}

LANGUAGE_CODE = 'en-gb'
TIME_ZONE = 'UTC'
USE_I18N = False
USE_L10N = False
USE_TZ = True

STATIC_URL = '/static/'

TEMPLATE_DIRS = (
    os.path.join(BASE_DIR, 'django_searchbar/templates'),
)

PASSWORD_HASHERS = (
    'django.contrib.auth.hashers.MD5PasswordHasher',
)

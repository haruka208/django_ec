from .base import *

import environ

DEBUG = False

env = environ.Env()
SECRET_KEY = env("SECRET_KEY")

ALLOWED_HOSTS = ['.herokuapp.com']

DATABASES = {
    "default": env.db(),
}

STATIC_ROOT = BASE_DIR / 'staticfiles'
STORAGES = {
    'staticfiles': {
        'BACKEND': 'whitenoise.storage.CompressedManifestStaticFilesStorage',
    },
}
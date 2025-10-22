from .base import *

import environ

DEBUG = True

env = environ.Env()
environ.Env.read_env(env_file=str(BASE_DIR) + '/.env')

SECRET_KEY = env('SECRET_KEY')

ALLOWED_HOSTS = ['*']

DATABASES = {
    'default': env.db(),
}

INSTALLED_APPS.insert(0, 'whitenoise.runserver_nostatic') #ローカル環境で本番と同じように WhiteNoise を使う設定

# EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend' # コンソールバックエンド
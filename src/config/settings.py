import logging
import os
from pathlib import Path

from src.utils.log_formatter import FormatterMode

# --- App settings ---

APP_ID: str = os.getenv('APP_ID', 'tournament_manager')
APP_ENVIRONMENT: str = os.getenv('APP_ENVIRONMENT', 'test')
APP_VERSION_FILE: str = 'src/.service_version'

DEBUG = int(os.getenv('DEBUG'))

LANGUAGE_PACKAGES_PATH = os.getenv('LANGUAGE_PACKAGES_PATH', 'tournament_manager')
DEFAULT_LANGUAGE: str = os.getenv('DEFAULT_LANGUAGE', 'ru')

# --- Telegram bot ---

BOT_TOKEN = os.getenv('BOT_TOKEN')

# --- logging ---

LOGGER_NAME: str = os.getenv('LOGGER_NAME', f'{APP_ID}_{APP_ENVIRONMENT}')
VERBOSE_LOGGER_NAME: str = os.getenv('VERBOSE_LOGGER_NAME', f'{APP_ID}_{APP_ENVIRONMENT}_verbose')

LOGGING_LEVEL: int = logging.DEBUG if DEBUG else logging.INFO

LOGGING = {
    'version': 1,
    'propagate': False,
    'disable_existing_loggers': False,
    'formatters': {
        'console': {
            'class': 'logging.Formatter',
            'format': '%(asctime)s.%(msecs)03d %(levelname)s %(message)s',
            'datefmt': '%Y-%m-%d %H:%M:%S',
        },
        'json_console': {
            '()': 'src.utils.log_formatter.LogFormatter',
            'formatter_mode': FormatterMode.COMPACT,
            'limit_keys_to': ['call_id', 'input_data', 'result', 'function_full_name'],
            'format': '%(asctime)s %(levelname)s %(message)s',
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'console',
        },
        'json_console': {
            'class': 'logging.StreamHandler',
            'formatter': 'json_console',
        },
    },
    'loggers': {
        'root': {
            'level': LOGGING_LEVEL,
            'handlers': ['console'],
        },
        VERBOSE_LOGGER_NAME: {
            'level': LOGGING_LEVEL,
            'handlers': ['json_console'],
        },
        LOGGER_NAME: {
            'level': LOGGING_LEVEL,
            'handlers': ['console'],
        },
        'django.server': {
            'level': LOGGING_LEVEL,
            'handlers': ['console'],
        },
        'uvicorn': {
            'level': LOGGING_LEVEL,
            'handlers': ['console'],
        },
    },
}

# --- Django ---

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = os.getenv('SECRET_KEY')

ALLOWED_HOSTS = [os.getenv('MAIN_HOST')]

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'src.apps.manager.apps.ManagerConfig',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'src.config.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
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

WSGI_APPLICATION = 'src.config.wsgi.application'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'postgres',
        'USER': os.getenv('DB_USER'),
        'PASSWORD': os.getenv('DB_PASSWORD'),
        'HOST': os.getenv('DB_HOST'),
        'PORT': int(os.getenv('DB_PORT')),
    },
}

AUTH_USER_MODEL = 'manager.CustomUser'

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True

STATIC_URL = 'static/'

STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

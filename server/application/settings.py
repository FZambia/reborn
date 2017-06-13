import os
import json
import dj_database_url
from django.core.exceptions import ImproperlyConfigured


CONFIG_PATH = os.environ.get("REBORN_CONFIG", "./config.json")

if os.path.exists(CONFIG_PATH):
    with open(CONFIG_PATH) as f:
        try:
            config = json.load(f)
        except ValueError:
            raise ImproperlyConfigured("Malformed configuration")
        if not isinstance(config, object):
            raise ImproperlyConfigured("Config must be object")
else:
    config = {}


def get_option(name, default_value):
    """
    get_option tries to extract option first from environment 
    and then from config file.

    Only str, int, bool and list of strings environment option 
    value types supported.
    """
    env_option_name = "REBORN_" + name.lower()
    env_option_name = env_option_name.replace(".", "_")

    if env_option_name.upper() in os.environ:
        option_type = type(default_value)
        value = os.environ[env_option_name.upper()]
        if option_type is str:
            return value
        elif option_type is int:
            return int(value)
        elif option_type is bool:
            return value.lower() in ["1", "true", "yes"]
        elif option_type is list:
            return value.split(",")
        raise ImproperlyConfigured("Unsupported configuration type: {}".format(option_type))

    if name.lower() in config:
        return config[name.lower()]

    return default_value


APP_NAME = get_option("app.name", "reborn")

APP_URL = get_option("app.url", "http://localhost:10000")

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

STATIC_ROOT = os.path.join(os.path.dirname(BASE_DIR), 'static')

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = get_option("app.secret_key", "vulnerable")

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = get_option("app.debug", False)

ALLOWED_HOSTS = get_option("app.allowed_hosts", ["*"])

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
    'rest_framework.authtoken',
    'social_django',
    'django_filters',
    'core',
    'users',
    'notifications',
    'loaders',
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

ROOT_URLCONF = 'application.urls'

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

WSGI_APPLICATION = 'application.wsgi.application'


default_database_url = 'sqlite:///' + os.path.join(BASE_DIR, 'db.sqlite3')
database_url = get_option("app.database.url", default_database_url)

DATABASES = {
    'default': dj_database_url.config(
        default=database_url
    )
}

# Password validation
# https://docs.djangoproject.com/en/1.11/ref/settings/#auth-password-validators
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


# Internationalization
# https://docs.djangoproject.com/en/1.11/topics/i18n/
LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True

STATIC_URL = '/static/'

REST_FRAMEWORK = {
    'DEFAULT_FILTER_BACKENDS': (
        'rest_framework.filters.DjangoFilterBackend',
    ),
    'DEFAULT_PARSER_CLASSES': (
        'rest_framework.parsers.JSONParser',
    )
}

AUTHENTICATION_BACKENDS = (
    'social.backends.facebook.FacebookOAuth2',
    'django.contrib.auth.backends.ModelBackend',
)

SOCIAL_AUTH_PIPELINE = (
    'social.pipeline.social_auth.social_details',
    'social.pipeline.social_auth.social_uid',
    'social.pipeline.social_auth.auth_allowed',
    'social.pipeline.social_auth.social_user',
    'social.pipeline.user.get_username',
    'social.pipeline.social_auth.associate_by_email',
    'social.pipeline.user.create_user',
    'social.pipeline.social_auth.associate_user',
    'social.pipeline.social_auth.load_extra_data',
    'social.pipeline.user.user_details'
)

SOCIAL_AUTH_FACEBOOK_KEY = get_option("auth.facebook.client_id", "")
SOCIAL_AUTH_FACEBOOK_SECRET = get_option("auth.facebook.secret", "")

LOGGING = {
    'version': 1,
    'disable_existing_loggers': True,
    'formatters': {
        'verbose': {
            'format': '%(levelname)s %(asctime)s %(module)s %(process)d %(thread)d %(message)s',
            'datefmt': '%Y-%m-%d %H:%M:%S'
        },
        'simple': {
            'format': '%(asctime)s [%(levelname)s] %(message)s',
            'datefmt': '%Y-%m-%d %H:%M:%S'
        },
    },
    'handlers': {
        'null': {
            'level': 'DEBUG',
            'class': 'logging.NullHandler',
        },
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'simple'
        },
        'mail_admins': {
            'level': 'ERROR',
            'class': 'django.utils.log.AdminEmailHandler',
        }
    },
    'loggers': {
        'django': {
            'handlers': ['null'],
            'propagate': True,
            'level': 'INFO',
        },
        'app': {
            'handlers': ['console'],
            'propagate': True,
            'level': 'DEBUG',
        },
        'django.request': {
            'handlers': ['mail_admins', 'console'],
            'level': 'ERROR',
            'propagate': False,
        }
    }
}

try:
    from local_settings import *
except ImportError:
    pass

if not DEBUG and len(SECRET_KEY) < 16:
    raise ImproperlyConfigured("SECRET_KEY missing or too short")

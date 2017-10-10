"""
Django settings for sso-profile project.

Generated by 'django-admin startproject' using Django 1.9.6.

For more information on this file, see
https://docs.djangoproject.com/en/1.9/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.9/ref/settings/
"""

import os

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
BASE_DIR = os.path.dirname(PROJECT_ROOT)


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.9/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.environ["SECRET_KEY"]

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = bool(os.getenv("DEBUG", False))

# As the app is running behind a host-based router supplied by Heroku or other
# PaaS, we can open ALLOWED_HOSTS
ALLOWED_HOSTS = ['*']


# Application definition

INSTALLED_APPS = [
    "django.contrib.staticfiles",
    "django.contrib.humanize",
    "raven.contrib.django.raven_compat",
    "django.contrib.sessions",
    "django.contrib.contenttypes",  # required by DRF, not using any DB
    "django.contrib.auth",
    "directory_constants",
    "directory_header_footer",
    "profile",
    "profile.api"
]

MIDDLEWARE_CLASSES = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'sso.middleware.SSOUserMiddleware',
    'config.middleware.NoCacheMiddlware',
]

ROOT_URLCONF = 'config.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'directory_header_footer.context_processors.sso_processor',
                (
                    'directory_header_footer.context_processors.'
                    'header_footer_context_processor'
                ),
                'config.context_processors.feature_flags',
                'config.context_processors.analytics',
                'sso.context_processors.sso_processor',
            ],
        },
    },
]

WSGI_APPLICATION = 'config.wsgi.application'


# # Database
# hard to get rid of this
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    }
}

CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
    }
}

# Internationalization
# https://docs.djangoproject.com/en/1.9/topics/i18n/

LANGUAGE_CODE = 'en-gb'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True

MEDIA_ROOT = os.path.join(PROJECT_ROOT, 'media')

# Static files served with Whitenoise and AWS Cloudfront
# http://whitenoise.evans.io/en/stable/django.html#instructions-for-amazon-cloudfront
# http://whitenoise.evans.io/en/stable/django.html#restricting-cloudfront-to-static-files
STATIC_ROOT = os.path.join(PROJECT_ROOT, 'staticfiles')
STATIC_HOST = os.environ.get('STATIC_HOST', '')
STATIC_URL = STATIC_HOST + '/static/'
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'


# Logging for development
if DEBUG:
    LOGGING = {
        'version': 1,
        'disable_existing_loggers': False,
        'filters': {
            'require_debug_false': {
                '()': 'django.utils.log.RequireDebugFalse'
            }
        },
        'handlers': {
            'console': {
                'level': 'DEBUG',
                'class': 'logging.StreamHandler',
            },
        },
        'loggers': {
            'django.request': {
                'handlers': ['console'],
                'level': 'ERROR',
                'propagate': True,
            },
            '': {
                'handlers': ['console'],
                'level': 'DEBUG',
                'propagate': False,
            },
        }
    }
else:
    # Sentry logging
    LOGGING = {
        'version': 1,
        'disable_existing_loggers': False,
        'root': {
            'level': 'WARNING',
            'handlers': ['sentry'],
        },
        'formatters': {
            'verbose': {
                'format': '%(levelname)s %(asctime)s %(module)s '
                          '%(process)d %(thread)d %(message)s'
            },
        },
        'handlers': {
            'sentry': {
                'level': 'ERROR',
                'class': (
                    'raven.contrib.django.raven_compat.handlers.SentryHandler'
                ),
                'tags': {'custom-tag': 'x'},
            },
            'console': {
                'level': 'DEBUG',
                'class': 'logging.StreamHandler',
                'formatter': 'verbose'
            }
        },
        'loggers': {
            'raven': {
                'level': 'DEBUG',
                'handlers': ['console'],
                'propagate': False,
            },
            'sentry.errors': {
                'level': 'DEBUG',
                'handlers': ['console'],
                'propagate': False,
            },
        },
    }


# directory-external-api
DIRECTORY_API_EXTERNAL_CLIENT_CLASSES = {
    'default': 'directory_api_external.client.DirectoryAPIExternalClient',
    'unit-test': (
        'directory_api_external.dummy_client.DummyDirectoryAPIExternalClient'
    ),
}
DIRECTORY_API_EXTERNAL_CLIENT_CLASS_NAME = os.getenv(
    'DIRECTORY_API_EXTERNAL_CLIENT_CLASS_NAME', 'default'
)
DIRECTORY_API_EXTERNAL_CLIENT_CLASS = DIRECTORY_API_EXTERNAL_CLIENT_CLASSES[
    DIRECTORY_API_EXTERNAL_CLIENT_CLASS_NAME
]
DIRECTORY_API_EXTERNAL_SIGNATURE_SECRET = os.environ[
    'DIRECTORY_API_EXTERNAL_SIGNATURE_SECRET'
]
DIRECTORY_API_EXTERNAL_CLIENT_BASE_URL = os.environ[
    'DIRECTORY_API_EXTERNAL_CLIENT_BASE_URL'
]

# directory-sso
SSO_PROXY_API_CLIENT_BASE_URL = os.environ["SSO_PROXY_API_CLIENT_BASE_URL"]
SSO_PROXY_SIGNATURE_SECRET = os.environ["SSO_PROXY_SIGNATURE_SECRET"]
SSO_PROXY_LOGIN_URL = os.environ["SSO_PROXY_LOGIN_URL"]
SSO_PROXY_LOGOUT_URL = os.environ["SSO_PROXY_LOGOUT_URL"]
SSO_PROXY_SIGNUP_URL = os.environ["SSO_PROXY_SIGNUP_URL"]
SSO_PROXY_PASSWORD_RESET_URL = os.environ["SSO_PROXY_PASSWORD_RESET_URL"]
SSO_PROXY_REDIRECT_FIELD_NAME = os.environ["SSO_PROXY_REDIRECT_FIELD_NAME"]
SSO_PROXY_SESSION_COOKIE = os.environ["SSO_PROXY_SESSION_COOKIE"]
SSO_PROFILE_URL = os.environ["SSO_PROFILE_URL"]
SSO_PROXY_API_OAUTH2_BASE_URL = os.environ["SSO_PROXY_API_OAUTH2_BASE_URL"]

ANALYTICS_ID = os.getenv("ANALYTICS_ID")

SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
SECURE_HSTS_SECONDS = int(os.getenv('SECURE_HSTS_SECONDS', '16070400'))
SECURE_HSTS_INCLUDE_SUBDOMAINS = True

# Sentry
RAVEN_CONFIG = {
    "dsn": os.getenv("SENTRY_DSN"),
}

SESSION_ENGINE = "django.contrib.sessions.backends.signed_cookies"
SESSION_COOKIE_SECURE = os.getenv('SESSION_COOKIE_SECURE', 'true') == 'true'
SESSION_COOKIE_HTTPONLY = True
CSRF_COOKIE_SECURE = True

# Google tag manager
GOOGLE_TAG_MANAGER_ID = os.environ['GOOGLE_TAG_MANAGER_ID']
GOOGLE_TAG_MANAGER_ENV = os.getenv('GOOGLE_TAG_MANAGER_ENV', '')
UTM_COOKIE_DOMAIN = os.environ['UTM_COOKIE_DOMAIN']


EXPORTING_OPPORTUNITIES_API_BASIC_AUTH_USERNAME = os.getenv(
    "EXPORTING_OPPORTUNITIES_API_BASIC_AUTH_USERNAME"
)
EXPORTING_OPPORTUNITIES_API_BASIC_AUTH_PASSWORD = os.getenv(
    "EXPORTING_OPPORTUNITIES_API_BASIC_AUTH_PASSWORD"
)
EXPORTING_OPPORTUNITIES_API_BASE_URL = os.environ[
    "EXPORTING_OPPORTUNITIES_API_BASE_URL"
]
EXPORTING_OPPORTUNITIES_API_SECRET = os.environ[
    "EXPORTING_OPPORTUNITIES_API_SECRET"
]
EXPORTING_OPPORTUNITIES_SEARCH_URL = os.environ[
    "EXPORTING_OPPORTUNITIES_SEARCH_URL"
]

# find a buyer
FAB_REGISTER_URL = os.environ['FAB_REGISTER_URL']
FAB_EDIT_COMPANY_LOGO_URL = os.environ['FAB_EDIT_COMPANY_LOGO_URL']
FAB_EDIT_PROFILE_URL = os.environ['FAB_EDIT_PROFILE_URL']
FAB_ADD_CASE_STUDY_URL = os.environ['FAB_ADD_CASE_STUDY_URL']
FAB_ADD_USER_URL = os.environ['FAB_ADD_USER_URL']
FAB_REMOVE_USER_URL = os.environ['FAB_REMOVE_USER_URL']
FAB_TRANSFER_ACCOUNT_URL = os.environ['FAB_TRANSFER_ACCOUNT_URL']

HEADER_FOOTER_CONTACT_US_URL = os.getenv(
    'HEADER_FOOTER_CONTACT_US_URL',
    'https://contact-us.export.great.gov.uk/directory',
)

# feature flags
FEATURE_MULTI_USER_ACCOUNT_ENABLED = os.getenv(
    'FEATURE_MULTI_USER_ACCOUNT_ENABLED'
) == 'true'

FEATURE_NEW_SHARED_HEADER_ENABLED = os.getenv(
    'FEATURE_NEW_SHARED_HEADER_ENABLED'
) == 'true'

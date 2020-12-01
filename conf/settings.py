"""
Django settings for sso-profile project.

Generated by 'django-admin startproject' using Django 1.9.6.

For more information on this file, see
https://docs.djangoproject.com/en/1.9/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.9/ref/settings/
"""

import os

import directory_healthcheck.backends
import environ
import sentry_sdk
from sentry_sdk.integrations.django import DjangoIntegration

env = environ.Env()
for env_file in env.list('ENV_FILES', default=[]):
    env.read_env(f'conf/env/{env_file}')


# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.9/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = env.str('SECRET_KEY')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = env.bool('DEBUG', False)

# As the app is running behind a host-based router supplied by Heroku or other
# PaaS, we can open ALLOWED_HOSTS
ALLOWED_HOSTS = ['*']

# Application definition

INSTALLED_APPS = [
    'django.contrib.staticfiles',
    'django.contrib.humanize',
    'django.contrib.auth',
    'django.contrib.sessions',
    'django.contrib.contenttypes',  # required by DRF and auth, not using DB
    'django.contrib.messages',
    'directory_sso_api_client',
    'captcha',
    'core',
    'sso',
    'directory_constants',
    'directory_components',
    'profile',
    'enrolment',
    'health_check.cache',
    'directory_healthcheck',
]


MIDDLEWARE = [
    'directory_components.middleware.MaintenanceModeMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'core.middleware.PrefixUrlMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'directory_sso_api_client.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'directory_components.middleware.NoCacheMiddlware',
]


ROOT_URLCONF = 'conf.urls'


TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.messages.context_processors.messages',
                'directory_components.context_processors.urls_processor',
                'directory_components.context_processors.header_footer_processor',
                'directory_components.context_processors.sso_processor',
                'directory_components.context_processors.ga360',
                'directory_components.context_processors.analytics',
                'directory_components.context_processors.feature_flags',
                'directory_components.context_processors.cookie_notice',
            ]
        },
    }
]

WSGI_APPLICATION = 'conf.wsgi.application'


VCAP_SERVICES = env.json('VCAP_SERVICES', {})

if 'redis' in VCAP_SERVICES:
    REDIS_URL = VCAP_SERVICES['redis'][0]['credentials']['uri']
else:
    REDIS_URL = env.str('REDIS_URL')

cache = {
    'BACKEND': 'django_redis.cache.RedisCache',
    'LOCATION': REDIS_URL,
    'OPTIONS': {'CLIENT_CLASS': 'django_redis.client.DefaultClient'},
}

CACHES = {'default': cache, 'api_fallback': cache}

# Internationalization
# https://docs.djangoproject.com/en/1.9/topics/i18n/

LANGUAGE_CODE = 'en-gb'

TIME_ZONE = 'UTC'

USE_L10N = True

USE_TZ = True

MEDIA_ROOT = os.path.join(PROJECT_ROOT, 'media')

# Static files served with Whitenoise and AWS Cloudfront
# http://whitenoise.evans.io/en/stable/django.html#instructions-for-amazon-cloudfront
# http://whitenoise.evans.io/en/stable/django.html#restricting-cloudfront-to-static-files
STATIC_ROOT = os.path.join(PROJECT_ROOT, 'staticfiles')
STATIC_HOST = env.str('STATIC_HOST', '')
STATIC_URL = STATIC_HOST + '/static/'
STATICFILES_STORAGE = env.str('STATICFILES_STORAGE', 'whitenoise.storage.CompressedManifestStaticFilesStorage')


# Public storage for uploaded logos and case study images
STORAGE_CLASS_NAME = env.str('STORAGE_CLASS_NAME', 'default')

if STORAGE_CLASS_NAME == 'local-storage':
    DEFAULT_FILE_STORAGE = 'django.core.files.storage.FileSystemStorage'
elif STORAGE_CLASS_NAME == 'default':
    DEFAULT_FILE_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'
    AWS_ACCESS_KEY_ID = env.str('AWS_ACCESS_KEY_ID')
    AWS_SECRET_ACCESS_KEY = env.str('AWS_SECRET_ACCESS_KEY')
    AWS_STORAGE_BUCKET_NAME = env.str('AWS_STORAGE_BUCKET_NAME')
    AWS_DEFAULT_ACL = 'public-read'
    AWS_AUTO_CREATE_BUCKET = True
    AWS_S3_ENCRYPTION = False
    AWS_S3_FILE_OVERWRITE = False
    AWS_S3_CUSTOM_DOMAIN = env.str('AWS_S3_CUSTOM_DOMAIN', '')
    AWS_S3_URL_PROTOCOL = env.str('AWS_S3_URL_PROTOCOL', 'https:')
    # Needed for new AWS regions
    # https://github.com/jschneier/django-storages/issues/203
    AWS_S3_SIGNATURE_VERSION = env.str('AWS_S3_SIGNATURE_VERSION', 's3v4')
    AWS_QUERYSTRING_AUTH = env.bool('AWS_QUERYSTRING_AUTH', False)
    S3_USE_SIGV4 = env.bool('S3_USE_SIGV4', True)
    AWS_S3_HOST = env.str('AWS_S3_HOST', 's3.eu-west-1.amazonaws.com')
else:
    raise NotImplementedError()

# Logging for development
if DEBUG:
    LOGGING = {
        'version': 1,
        'disable_existing_loggers': False,
        'filters': {'require_debug_false': {'()': 'django.utils.log.RequireDebugFalse'}},
        'handlers': {'console': {'level': 'DEBUG', 'class': 'logging.StreamHandler'}},
        'loggers': {
            'django.request': {'handlers': ['console'], 'level': 'ERROR', 'propagate': True},
            '': {'handlers': ['console'], 'level': 'DEBUG', 'propagate': False},
        },
    }

# Sentry
if env.str('SENTRY_DSN', ''):
    sentry_sdk.init(
        dsn=env.str('SENTRY_DSN'), environment=env.str('SENTRY_ENVIRONMENT'), integrations=[DjangoIntegration()]
    )


# SSO API Client
DIRECTORY_SSO_API_CLIENT_BASE_URL = env.str('SSO_API_CLIENT_BASE_URL', '')
DIRECTORY_SSO_API_CLIENT_API_KEY = env.str('SSO_SIGNATURE_SECRET', '')
DIRECTORY_SSO_API_CLIENT_SENDER_ID = env.str('DIRECTORY_SSO_API_CLIENT_SENDER_ID', 'directory')
DIRECTORY_SSO_API_CLIENT_DEFAULT_TIMEOUT = 15

SSO_PROXY_LOGIN_URL = env.str('SSO_PROXY_LOGIN_URL')
LOGIN_URL = SSO_PROXY_LOGIN_URL
SSO_PROXY_LOGOUT_URL = env.str('SSO_PROXY_LOGOUT_URL')
SSO_PROXY_SIGNUP_URL = env.str('SSO_PROXY_SIGNUP_URL')
SSO_PROXY_PASSWORD_RESET_URL = env.str('SSO_PROXY_PASSWORD_RESET_URL')
SSO_PROXY_REDIRECT_FIELD_NAME = env.str('SSO_PROXY_REDIRECT_FIELD_NAME')
SSO_SESSION_COOKIE = env.str('SSO_SESSION_COOKIE')
SSO_PROFILE_URL = env.str('SSO_PROFILE_URL')

SECURE_SSL_REDIRECT = env.bool('SECURE_SSL_REDIRECT', True)
USE_X_FORWARDED_HOST = True
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
SECURE_HSTS_SECONDS = env.int('SECURE_HSTS_SECONDS', 16070400)
SECURE_HSTS_INCLUDE_SUBDOMAINS = True

# HEADER AND FOOTER LINKS
DIRECTORY_CONSTANTS_URL_EXPORT_OPPORTUNITIES = env.str('DIRECTORY_CONSTANTS_URL_EXPORT_OPPORTUNITIES', '')
DIRECTORY_CONSTANTS_URL_SELLING_ONLINE_OVERSEAS = env.str('DIRECTORY_CONSTANTS_URL_SELLING_ONLINE_OVERSEAS', '')
DIRECTORY_CONSTANTS_URL_EVENTS = env.str('DIRECTORY_CONSTANTS_URL_EVENTS', '')
DIRECTORY_CONSTANTS_URL_INVEST = env.str('DIRECTORY_CONSTANTS_URL_INVEST', '')
DIRECTORY_CONSTANTS_URL_FIND_A_SUPPLIER = env.str('DIRECTORY_CONSTANTS_URL_FIND_A_SUPPLIER', '')
DIRECTORY_CONSTANTS_URL_SINGLE_SIGN_ON = env.str('DIRECTORY_CONSTANTS_URL_SINGLE_SIGN_ON', '')
DIRECTORY_CONSTANTS_URL_FIND_A_BUYER = env.str('DIRECTORY_CONSTANTS_URL_FIND_A_BUYER', '')
DIRECTORY_CONSTANTS_URL_GREAT_DOMESTIC = env.str('DIRECTORY_CONSTANTS_URL_GREAT_DOMESTIC', '')
DIRECTORY_CONSTANTS_URL_INTERNATIONAL = env.str('DIRECTORY_CONSTANTS_URL_INTERNATIONAL', '')
DIRECTORY_CONSTANTS_URL_INVESTMENT_SUPPORT_DIRECTORY = env.str(
    'DIRECTORY_CONSTANTS_URL_INVESTMENT_SUPPORT_DIRECTORY', ''
)

SESSION_ENGINE = 'django.contrib.sessions.backends.signed_cookies'
SESSION_COOKIE_SECURE = env.bool('SESSION_COOKIE_SECURE', True)
SESSION_COOKIE_NAME = env.str('SESSION_COOKIE_NAME', 'profile_sessionid')
SESSION_COOKIE_HTTPONLY = True
CSRF_COOKIE_SECURE = True

# Google tag manager
GOOGLE_TAG_MANAGER_ID = env.str('GOOGLE_TAG_MANAGER_ID')
GOOGLE_TAG_MANAGER_ENV = env.str('GOOGLE_TAG_MANAGER_ENV', '')
UTM_COOKIE_DOMAIN = env.str('UTM_COOKIE_DOMAIN')
GA360_BUSINESS_UNIT = 'SSOProfile'


EXPORTING_OPPORTUNITIES_API_BASIC_AUTH_USERNAME = env.str('EXPORTING_OPPORTUNITIES_API_BASIC_AUTH_USERNAME', '')
EXPORTING_OPPORTUNITIES_API_BASIC_AUTH_PASSWORD = env.str('EXPORTING_OPPORTUNITIES_API_BASIC_AUTH_PASSWORD', '')
EXPORTING_OPPORTUNITIES_API_BASE_URL = env.str('EXPORTING_OPPORTUNITIES_API_BASE_URL')
EXPORTING_OPPORTUNITIES_API_SECRET = env.str('EXPORTING_OPPORTUNITIES_API_SECRET')
EXPORTING_OPPORTUNITIES_SEARCH_URL = env.str('EXPORTING_OPPORTUNITIES_SEARCH_URL')

# feature flags
FEATURE_FLAGS = {
    'COUNTRY_SELECTOR_ON': False,
    'MAINTENANCE_MODE_ON': env.bool('FEATURE_MAINTENANCE_MODE_ENABLED', False),  # used by directory-components
    'ADMIN_REQUESTS_ON': env.bool('FEATURE_ADMIN_REQUESTS_ENABLED', False),
}

# Healthcheck
DIRECTORY_HEALTHCHECK_TOKEN = env.str('HEALTH_CHECK_TOKEN')
DIRECTORY_HEALTHCHECK_BACKENDS = [
    directory_healthcheck.backends.SingleSignOnBackend,
    directory_healthcheck.backends.APIBackend,
    # health_check.cache.CacheBackend is also registered in
    # INSTALLED_APPS's health_check.cache
]


REST_FRAMEWORK = {'DEFAULT_RENDERER_CLASSES': ('rest_framework.renderers.JSONRenderer',)}

# Google captcha
RECAPTCHA_PUBLIC_KEY = env.str('RECAPTCHA_PUBLIC_KEY')
RECAPTCHA_PRIVATE_KEY = env.str('RECAPTCHA_PRIVATE_KEY')
RECAPTCHA_REQUIRED_SCORE = env.int('RECAPTCHA_REQUIRED_SCORE', 0.5)
# NOCAPTCHA = True turns on version 2 of recaptcha
NOCAPTCHA = env.bool('NOCAPTCHA', True)
SILENCED_SYSTEM_CHECKS = ['captcha.recaptcha_test_key_error']


# Companies House Search
DIRECTORY_CH_SEARCH_CLIENT_BASE_URL = env.str('DIRECTORY_CH_SEARCH_CLIENT_BASE_URL')
DIRECTORY_CH_SEARCH_CLIENT_API_KEY = env.str('DIRECTORY_CH_SEARCH_CLIENT_API_KEY')
DIRECTORY_CH_SEARCH_CLIENT_SENDER_ID = env.str('DIRECTORY_CH_SEARCH_CLIENT_SENDER_ID', 'directory')
DIRECTORY_CH_SEARCH_CLIENT_DEFAULT_TIMEOUT = env.str('DIRECTORY_CH_SEARCH_CLIENT_DEFAULT_TIMEOUT', 5)

# getAddress.io
GET_ADDRESS_API_KEY = env.str('GET_ADDRESS_API_KEY')

# directory forms api client
DIRECTORY_FORMS_API_BASE_URL = env.str('DIRECTORY_FORMS_API_BASE_URL')
DIRECTORY_FORMS_API_API_KEY = env.str('DIRECTORY_FORMS_API_API_KEY')
DIRECTORY_FORMS_API_SENDER_ID = env.str('DIRECTORY_FORMS_API_SENDER_ID')
DIRECTORY_FORMS_API_DEFAULT_TIMEOUT = env.int('DIRECTORY_API_FORMS_DEFAULT_TIMEOUT', 5)

# gov.uk notify
CONFIRM_VERIFICATION_CODE_TEMPLATE_ID = env.str(
    'CONFIRM_VERIFICATION_CODE_TEMPLATE_ID', 'a1eb4b0c-9bab-44d3-ac2f-7585bf7da24c'
)
GOV_NOTIFY_ALREADY_REGISTERED_TEMPLATE_ID = env.str(
    'GOV_NOTIFY_ALREADY_REGISTERED_TEMPLATE_ID', '5c8cc5aa-a4f5-48ae-89e6-df5572c317ec'
)
GOV_NOTIFY_NEW_MEMBER_REGISTERED_TEMPLATE_ID = env.str(
    'GOV_NOTIFY_NEW_MEMBER_REGISTERED_TEMPLATE_ID', '439a8415-52d8-4975-b230-15cd34305bb5'
)

GOV_NOTIFY_COLLABORATION_REQUEST_RESENT = env.str(
    'GOV_NOTIFY_COLLABORATION_REQUEST_RESENT', '60c14d97-8e58-4e5f-96e9-e0ca49bc3b96'
)


# directory api
DIRECTORY_API_CLIENT_BASE_URL = env.str('DIRECTORY_API_CLIENT_BASE_URL')
DIRECTORY_API_CLIENT_API_KEY = env.str('DIRECTORY_API_CLIENT_API_KEY')
DIRECTORY_API_CLIENT_SENDER_ID = env.str('DIRECTORY_API_CLIENT_SENDER_ID', 'directory')
DIRECTORY_API_CLIENT_DEFAULT_TIMEOUT = env.str('DIRECTORY_API_CLIENT_DEFAULT_TIMEOUT', 15)

# directory client core
DIRECTORY_CLIENT_CORE_CACHE_EXPIRE_SECONDS = 60 * 60 * 24 * 30  # 30 days


# parity with nginx config for maximum request body
DATA_UPLOAD_MAX_MEMORY_SIZE = 6 * 1024 * 1024
FILE_UPLOAD_MAX_MEMORY_SIZE = 6 * 1024 * 1024

# directory validators
VALIDATOR_MAX_LOGO_SIZE_BYTES = env.int('VALIDATOR_MAX_LOGO_SIZE_BYTES', 2 * 1024 * 1024)
VALIDATOR_MAX_CASE_STUDY_IMAGE_SIZE_BYTES = env.int('VALIDATOR_MAX_CASE_STUDY_IMAGE_SIZE_BYTES', 2 * 1024 * 1024)
VALIDATOR_MAX_CASE_STUDY_VIDEO_SIZE_BYTES = env.int('VALIDATOR_MAX_CASE_STUDY_VIDEO_SIZE_BYTES', 20 * 1024 * 1024)

AUTH_USER_MODEL = 'sso.SSOUser'

AUTHENTICATION_BACKENDS = ['directory_sso_api_client.backends.SSOUserBackend']


# Directory Components
if env.bool('FEATURE_SETTINGS_JANITOR_ENABLED', False):
    INSTALLED_APPS.append('directory_components.janitor')
    DIRECTORY_COMPONENTS_VAULT_DOMAIN = env.str('DIRECTORY_COMPONENTS_VAULT_DOMAIN')
    DIRECTORY_COMPONENTS_VAULT_ROOT_PATH = env.str('DIRECTORY_COMPONENTS_VAULT_ROOT_PATH')
    DIRECTORY_COMPONENTS_VAULT_PROJECT = env.str('DIRECTORY_COMPONENTS_VAULT_PROJECT')

PRIVACY_COOKIE_DOMAIN = env.str('PRIVACY_COOKIE_DOMAIN')
URL_PREFIX_DOMAIN = env.str('URL_PREFIX_DOMAIN', '')

# message framework
MESSAGE_STORAGE = 'django.contrib.messages.storage.session.SessionStorage'

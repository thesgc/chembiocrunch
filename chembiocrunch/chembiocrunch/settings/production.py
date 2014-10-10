"""Production settings and globals."""

from __future__ import absolute_import

from os import environ

from .base import *

# Normally you should not import ANYTHING from Django directly
# into your settings, but ImproperlyConfigured is an exception.
from django.core.exceptions import ImproperlyConfigured
DEBUG=True

def get_env_setting(setting):
    """ Get the environment setting or return exception """
    try:
        return environ[setting]
    except KeyError:
        error_msg = "Set the %s env variable" % setting
        raise ImproperlyConfigured(error_msg)

########## HOST CONFIGURATION
# See: https://docs.djangoproject.com/en/1.5/releases/1.5/#allowed-hosts-required-in-production
ALLOWED_HOSTS = ["chembiohub.ox.ac.uk"]
########## END HOST CONFIGURATION

LOGIN_URL = "/crunch/accounts/login"
USE_X_FORWARDED_HOST = True
FORCE_SCRIPT_NAME = ""
STATIC_URL = '/crunch/static/'
INSTALLED_APPS = list(INSTALLED_APPS) + ["django_webauth",] 
print INSTALLED_APPS
AUTHENTICATION_BACKENDS =  ["django.contrib.auth.backends.ModelBackend","django_webauth.backends.WebauthLDAP"]
LOGIN_REDIRECT_URL = '/crunch/my_workflows/'
########## EMAIL CONFIGURATION
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
# See: https://docs.djangoproject.com/en/dev/ref/settings/#email-backend
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'

# See: https://docs.djangoproject.com/en/dev/ref/settings/#email-host
EMAIL_HOST = environ.get('EMAIL_HOST', 'smtp.gmail.com')

# See: https://docs.djangoproject.com/en/dev/ref/settings/#email-host-password
EMAIL_HOST_PASSWORD = environ.get('EMAIL_HOST_PASSWORD', '')

# See: https://docs.djangoproject.com/en/dev/ref/settings/#email-host-user
EMAIL_HOST_USER = environ.get('EMAIL_HOST_USER', 'your_email@example.com')

# See: https://docs.djangoproject.com/en/dev/ref/settings/#email-port
EMAIL_PORT = environ.get('EMAIL_PORT', 587)

# See: https://docs.djangoproject.com/en/dev/ref/settings/#email-subject-prefix
EMAIL_SUBJECT_PREFIX = '[%s] ' % SITE_NAME

# See: https://docs.djangoproject.com/en/dev/ref/settings/#email-use-tls
EMAIL_USE_TLS = True

# See: https://docs.djangoproject.com/en/dev/ref/settings/#server-email
SERVER_EMAIL = EMAIL_HOST_USER
########## END EMAIL CONFIGURATION

########## DATABASE CONFIGURATION

########## END DATABASE CONFIGURATION


########## CACHE CONFIGURATION
# See: https://docs.djangoproject.com/en/dev/ref/settings/#caches

CACHES = {
	    'default': {
	        'BACKEND': 'redis_cache.RedisCache',
	        'LOCATION': '127.0.0.1:6379',
	        'KEY_PREFIX' :"chembiocrunch",
	        'OPTIONS': {
	            'DB': 1,
	            'PARSER_CLASS': 'redis.connection.HiredisParser',
	            'CONNECTION_POOL_CLASS': 'redis.BlockingConnectionPool',
	            'CONNECTION_POOL_CLASS_KWARGS': {
	                'max_connections': 50,
	                'timeout': 20,
	            }
	        },
	    },
	}


########## END SECRET CONFIGURATION
DEBUG=True

########## MEDIA CONFIGURATION
# See: https://docs.djangoproject.com/en/dev/ref/settings/#media-root
MEDIA_ROOT = '/var/lib/data/chembiocrunch/'

# See: https://docs.djangoproject.com/en/dev/ref/settings/#media-url
MEDIA_URL = '/media/'
########## END MEDIA CONFIGURATION

from .secret import *

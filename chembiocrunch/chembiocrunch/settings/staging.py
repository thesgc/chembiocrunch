from .production import *


INSTALLED_APPS += (
    'django_shell_ipynb',
    'djangobower',
    'rest_framework',
    'qpcr',
    'gunicorn',
)

STATICFILES_FINDERS += ('djangobower.finders.BowerFinder',)
BOWER_COMPONENTS_ROOT =  SITE_ROOT + '/bower_components/'

BOWER_INSTALLED_APPS = (
    'chembiocrunch_vis',
)

ALLOWED_INCLUDE_ROOTS = ('/home/vagrant', '/var/www')
ALLOWED_HOSTS = "*"
DEBUG = True
LOGGING_CONFIG =None

MEDIA_ROOT = '/var/lib/data/chembiocrunch/'

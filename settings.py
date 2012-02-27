import os

APP_NAME = 'lightrail'
APP_VERSION = '0.1'
API_KEYS = (
    'defaultapikey',
)
DEBUG = False

APPLICATIONS_ROOT = '/var/tmp/apps'
VIRTUALENV_ROOT = '/var/tmp/ve'
APPLICATION_STATE_DIR = '/var/tmp/state'
SUPERVISOR_CONF_DIR = '/etc/supervisor/conf.d'

# check app dirs
if not os.path.exists(APPLICATIONS_ROOT):
    os.makedirs(APPLICATIONS_ROOT)
if not os.path.exists(VIRTUALENV_ROOT):
    os.makedirs(VIRTUALENV_ROOT)
if not os.path.exists(APPLICATION_STATE_DIR):
    os.makedirs(APPLICATION_STATE_DIR)
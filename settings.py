import os

APP_NAME = 'lightrail'
APP_VERSION = '0.1'
API_KEYS = (
    'defaultapikey',
)
DEBUG = False
REDIS_HOST = 'localhost'
REDIS_PORT = 6379
REDIS_DB = 0
REDIS_PASSWORD = None
TASK_QUEUE_NAME = 'queue'
TASK_QUEUE_KEY_TTL = 86400

APPLICATIONS_ROOT = '/var/tmp/apps'
APPLICATION_STATE_DIR = '/var/tmp/state'
NGINX_CONF_DIR = '/var/tmp/nginx'
SUPERVISOR_CONF_DIR = '/var/tmp/supervisor'
VIRTUALENV_ROOT = '/var/tmp/ve'

try:
    from local_settings import *
except:
    pass

# check app dirs
if not os.path.exists(APPLICATIONS_ROOT):
    os.makedirs(APPLICATIONS_ROOT)
if not os.path.exists(APPLICATION_STATE_DIR):
    os.makedirs(APPLICATION_STATE_DIR)
if not os.path.exists(NGINX_CONF_DIR):
    os.makedirs(NGINX_CONF_DIR)
if not os.path.exists(SUPERVISOR_CONF_DIR):
    os.makedirs(SUPERVISOR_CONF_DIR)
if not os.path.exists(VIRTUALENV_ROOT):
    os.makedirs(VIRTUALENV_ROOT)

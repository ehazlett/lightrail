import os
TESTING = True
DEBUG = True
APPLICATIONS_ROOT = './tmp/apps'
APPLICATION_STATE_DIR = './tmp/state'
APPLICATION_USER = 'www-data'
NGINX_CONF_DIR = './tmp/nginx'
SUPERVISOR_CONF_DIR = './tmp/supervisor'
VIRTUALENV_ROOT = './tmp/ve'
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

import zipfile
import tempfile
import os
import shutil
import logging
import subprocess
from config import create_app
import time
import pwd
from queue import task
try:
    import simplejson as json
except ImportError:
    import json
from utils import generate_uwsgi_config, generate_nginx_config

app = create_app()

class Application(object):
    '''
        Application

    '''
    def __init__(self, app_name=None):
        self._app_pkg = None
        self._tmp_dir = tempfile.mkdtemp()
        self._apps_root = app.config.get('APPLICATIONS_ROOT', None)
        self._ve_root = app.config.get('VIRTUALENV_ROOT', None)
        self._app_state_dir = app.config.get('APPLICATION_STATE_DIR', None)
        self._supervisor_conf_dir = app.config.get('SUPERVISOR_CONF_DIR', None)
        self._nginx_conf_dir = app.config.get('NGINX_CONF_DIR', None)
        self._manifest = None
        self._log = logging.getLogger('api')
        if app_name:
            self._app_name = app_name
            self._log.debug('Loading existing application manifest for {0}'.format(app_name))
            app_manifest = os.path.join(os.path.join(self._apps_root, app_name), 'manifest.json')
            # try to read existing manifest
            if os.path.exists(app_manifest):
                self._read_manifest(app_manifest)
            else:
                raise RuntimeError('Unable to find application manaifest for {0}'.format(app_name))

    def _unbundle(self):
        self._log.debug('Extracting {0}'.format(self._app_pkg))
        z = zipfile.ZipFile(self._app_pkg, 'r')
        z.extractall(self._tmp_dir)

    def _read_manifest(self, manifest=None):
        if not manifest:
            manifest = os.path.join(self._tmp_dir, 'manifest.json')
        if os.path.exists(manifest):
            self._log.debug('Reading manifest')
            self._manifest = json.loads(open(manifest, 'r').read())
            self._validate_manifest()
        else:
            raise RuntimeError('Application manifest not found')

    def _validate_manifest(self):
        '''
            Checks application manifest for required information

        '''
        try:
            assert 'application' in self._manifest.keys(), "No application specified"
            app = self._manifest['application']
            assert 'name' in app, "No application name specified"
            assert 'framework' in app, "No application framework specified"
            framework = app['framework']
            assert 'name' in framework, "No framework name specified"
            assert 'deployed_url' in app, "No deployed url specified"
            # shortcuts
            self._app_name = app['name']
            self._app_framework = framework
            self._deployed_url = app['deployed_url']
            self._app_dir = os.path.join(self._apps_root, self._app_name)
            self._ve_dir = os.path.join(self._ve_root, self._app_name)
        except AssertionError, e:
            raise RuntimeError('Invalid application manifest: {0}'.format(e))

    def _install_app(self):
        self._validate_manifest()
        if os.path.exists(self._app_dir):
            shutil.rmtree(self._app_dir)
        shutil.copytree(self._tmp_dir, self._app_dir)
        # set permissions
        user = app.config.get('APPLICATION_USER')
        for r,d,f in os.walk(self._app_dir):
            for x in d:
                if os.getuid() == 0:
                    os.chown(os.path.join(r, x), pwd.getpwnam(user).pw_uid, -1)
                os.chmod(os.path.join(r, x), 770)
            for x in f:
                if os.getuid() == 0:
                    os.chown(os.path.join(r, x), pwd.getpwnam(user).pw_uid, -1)
                os.chmod(os.path.join(r, x), 0660)

    def _install_virtualenv(self):
        self._log.debug('Installing virtualenv')
        self._log.debug(subprocess.Popen('virtualenv --no-site-packages {0}'.format(self._ve_dir), \
            shell=True, stdout=subprocess.PIPE).stdout.read())
        # install requirements
        cmd = '{0}/bin/pip install --use-mirrors -r {1}/requirements.txt'.format(self._ve_dir, self._app_dir)
        self._log.debug(subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE).stdout.read())

    def _generate_status(self, action=None, result=None):
        data = {
            'date': time.time(),
            'application': self._app_name,
            'action': action,
            'result': result,
        }
        return data

    def deploy(self, package=None):
        if not package:
            raise RuntimeError('You must specify a package')
        self._app_pkg = package
        self._unbundle()
        self._read_manifest()
        # install app
        self._install_app()
        # install ve
        self._install_virtualenv()
        # generate supervisor config
        containers = { 'wsgi': generate_uwsgi_config, }
        uwsgi_cfg = containers[self._app_framework.get('name')](app_name=self._app_name, \
            app_dir=self._app_dir,
            ve_dir=self._ve_dir,
            framework=self._app_framework,
            app_state_dir=self._app_state_dir)
        supervisor_cfg = os.path.join(self._supervisor_conf_dir, '{0}.conf'.format(self._app_name))
        open(supervisor_cfg, 'w').write(uwsgi_cfg)
        # update supervisor
        self._log.debug(subprocess.Popen('supervisorctl update', shell=True, stdout=subprocess.PIPE).stdout.read())
        # generate nginx config
        nginx_cfg = os.path.join(self._nginx_conf_dir, '{0}.conf'.format(self._app_name))
        cfg = generate_nginx_config(app_name=self._app_name, \
            deployed_url=self._deployed_url, app_state_dir=self._app_state_dir)
        open(nginx_cfg, 'w').write(cfg)
        self._log.debug(subprocess.Popen('service nginx reload', shell=True, stdout=subprocess.PIPE).stdout.read())
        return self._generate_status(action='deploy', result='ok')

    def delete(self):
        supervisor_cfg = os.path.join(self._supervisor_conf_dir, '{0}.conf'.format(self._app_name))
        if os.path.exists(supervisor_cfg):
            os.remove(supervisor_cfg)
        self._log.debug(subprocess.Popen('supervisorctl update', shell=True, stdout=subprocess.PIPE).stdout.read())
        nginx_cfg = os.path.join(self._nginx_conf_dir, '{0}.conf'.format(self._app_name))
        if os.path.exists(nginx_cfg):
            os.remove(nginx_cfg)
        self._log.debug(subprocess.Popen('service nginx reload', shell=True, stdout=subprocess.PIPE).stdout.read())
        if os.path.exists(self._app_dir):
            shutil.rmtree(self._app_dir)
        if os.path.exists(self._ve_dir):
            shutil.rmtree(self._ve_dir)
        return self._generate_status(action='delete', result='ok')
        
    def cleanup(self):
        self._log.debug('Cleaning up')
        shutil.rmtree(self._tmp_dir)

@task
def deploy_application(app_name=None, pkg=None):
    '''
        Wrapper function for async task
    '''
    application = Application(app_name)
    status = application.deploy(pkg)
    return status

@task
def delete_application(app_name=None):
    '''
        Wrapper function for async task
    '''
    application = Application(app_name)
    status = application.delete()
    return status

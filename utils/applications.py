import zipfile
import tempfile
import os
import shutil
import logging
import subprocess
try:
    import simplejson as json
except ImportError:
    import json
from utils import generate_uwsgi_config

class Application(object):
    '''
        Application

    '''
    def __init__(self, app_name=None, apps_root=None, ve_root=None, app_state_dir=None,\
        supervisor_conf_dir=None):
        self._app_pkg = None
        self._tmp_dir = tempfile.mkdtemp()
        if not apps_root or not ve_root or not app_state_dir or not supervisor_conf_dir:
            raise RuntimeError('You must specify an apps_root, ve_root, app_state_dir, and supervisor_conf_dir')
        self._apps_root = apps_root
        self._ve_root = ve_root
        self._app_state_dir = app_state_dir
        self._supervisor_conf_dir = supervisor_conf_dir
        self._manifest = None
        self._log = logging.getLogger('api')
        app_manifest = os.path.join(os.path.join(self._apps_root, app_name), 'manifest.json')
        # try to read existing manifest
        if os.path.exists(app_manifest):
            self._read_manifest(app_manifest)
        self._app_dir = os.path.join(self._apps_root, self._app_name)
        self._ve_dir = os.path.join(self._ve_root, self._app_name)

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
            assert 'container' in app, "No container specified"
            # shortcuts
            self._app_name = app['name']
            self._app_framework = framework
            self._app_container = app['container']
        except AssertionError, e:
            raise RuntimeError('Invalid application manifest: {0}'.format(e))

    def _install_app(self):
        if os.path.exists(self._app_dir):
            shutil.rmtree(self._app_dir)
        shutil.copytree(self._tmp_dir, self._app_dir)

    def _install_virtualenv(self):
        self._log.debug('Installing virtualenv')
        self._log.debug(subprocess.check_output('virtualenv --no-site-packages {0}'.format(self._ve_dir), shell=True))
        # install requirements
        cmd = '{0}/bin/pip install --use-mirrors -r {1}/requirements.txt'.format(self._ve_dir, self._app_dir)
        self._log.debug(subprocess.check_output(cmd, shell=True))

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
        containers = { 'uwsgi': generate_uwsgi_config, }
        cfg = containers[self._app_container](app_name=self._app_name, \
            app_dir=self._app_dir,
            ve_dir=self._ve_dir,
            framework=self._app_framework,
            app_state_dir=self._app_state_dir)
        supervisor_cfg = os.path.join(self._supervisor_conf_dir, '{0}.conf'.format(self._app_name))
        open(supervisor_cfg, 'w').write(cfg)
        return {'status': 'ok'}

    def delete(self):
        supervisor_cfg = os.path.join(self._supervisor_conf_dir, '{0}.conf'.format(self._app_name))
        if os.path.exists(supervisor_cfg):
            os.remove(supervisor_cfg)
        self._log.debug(subprocess.check_output('supervisorctl update', shell=True))
        if os.path.exists(self._app_dir):
            shutil.rmtree(self._app_dir)
        if os.path.exists(self._ve_dir):
            shutil.rmtree(self._ve_dir)
        return {'status': 'ok'}
        
    def cleanup(self):
        self._log.debug('Cleaning up')
        shutil.rmtree(self._tmp_dir)

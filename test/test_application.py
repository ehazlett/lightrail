import os
import unittest2
import sys
sys.path.append('../')
from application import app
import utils.applications
from utils.applications import Application
import tempfile
import shutil
from zipfile import ZipFile
from config import create_app

class ApplicationTestCase(unittest2.TestCase):
    @classmethod
    def setUpClass(self):
        # create app package
        pkg = ZipFile('test.zip', 'w')
        pkg.write('testapp/application.py', arcname='application.py')
        pkg.write('testapp/manifest.json', arcname='manifest.json')
        pkg.write('testapp/requirements.txt', arcname='requirements.txt')
        pkg.write('testapp/wsgi.py', arcname='wsgi.py')
        pkg.close()
        # run
        self.pkg = os.path.join(os.path.dirname('.'), 'test.zip')
        if not os.path.exists(self.pkg):
            raise RuntimeError('Error creating test package: {0}'.format(self.pkg))
        self.app = app.test_client()
        # monkey patch app to load custom test_settings
        utils.applications.app = create_app('test_settings')
        self.application = Application()
    
    def test___unbundle(self):
        self.application._app_pkg = self.pkg
        self.application._unbundle()
        self.assertNotEqual(len(os.listdir(self.application._tmp_dir)), 0)

    def test__read_manifest(self):
        self.application._read_manifest()
        self.assertNotEqual(self.application._manifest, None)

    def test__install_app(self):
        self.application._read_manifest()
        self.application._install_app()
        self.assertTrue(os.path.exists('tmp/apps/hellotest'))

    def test__install_virtualenv(self):
        self.application._read_manifest()
        self.application._install_virtualenv()
        self.assertTrue(os.path.exists('tmp/ve/hellotest'))

    @classmethod
    def tearDownClass(self):
        # cleanup
        self.application.cleanup()
        shutil.rmtree('tmp')
        os.remove('test.zip')

if __name__=='__main__':
    unittest2.main()

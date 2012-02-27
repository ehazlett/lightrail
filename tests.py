import os
import unittest
from utils.applications import Application
import tempfile
import shutil

class FrameworkTestCase(unittest.TestCase):
    def setUp(self):
        self.pkg = os.path.join(os.path.dirname('.'), 'test.zip')
        if not os.path.exists(self.pkg):
            raise RuntimeError('You must create or add the test package: {0}'.format(self.pkg))
        self.apps_root = os.path.join(tempfile.gettempdir(), 'apps')
        self.ve_root = os.path.join(tempfile.gettempdir(), 've')
        self.app_state_dir = os.path.join(tempfile.gettempdir(), 'app_state')
        if not os.path.exists(self.app_state_dir):
            os.makedirs(self.app_state_dir)
        self.supervisor_dir = os.path.join(tempfile.gettempdir(), 'svr')
        if not os.path.exists(self.supervisor_conf_dir):
            os.makedirs(self.supervisor_conf_dir)
        self.app = Application(self.pkg, apps_root=self.apps_root, ve_root=self.ve_root,\
            app_state_dir=self.app_state_dir, supervisor_conf_dir=self.supervisor_dir)

    def test_instantiate_app(self):
        self.assertNotEqual(self.app._manifest, None)

    def test_deploy(self):
        self.assertNotEqual(self.app.deploy(), None)

    def tearDown(self):
        self.app.cleanup()
        if os.path.exists(self.apps_root):
            shutil.rmtree(self.apps_root)
        if os.path.exists(self.ve_root):
            shutil.rmtree(self.ve_root)
        if os.path.exists(self.app_state_dir):
            shutil.rmtree(self.app_state_dir)
        #if os.path.exists(self.supervisor_dir):
        #    shutil.rmtree(self.supervisor_dir)

if __name__=='__main__':
    unittest.main()

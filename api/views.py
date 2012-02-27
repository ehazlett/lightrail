from flask import Blueprint
from flask import request, jsonify, session
from config import create_app
from decorators import api_key_required
import tempfile
from utils.applications import Application

app = create_app()
bp = api_blueprint = Blueprint('api', __name__)

def create_application(app_name=None):
    application = Application(app_name=app_name, apps_root=app.config.get('APPLICATIONS_ROOT'), \
        ve_root=app.config.get('VIRTUALENV_ROOT'), \
        app_state_dir=app.config.get('APPLICATION_STATE_DIR'), \
        supervisor_conf_dir=app.config.get('SUPERVISOR_CONF_DIR'))
    return application

@bp.route('')
def index():
    data = {
        'data': 'deploy',
    }
    return jsonify(data)
    
@bp.route('/deploy', methods=['POST'])
@api_key_required
def deploy():
    data = {}
    f = request.files['package']
    pkg = tempfile.mktemp()
    f.save(pkg)
    # create app and deploy
    application = create_application()
    status = application.deploy(pkg)
    return jsonify(status)

@bp.route('/delete/<app_name>')
@api_key_required
def delete(app_name=None):
    application = create_application(app_name)
    status = application.delete()
    return jsonify(status)

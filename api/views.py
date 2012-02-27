from flask import Blueprint
from flask import request, jsonify, session
from config import create_app
from decorators import api_key_required
import tempfile
from utils.applications import Application

app = create_app()
bp = api_blueprint = Blueprint('api', __name__)

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
    app_name = request.form.get('app', None)
    f = request.files['package']
    pkg = tempfile.mktemp()
    f.save(pkg)
    # create app and deploy
    application = Application(pkg, apps_root=app.config.get('APPLICATIONS_ROOT'), \
        ve_root=app.config.get('VIRTUALENV_ROOT'), \
        app_state_dir=app.config.get('APPLICATION_STATE_DIR'), \
        supervisor_conf_dir=app.config.get('SUPERVISOR_CONF_DIR'))
    status = application.deploy()
    return jsonify(status)

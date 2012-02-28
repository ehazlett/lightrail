from flask import Blueprint
from flask import request, jsonify, session, Response, json
from config import create_app, get_redis_connection
from decorators import api_key_required
import tempfile
from utils.applications import deploy_application, delete_application
import time

app = create_app()
bp = api_blueprint = Blueprint('api', __name__)
rds = get_redis_connection()

def generate_task_response(task_id=None):
    return jsonify({'status': 'ok', 'task_id': task_id})

def wait_for_task(task_id=None):
    key = '{0}:{1}'.format(app.config.get('TASK_QUEUE_NAME'), task_id)
    while True:
        try:
            if json.loads(rds.get(key))['status'] != 'running':
                break
        except:
            # if task hasn't started, the json.loads will fail because the task
            # data is still pickled from the queue
            pass
        time.sleep(1)
    return rds.get(key)

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
    res = deploy_application.delay(pkg=pkg)
    resp = generate_task_response(res.key)
    if request.args.get('wait'):
        resp = wait_for_task(res.key)
    return resp

@bp.route('/delete/<app_name>')
@api_key_required
def delete(app_name=None):
    res = delete_application.delay(app_name)
    resp = generate_task_response(res.key)
    if request.args.get('wait'):
        resp = wait_for_task(res.key)
    return resp

@bp.route('/status/<task_id>')
@api_key_required
def task_status(task_id=None):
    rds = get_redis_connection()
    v = rds.get('{0}:{1}'.format(app.config.get('TASK_QUEUE_NAME'), task_id))
    if not v:
        v = jsonify({'status': 'fail', 'result': 'invalid task'})
    return v

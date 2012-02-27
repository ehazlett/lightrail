from flask import Blueprint
from flask import request, jsonify, session
from config import create_app

bp = meta_blueprint = Blueprint('meta', __name__)

@bp.route('')
def index():
    data = {
        'data': 'meta',
    }
    return jsonify(data)
    

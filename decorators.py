#!/usr/bin/env python
from functools import wraps
from flask import g, session, redirect, url_for, request, current_app
from flask import json
from flask import jsonify
import messages

def api_key_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        api_key = None
        if 'apikey' in request.form:
            api_key = request.form['apikey']
        elif 'X-Api-Key' in request.headers.keys():
            api_key = request.headers['X-Api-Key']
        # validate
        if not api_key:
            data = {'error': messages.NO_API_KEY}
            return jsonify(data)
        if api_key not in current_app.config['API_KEYS']:
            data = {'error': messages.INVALID_API_KEY}
            return jsonify(data)
        return f(*args, **kwargs)
    return decorated

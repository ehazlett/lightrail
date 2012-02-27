from flask import request, redirect, url_for, session
from flask import jsonify
from config import create_app
# blueprints
from meta.views import meta_blueprint
from api.views import api_blueprint

app = create_app()
app.register_blueprint(meta_blueprint, url_prefix='/meta')
app.register_blueprint(api_blueprint, url_prefix='/api')

@app.route('/', methods=['GET'])
def index():
    data = {
        'name': app.config.get('APP_NAME'),
        'version': app.config.get('APP_VERSION'),
    }
    return jsonify(data)

if __name__=='__main__':
    app.run(host='0.0.0.0')


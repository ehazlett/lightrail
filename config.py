from flask import Flask

def create_app():
    app = Flask(__name__)
    app.config.from_object('settings')
    try:
        app.config.from_object('local_settings')
    except:
        pass
    return app


from flask import Flask
import redis

def create_app(config_module=None):
    app = Flask(__name__)
    if not config_module:
        config_module = 'settings'
    app.config.from_object(config_module)
    return app

def get_redis_connection():
    app = create_app()
    return redis.Redis(host=app.config.get('REDIS_HOST', 'localhost'), \
        port=app.config.get('REDIS_PORT', 6379), db=app.config.get('REDIS_DB', 0), \
        password=app.config.get('REDIS_PASSWORD', None))


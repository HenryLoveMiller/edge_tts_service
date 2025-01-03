# app/__init__.py
from flask import Flask
from config import config

def create_app(config_name):
    app = Flask(__name__)
    app.config.from_object(config[config_name])

    # Register blueprint
    from app.api import api as api_blueprint
    app.register_blueprint(api_blueprint)

    # Register player route without prefix
    from app.api.routes import play_audio
    app.add_url_rule('/player', view_func=play_audio)

    return app

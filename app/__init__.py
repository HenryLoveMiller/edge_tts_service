# app/__init__.py
from flask import Flask
from config import config
import os

def create_app(config_name):
    app = Flask(__name__)
    app.config.from_object(config[config_name])

    # Serve static files
    static_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static')
    if not os.path.exists(static_dir):
        os.makedirs(static_dir)
    app.config['UPLOAD_FOLDER'] = static_dir
    app.static_folder = static_dir

    # 注册蓝图
    from app.api import api as api_blueprint
    app.register_blueprint(api_blueprint, url_prefix='/api/v1')

    return app

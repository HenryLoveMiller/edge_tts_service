# config.py
import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev')
    TEMP_FILE_DIR = os.getenv('TEMP_FILE_DIR', '/tmp')
    MAX_CONTENT_LENGTH = 5 * 1024 * 1024  # 5MB
    BASE_URL = os.getenv('BASE_URL')
    GITHUB_TOKEN = os.getenv('GITHUB_TOKEN')
    GITHUB_REPO = os.getenv('GITHUB_REPO')
    GITHUB_BRANCH = os.getenv('GITHUB_BRANCH', 'main')
    GITHUB_FOLDER = os.getenv('GITHUB_FOLDER', '')
    LOCAL_STORAGE_DIR = os.getenv('LOCAL_STORAGE_DIR', '/app/audio_files')
    STORAGE_METHOD = os.getenv('STORAGE_METHOD', 'local')

class DevelopmentConfig(Config):
    DEBUG = True
    BASE_URL = os.getenv('BASE_URL', 'http://localhost:5000')

class ProductionConfig(Config):
    DEBUG = False
    BASE_URL = os.getenv('BASE_URL', 'https://production.example.com')

config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}
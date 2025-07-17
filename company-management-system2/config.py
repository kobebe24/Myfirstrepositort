# config.py
import os

class Config:
    SECRET_KEY = os.getenv('SECRET_KEY', 'default_secret_key')
    SQLALCHEMY_DATABASE_URI = os.getenv('SQLALCHEMY_DATABASE_URI', 'sqlite:///company_management.db')  # 默认使用 SQLite（仅用于开发）
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    DEBUG = bool(os.getenv('DEBUG', True))
    LOGIN_VIEW = 'login'

class DevelopmentConfig(Config):
    DEBUG = True

class ProductionConfig(Config):
    DEBUG = False

config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig
}
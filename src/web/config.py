import os
from datetime import timedelta

class Config:
    basedir = os.path.abspath(os.path.dirname(__file__))  # Get the absolute directory path
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'your-secret-key'
    
    # Updated to use an absolute path
    SQLALCHEMY_DATABASE_URI = f'sqlite:///{os.path.join(basedir, "instance", "meraki_health_check.db")}'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # JWT configuration
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY') or 'your-jwt-secret-key'
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=1)

    # Celery configuration
    CELERY_BROKER_URL = 'redis://localhost:6379/0'
    CELERY_RESULT_BACKEND = 'redis://localhost:6379/0'
    
    # Email configuration
    MAIL_SERVER = os.environ.get('MAIL_SERVER', 'smtp.googlemail.com')
    MAIL_PORT = int(os.environ.get('MAIL_PORT', '587'))
    MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS', 'true').lower() in ['true', 'on', '1']
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    MAIL_DEFAULT_SENDER = os.environ.get('MAIL_DEFAULT_SENDER', 'noreply@merakihealthcheck.com')

    @staticmethod
    def init_app(app):
        pass

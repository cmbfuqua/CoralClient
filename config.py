import os
from urllib.parse import quote

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev_fallback_secret_key'
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    GOOGLE_APPLICATION_CREDENTIALS = os.environ.get('GOOGLE_APPLICATION_CREDENTIALS', 'corals4cheap-65a82a68dbed.json')

    UPLOAD_FOLDER = os.environ.get('UPLOAD_FOLDER', '/data')
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

    MAIL_SERVER = os.environ.get('MAIL_SERVER', 'smtp.gmail.com')
    MAIL_PORT = int(os.environ.get('MAIL_PORT', 587))
    MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS', 'True') == 'True'
    MAIL_USE_SSL = os.environ.get('MAIL_USE_SSL', 'False') == 'True'
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    MAIL_DEFAULT_SENDER = os.environ.get('MAIL_DEFAULT_SENDER', MAIL_USERNAME)

    RECAPTCHA_PUBLIC_KEY = os.environ.get('RECAPTCHA_PUBLIC_KEY')
    RECAPTCHA_PRIVATE_KEY = os.environ.get('RECAPTCHA_PRIVATE_KEY')

    SQLALCHEMY_ENGINE_OPTIONS = {
        "pool_size": int(os.environ.get('DB_POOL_SIZE', 10)),
        "pool_recycle": int(os.environ.get('DB_POOL_RECYCLE', 1800)),
        "max_overflow": int(os.environ.get('DB_MAX_OVERFLOW', 20)),
    }

class DevConfig(Config):
    SQLALCHEMY_DATABASE_URI = os.environ.get('DEV_DATABASE_URL') or 'sqlite:///dev_database.db'
    DEBUG = True

class ProdConfig(Config):
    username = os.environ.get('DB_USER', 'root')
    password = quote(os.environ.get('DB_PASS', '')) if os.environ.get('DB_PASS') else ''
    database = os.environ.get('DB_NAME', 'CoralClientSeller')
    instance_connection_name = os.environ.get('INSTANCE_CONNECTION_NAME', '')
    
    if instance_connection_name:
        SQLALCHEMY_DATABASE_URI = f"mysql+pymysql://{username}:{password}@/{database}?unix_socket=/cloudsql/{instance_connection_name}"
    else:
        db_host = os.environ.get('DB_HOST', '127.0.0.1')
        db_port = os.environ.get('DB_PORT', '3306')
        SQLALCHEMY_DATABASE_URI = f"mysql+pymysql://{username}:{password}@{db_host}:{db_port}/{database}"

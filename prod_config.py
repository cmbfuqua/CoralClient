from base_config import Config
from urllib.parse import quote
import os

class ProdConfig(Config):
    username = os.environ.get('DB_USER', 'root')
    password = quote(os.environ.get('DB_PASS', '')) if os.environ.get('DB_PASS') else ''
    database = os.environ.get('DB_NAME', 'CoralClientSeller')
    instance_connection_name = os.environ.get('INSTANCE_CONNECTION_NAME', '')
    
    if instance_connection_name:
        prod = f"mysql+pymysql://{username}:{password}@/{database}?unix_socket=/cloudsql/{instance_connection_name}"
    else:
        # Fallback to standard host/port if not using Cloud SQL unix socket
        db_host = os.environ.get('DB_HOST', '127.0.0.1')
        db_port = os.environ.get('DB_PORT', '3306')
        prod = f"mysql+pymysql://{username}:{password}@{db_host}:{db_port}/{database}"

    SQLALCHEMY_DATABASE_URI = prod

from base_config import Config

class DevConfig(Config):
    # Use SQLite for local development (no MySQL installation required)
    SQLALCHEMY_DATABASE_URI = 'sqlite:///dev_database.db'
    DEBUG = True

import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_wtf.csrf import CSRFProtect
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

from dev_config import DevConfig
from prod_config import ProdConfig

app = Flask(__name__)

if os.environ.get('FLASK_ENV') == 'production':
    app.config.from_object(ProdConfig)
else:
    app.config.from_object(DevConfig)

db = SQLAlchemy(app)
csrf = CSRFProtect(app)
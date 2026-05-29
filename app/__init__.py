import os
from flask import Flask
from .extensions import db, mail, bcrypt, login_manager, csrf
from dotenv import load_dotenv

# Load environment variables early
load_dotenv()

def create_app(config_class=None):
    app = Flask(__name__)

    # Default configuration
    if config_class is None:
        from config import Config
        if os.environ.get('FLASK_ENV') == 'production':
            from config import ProdConfig
            app.config.from_object(ProdConfig)
        else:
            from config import DevConfig
            app.config.from_object(DevConfig)
    else:
        app.config.from_object(config_class)

    # Initialize extensions
    db.init_app(app)
    mail.init_app(app)
    bcrypt.init_app(app)
    login_manager.init_app(app)
    csrf.init_app(app)

    login_manager.login_view = 'auth.login'

    from .models import User

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    # Register Blueprints
    from .auth import auth_bp
    app.register_blueprint(auth_bp)

    from .catalog import catalog_bp
    app.register_blueprint(catalog_bp)

    from .admin import admin_bp
    app.register_blueprint(admin_bp)

    from .main import main_bp
    app.register_blueprint(main_bp)

    from .billing import billing_bp
    app.register_blueprint(billing_bp)

    return app

import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_cors import CORS
from datetime import datetime

db = SQLAlchemy()
login_manager = LoginManager()

def create_app():
    app = Flask(__name__, static_folder='static', template_folder='templates')

    # Secret key
    app.config['SECRET_KEY'] = os.environ.get('PCMAMS_SECRET', 'dev-secret-change-me')

    # Database config
    app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:reethu%40123@localhost/pcmams'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # GLOBAL YEAR IN TEMPLATES
    @app.context_processor
    def inject_year():
        return {'current_year': datetime.now().year}

    # Extensions
    CORS(app)
    db.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'

    # Blueprints
    from .auth import auth_bp
    from .main import main_bp
    from .api import api_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(main_bp)
    app.register_blueprint(api_bp, url_prefix='/api')

    # Create DB
    with app.app_context():
        from . import models
        db.create_all()

    return app

"""
SmartBEP Application Package
=============================
Flask application factory and initialization.
"""

import os
from flask import Flask, redirect, url_for
from flask_login import LoginManager
from flask_wtf.csrf import CSRFProtect

from config import config_by_name


def create_app(config_name: str = None) -> Flask:
    """
    Application factory.
    Creates and configures the Flask app instance.
    """
    if config_name is None:
        config_name = os.environ.get('FLASK_ENV', 'development')

    app = Flask(__name__,
                template_folder='templates',
                static_folder='static')
    app.config.from_object(config_by_name.get(config_name, config_by_name['development']))

    # Ensure data directory exists
    data_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data')
    os.makedirs(data_dir, exist_ok=True)
    os.makedirs(app.config.get('MODEL_DIR', os.path.join(data_dir, 'models')), exist_ok=True)

    # Initialize extensions
    _init_extensions(app)

    # Register blueprints
    _register_blueprints(app)

    # Setup logging
    _setup_logging(app)

    # Register root redirect
    @app.route('/')
    def root():
        return redirect(url_for('dashboard.index'))

    return app


def _init_extensions(app: Flask):
    """Initialize Flask extensions."""
    from app.models.database import db

    db.init_app(app)

    # CSRF Protection
    csrf = CSRFProtect()
    csrf.init_app(app)

    # Login Manager
    login_manager = LoginManager()
    login_manager.login_view = 'auth.login'
    login_manager.login_message_category = 'info'
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(user_id):
        from app.models.user import User
        return User.query.get(int(user_id))

    # Create tables
    with app.app_context():
        db.create_all()


def _register_blueprints(app: Flask):
    """Register all route blueprints."""
    from app.routes.auth import auth_bp
    from app.routes.dashboard import dashboard_bp
    from app.routes.projects import projects_bp
    from app.routes.reports import reports_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(projects_bp)
    app.register_blueprint(reports_bp)


def _setup_logging(app: Flask):
    """Configure application logging."""
    from app.utils.logger import setup_logging
    if not app.testing:
        setup_logging(app)

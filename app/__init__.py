"""
app/__init__.py
====================================
Create our application
"""
import sentry_sdk
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_wtf.csrf import CSRFProtect
from flask_cors import CORS
from flask_mongoengine import MongoEngine
from flask_pymongo import PyMongo
from config import app_config
from sentry_sdk.integrations.flask import FlaskIntegration

# DEVELOPERS-NOTE: -INCLUDE YOUR IMPORTS HERE-

#                  -END-

db = MongoEngine()
mongo = PyMongo()
migrate = Migrate()
csrf = CSRFProtect()
cors = CORS()
login_manager = LoginManager()

# DEVELOPERS-NOTE: -INITIATE YOUR IMPORTS HERE-

#                   -END-


MODULES = []

CONTEXT = {
    'system_modules': []
}

# SECRETARYREFERENCE = None


def internal_server_error(e):
    from flask import render_template
    return render_template('admin/internal_server_error.html'), 500


def create_app(config_name):
    """
    Return the app at crenecreate nito ang application
    ----------
    config_name
        A string para kung ano ang gagamiting environment configuration(eg.develop,production,testing)
    """
    app = Flask(__name__, instance_relative_config=False)
    app.config.from_object(app_config[config_name])
    app.register_error_handler(500, internal_server_error)

    db.init_app(app)
    mongo.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    cors.init_app(app)
    csrf.init_app(app)
    
    sentry_sdk.init(
        dsn="https://9cf2405303714b4b873f1f6c0e28eed3@o4503912449245184.ingest.sentry.io/4503912450424832",
        integrations=[
            FlaskIntegration(),
        ],
        traces_sample_rate=1.0,
    )

    # DEVELOPERS-NOTE: -INITIALIZE YOUR IMPORTS HERE-

    #                    -END-

    login_manager.login_view = 'bp_auth.login'
    login_manager.login_message = "You must be logged in to access this page."

    print("CURRENT ENVIRONMENT: ", app.config['ENV'])
    print("CURRENT DATABASE: ", app.config['MONGO_URI'])

    with app.app_context():

        # DEVELOPERS-NOTE: -IMPORT HERE THE SYSTEM MODULES-
        from app.core import bp_core
        from app.auth import bp_auth
        from app.admin import bp_admin
        from prime_admin import bp_lms
        from prime_home import bp_prime_home
        from api import bp_api
        #                   -END-

        # DEVELOPERS-NOTE: -REGISTER HERE THE MODULE BLUEPRINTS-
        app.register_blueprint(bp_core, url_prefix='/')
        app.register_blueprint(bp_auth, url_prefix='/auth')
        app.register_blueprint(bp_admin, url_prefix='/admin')
        app.register_blueprint(bp_lms, url_prefix='/learning-management')
        app.register_blueprint(bp_prime_home, url_prefix='/home')
        app.register_blueprint(bp_api, url_prefix='/api')
        #               -END-

        # DEVELOPERS-NOTE: -INCLUDE HERE YOUR MODULE Admin models FOR ADMIN TEMPLATE-
        from app.admin.admin import AdminModule
        from app.auth.auth import AuthModule
        from prime_home.prime_home import PrimeHomeModule
        #                  -END-
        
        # DEVELOPERS-NOTE: -APPEND YOUR MODULE HERE-
        MODULES.append(AdminModule)
        MODULES.append(AuthModule)
        MODULES.append(PrimeHomeModule)
        #                  -END-

        # Load CONTEXT data
        CONTEXT['header_color'] = 'header_color15' # Default color
        CONTEXT['sidebar_color'] = "sidebar_color15" # Default color
    
    @app.context_processor
    def inject_debug():
        return dict(debug=app.debug)

    return app

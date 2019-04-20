import os
import click
from environs import Env
from flask import Flask
from flask import render_template
from flask import session
from flask import redirect
from serafim.config import APP_SECRET

def create_app(test_config=None):
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY=APP_SECRET
    )

    # if test_config is None:
    #     # It probably fail, but it must shut up!!
    #     app.config.from_pyfile('config.py', silent=True)
    # else:
    #     app.config.from_mapping(test_config)

    try:
        # Ensure instance path exists
        os.makedirs(app.instance_path)
    except OSError:
        # So it already exists... do nothing
        pass

    # Register db session hook, and db seed command
    from .model import init_app
    model.init_app(app)

    from serafim.admin import admin_blueprint
    app.register_blueprint(admin_blueprint)

    from serafim.user import user_blueprint
    app.register_blueprint(user_blueprint)

    #
    # # Register auth blueprint
    from serafim.auth import auth_blueprint
    app.register_blueprint(auth_blueprint)
    #
    # # Register auth blueprint
    # from .routes import api
    # app.register_blueprint(api.api)
    #
    # from .routes import admin
    # app.register_blueprint(admin.admin)
    #
    # from .routes import user
    # app.register_blueprint(user.user_bp)

    return app
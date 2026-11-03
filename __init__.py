"""Smart Job Application Tracker with Resume Analyzer."""

import os

from flask import Flask

from . import api, database, views


def create_app(test_config=None):
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY=os.environ.get("SECRET_KEY", "dev-change-me"),
        DATABASE=os.path.join(app.instance_path, "tracker.sqlite"),
        MAX_CONTENT_LENGTH=5 * 1024 * 1024,  # 5 MB upload limit
    )
    if test_config:
        app.config.update(test_config)

    os.makedirs(app.instance_path, exist_ok=True)
    database.init_app(app)

    app.register_blueprint(views.bp)
    app.register_blueprint(api.bp)
    return app

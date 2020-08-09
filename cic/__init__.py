from flask import Flask, g
from flask_sqlalchemy import SQLAlchemy
from flask_script import Manager
from flask_migrate import Migrate, MigrateCommand
import psycopg2
import logging
from flask_login import LoginManager
from flask_scss import Scss
from flaskext.markdown import Markdown
from markdown.extensions.fenced_code import FencedCodeExtension
from markdown.extensions.tables import TableExtension
from markdown.extensions.codehilite import CodeHiliteExtension
from flask_pagedown import PageDown


# Globally accessible libraries
db = SQLAlchemy()
login_manager = LoginManager()



def create_app():
    """Initialize the core application."""
    app = Flask(__name__, instance_relative_config=False)
    logging.basicConfig(level=logging.DEBUG)
    app.config.from_object('config.Config')


    db.init_app(app)
    login_manager.init_app(app)

    Scss(app)
    Markdown(app, extensions=['fenced_code', 'tables', 'codehilite'])
    pagedown = PageDown(app)

    migrate = Migrate(app, db, compare_type=True)
    manager = Manager(app)
    manager.add_command('db', MigrateCommand)




    with app.app_context():
        from cic.admin.app import admin
        from cic.api.app import api
        from cic.frontend.app import frontend

        # Register Blueprints
        app.register_blueprint(admin, url_prefix='/admin')
        app.register_blueprint(api, url_prefix='/api')
        app.register_blueprint(frontend)



        # Create tables for our models
        db.create_all()

        if db.engine.url.drivername == 'sqlite':
            migrate.init_app(app, db, render_as_batch=True)
        else:
            migrate.init_app(app, db)


        return app

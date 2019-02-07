from logging.config import dictConfig

from flask_migrate import Migrate
from flask_principal import Principal, identity_loaded
from flask_sqlalchemy import SQLAlchemy
import connexion

from config import config
from app.helpers.celery import Celery
from app.hacks import CustomResponseValidator
from app.middleware.debug import debug_request, debug_response
from app.middleware.gdpr import log_request
from app.middleware.headers import HttpHostHeaderMiddleware
from app.security import load_identity


# Common objects usable across the application
db = SQLAlchemy()
migrate = Migrate()
celery = Celery()
principal = Principal(use_sessions=False)


def create_app(config_name=None):
    # Use connexion to create and configure the initial application, but
    # we will use the Flask application to configure the rest
    connexion_app = connexion.App(__name__)
    flask_app = connexion_app.app
    # Update configuration according to the factory parameter or the FLASK_ENV
    # variable
    config_obj = config.get(config_name or flask_app.env)
    if config_obj is None:
        raise ValueError(f'Unknown configuration "{config_name}"')
    flask_app.config.from_object(config_obj)

    # Configure logging from the configuration object: I refuse to have the
    # logging configuration in another file (it's easier to manage)
    if 'LOGGING' in flask_app.config and flask_app.config['LOGGING']:
        dictConfig(flask_app.config['LOGGING'])

    # Database
    db.init_app(flask_app)
    migrate.init_app(flask_app, db)

    # Celery (background tasks)
    flask_app.config['CELERY_BROKER_URL'] = flask_app.config['CELERY']['broker_url']
    celery.init_app(flask_app)
    # This is needed if flask-celery-helper is used instead of the
    # custom made Celery object in the app/helpers/celery.py helper script
    # celery.conf.update(flask_app.config['CELERY'])

    # Make configured Celery instance attach to Flask
    flask_app.celery = celery

    # APIs
    connexion_app.add_api('../openapi.yaml', strict_validation=True, validate_responses=True,
                          validator_map={'response': CustomResponseValidator})

    # Principals
    principal.init_app(flask_app)
    identity_loaded.connect_via(flask_app)(load_identity)

    # Command-line interface tools
    from .cli import data_cli, role_cli, user_cli
    flask_app.cli.add_command(data_cli)
    flask_app.cli.add_command(role_cli)
    flask_app.cli.add_command(user_cli)

    # Flask shell configuration
    from app.models import (
        User, Role,
        Metadata, Family, MetadataQuery, QueryDialect, Workspace, WorkspaceState
    )

    @flask_app.shell_context_processor
    def make_shell_context():
        return {
            # Handy reference to the database
            'db': db,
            # Add models here
            'User': User,
            'Role': Role,
            'Metadata': Metadata,
            'Family': Family,
            'MetadataQuery': MetadataQuery,
            'QueryDialect': QueryDialect,
            'Workspace': Workspace,
            'WorkspaceState': WorkspaceState,
        }

    # Request/response logging
    # GDPR logging
    flask_app.before_request(log_request)

    # Debugging of requests and responses
    if flask_app.debug:
        flask_app.before_request(debug_request)
        flask_app.after_request(debug_response)

    # Other middleware
    proxied = HttpHostHeaderMiddleware(flask_app.wsgi_app, server=flask_app.config['SERVER_NAME'])
    flask_app.wsgi_app = proxied

    return flask_app

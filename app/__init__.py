from logging.config import dictConfig

from celery import Celery
from flask.cli import AppGroup
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
import connexion

from config import config


# Celery helper for configuration,
# taken from http://flask.pocoo.org/docs/1.0/patterns/celery/
def make_celery(app):
    celery_obj = Celery(
        app.import_name,
        broker=app.config['CELERY_BROKER_URL'],
        backend=app.config['CELERY_RESULT_BACKEND'],
        include=['app.api.data.tasks'],
    )
    celery_obj.conf.update(app.config)

    # Replace the base parent task with a task that has the application context
    BaseTask = celery_obj.Task

    class ContextBaseTask(BaseTask):
        abstract = True

        def __call__(self, *args, **kwargs):
            with app.app_context():
                return self.run(*args, **kwargs)

    celery_obj.Task = ContextBaseTask
    return celery_obj


# Application is initialized by connexion. Note that connexion is not a Flask
# extension; it wraps the Flask application entirely. The Flask application is
# accesible through app.app
app = connexion.App(__name__)
application = app.app
application.config.from_object(config.get(application.env))

# Logging
dictConfig(application.config['LOGGING'])

# Database
db = SQLAlchemy(application)
migrate = Migrate(application, db)

# Background tasks
celery = make_celery(application)

# APIs
app.add_api('../openapi.yaml', strict_validation=True, validate_responses=True)

# Command line tools
from app.api.data.commands import init_buckets  # nopep8

data_cli = AppGroup('data')


@data_cli.command('init')
def data_init_command():
    """ Initialize data buckets """
    init_buckets()


application.cli.add_command(data_cli)

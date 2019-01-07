import os

# TODO: consider / add dot_env and load_dotenv
basedir = os.path.abspath(os.path.dirname(__file__))


class Config:
    # General Flask configuration
    DEBUG = False
    TESTING = False
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'some-secret-key'

    # Logging
    LOG_DIR = os.environ.get('LOG_DIR') or os.path.join(basedir, 'logs')
    LOGGING = {
        'version': 1,
        'formatters': {
            'default': {
                'format': '%(levelname)s %(asctime)s %(message)s',
                'datefmt': '%Y-%m-%d %H:%M:%S',
            },
            'detailed': {
                'format': '%(asctime)s %(levelname)s %(name)s.%(funcName)s:- %(message)s '
                          '[in %(pathname)s:%(lineno)d]',
                'datefmt': '%Y-%m-%d %H:%M:%S',
            },
            # A formatter for celery tasks that includes task_name and task_id
            'celery_formatter': {
                '()': 'celery.app.log.TaskFormatter',
                'format': '%(levelname)s %(asctime)s [%(task_name)s(%(task_id)s)] '
                          '%(name)s.%(funcName)s:%(lineno)s- %(message)s',
            }
        },
        'handlers': {
            # The default logging on console
            'console': {
                'level': 'INFO',  # on info so that the console is rather brief
                'class': 'logging.StreamHandler',
                'formatter': 'default',
            },
            # A more detailed logging file for debugging
            'file': {
                'level': 'DEBUG',  # on debug so that the file has much more details
                'class': 'logging.handlers.RotatingFileHandler',
                'formatter': 'detailed',
                'filename': os.path.join(LOG_DIR, 'quetzal.log'),
                'maxBytes': 10 * (1 << 20),  # 10 Mb
                'backupCount': 100,
            },
            # A separate logging file for the celery tasks
            'file_worker': {
                'level': 'DEBUG',  # like the file handler but on another file
                'class': 'logging.handlers.RotatingFileHandler',
                'formatter': 'celery_formatter',
                'filename': os.path.join(LOG_DIR, 'worker.log'),
                'maxBytes': 10 * (1 << 20),  # 10 Mb
                'backupCount': 100,
            },
            # TODO: add email handler for errors
        },
        'loggers': {
            'app.api.data.tasks': {
                'level': 'DEBUG',
                'handlers': ['file_worker']
            }
        },
        'root': {
            'level': 'DEBUG',  # on debug so that the file has all details
            'handlers': ['console', 'file'],
        },
        'disable_existing_loggers': True,
    }

    # Database configuration
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        f'sqlite:///{os.path.join(basedir, "app.db")}'
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Celery configuration
    # Note that from Celery 4.0, configuration keys are in lowercase. This is
    # why the Celery configuration is set in this inner dictionary
    CELERY = {
        'broker_url': 'amqp://guest:guest@rabbitmq:5672//',
        'result_backend': 'rpc://',
        # 'worker_log_format': LOGGING['formatters']['default']['format'],
        # 'worker_task_log_format': LOGGING['formatters']['celery_tasks']['format'],
        'worker_hijack_root_logger': False,
    }

    # Quetzal-specific configuration
    QUETZAL_GCP_CREDENTIALS = os.environ.get('QUETZAL_APP_CREDENTIALS') or \
        os.path.join(basedir, 'conf', 'credentials.json')
    QUETZAL_GCP_DATA_BUCKET = os.environ.get('QUETZAL_GCP_DATA_BUCKET') or \
        'gs://quetzal-dev-data'


class DevelopmentConfig(Config):
    DEBUG = True
    JSON_SORT_KEYS = False


class TestConfig(Config):
    TESTING = True

    # Database configuration (in-memory database)
    SQLALCHEMY_DATABASE_URI = 'sqlite://'


class ProductionConfig(Config):
    pass


# Map of environment name -> configuration object
config = {
    'development': DevelopmentConfig,
    'testing': TestConfig,
    'production': ProductionConfig,
    'default': Config,
}

import os
from datetime import timedelta

sqlalchemy_echo = os.getenv('SQLALCHEMY_ECHO') == 'true'

class BaseConfig(object):
    CONFIGURATION_NAME = "baseconfig"
    HTTP_ADDRESS = "http://127.0.0.1:5000"
    ADMINS = ["william.aaron@cfa.harvard.edu"]
    TEST_NOTIFICATIONS = True
    TEST_DATABASE = True
    #
    # --- Database and CSRF secret key
    #
    SECRET_KEY = 'secret_key_for_test'
    #
    # --- SQLAlchemy
    #
    SQLALCHEMY_DATABASE_URI = "sqlite:///test_usint.db"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {'echo': sqlalchemy_echo}
    #
    # --- Session Settings
    #
    PERMANENT_SESSION_LIFETIME = timedelta(minutes=60)
    SESSION_REFRESH_EACH_REQUEST = True
    SESSION_TYPE = 'sqlalchemy' #: Must set SQLAlchemy instance for session once database connection is instantiated
    #
    # --- Directory Pathing
    #
    OBS_SS = "/data/mta4/obs_ss/"

class LocalHostConfig(BaseConfig):
    CONFIGURATION_NAME = "localhost"

class CXCWebConfig(BaseConfig):
    CONFIGURATION_NAME = "cxcweb"
    HTTP_ADDRESS = "https://cxc.cfa.harvard.edu/wsgi/cus/usint"
    SQLALCHEMY_DATABASE_URI = "sqlite:///usint.db"
    TEST_NOTIFICATIONS = False
    TEST_DATABASE = False

_CONFIG_DICT = {
    'localhost': LocalHostConfig,
    'cxcweb': CXCWebConfig,
    'baseconfig': BaseConfig
}
import os
basedir = os.path.abspath(os.path.dirname(__file__))

password = ''

class Config(object):
    SECRET_KEY = os.urandom(24)
    SQLALCHEMY_DATABASE_URI = 'postgresql://phil:' + password
        + 'cparuupfbjxx.us-west-2.rds.amazonaws.com/phil_app'

# flask-login uses sessions which require a secret Key
    SQLALCHEMY_TRACK_MODIFICATIONS = True

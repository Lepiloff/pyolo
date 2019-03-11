import os


class Configuration(object):
    DEBUG = True
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'e5ac358c-f0bf-11e5-9e39-d3b532c10a28'
    REDIS_URL = os.environ.get('REDIS_URL') or 'redis://'

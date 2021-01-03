import os

class AWSConfig:
    S3_LINK = "https://{}.s3.amazonaws.com".format(os.environ['S3_BUCKET'])
    AWS_ACCESS_KEY_ID = os.environ['AWS_ACCESS_KEY_ID']
    AWS_SECRET_ACCESS_KEY = os.environ['AWS_SECRET_ACCESS_KEY']
    S3_BUCKET = os.environ['S3_BUCKET']

class PayPalConfig:
    PAYPAL_MODE = os.environ['PAYPAL_MODE']
    PAYPAL_CLIENT_ID = os.environ['PAYPAL_CLIENT_ID']
    PAYPAL_CLIENT_SECRET = os.environ['PAYPAL_CLIENT_SECRET']
    PAYPAL_IPN_INACTIVE = True

class SiteConfig:
    ADMIN_LIST = [
        'abalogun316@gmail.com',
        'adb2189@columbia.edu'
        ]
    BUSINESS_EMAIL = os.environ['BUSINESS_EMAIL']

class GoogleOAuth:
    GOOGLE_CLIENT_ID = os.environ.get("GOOGLE_CLIENT_ID", None)
    GOOGLE_CLIENT_SECRET = os.environ.get("GOOGLE_CLIENT_SECRET", None)
    GOOGLE_DISCOVERY_URL = (
        "https://accounts.google.com/.well-known/openid-configuration"
        )

class Config(object):
    #DB and Session configurations
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_DATABASE_URI = 'sqlite:///schema.db'

    FLASK_DEBUG = True
    TESTING  =  False

class ProductionConfig(Config):
    FLASK_DEBUG = False

    #DB and Session configurations
    SQLALCHEMY_DATABASE_URI = os.environ['DATABASE_URL']
    SECRET_KEY = os.environ['SECRET_KEY']

class DevelopmentConfig(Config):
    FLASK_DEBUG = os.environ['FLASK_DEBUG']
    SECRET_KEY = os.environ['SECRET_KEY']
    TESTING = True

class TestingConfig(Config):
    TESTING = True
    SECRET_KEY = os.environ['SECRET_KEY']

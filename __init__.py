import boto3

from flask import Flask
from flask_bootstrap import Bootstrap

from support.config import DevelopmentConfig, ProductionConfig, TestingConfig
from support.extensions import aws

#Create Flask object
def create_app(config_object=DevelopmentConfig()):
    app = Flask(__name__)
    app.config.from_object(config_object)

    s3 = boto3.client('s3',
                aws_access_key_id=aws.AWS_ACCESS_KEY_ID,
                aws_secret_access_key=aws.AWS_SECRET_ACCESS_KEY)

    from flask_bootstrap import Bootstrap
    Bootstrap(app)

    from support.login import login_manager
    login_manager.init_app(app)

    from support.models import db
    db.init_app(app)

    from views.auth import bp as auth
    from views.shop import bp as shop
    from views.admin import bp as admin
    app.register_blueprint(auth)
    app.register_blueprint(shop)
    app.register_blueprint(admin)
    return app

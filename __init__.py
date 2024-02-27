import os
import logging
from flask import Flask
from flask_cors import CORS
from flask_mailman import Mail
from flask_security import SQLAlchemySessionUserDatastore, Security
from dotenv import load_dotenv
from linuxlab.db import db
from linuxlab.routes.player import pages as player
from linuxlab.routes.admin import pages as admin
from linuxlab.models import PlayerModel, RoleModel
from linuxlab.forms import SigninForm
from datetime import timedelta
import MySQLdb

load_dotenv()


def create_app():

    app = Flask(__name__)
    mail = Mail()
    security = Security()
    CORS(app)
    app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("SQLALCHEMY_DATABASE_URI")
    app.config["SECRET_KEY"] = os.environ.get(
        "SECRET_KEY", "4390065a5b4ae483c59aed71ae9693f15bba815fe5c9153f19b24c1436949e25"
    )
    app.config["SECURITY_PASSWORD_SALT"] = os.environ.get(
        "SECURITY_PASSWORD_SALT",
        "w7F4eyAgSOsAs0t0JnLrVru7WhXWcs9hpCkzxfYHVP5owg29rgKhzbM",
    )
    app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(days=1)
    app.config["MAIL_SERVER"] = os.getenv("MAIL_SERVER")
    app.config["MAIL_PORT"] = os.getenv("MAIL_PORT")
    app.config["MAIL_USERNAME"] = os.getenv("MAIL_USERNAME")
    app.config["MAIL_PASSWORD"] = os.environ.get("MAIL_PASSWORD", "dzbpgapjbivtwlgb")
    app.config['MAIL_USE_TLS'] = False
    app.config['MAIL_USE_SSL'] = True
    app.config["SECURITY_CONFIRMABLE"] = True

    db.init_app(app)
    mail.init_app(app)
    user_datastore = SQLAlchemySessionUserDatastore(db.session, PlayerModel, RoleModel)
    security.init_app(app, user_datastore, login_form=SigninForm)
    

    logging.basicConfig()
    logging.getLogger("sqlalchemy.engine").setLevel(logging.INFO)
    logging.getLogger("sqlalchemy.pool").setLevel(logging.DEBUG)

    app.register_blueprint(admin)
    app.register_blueprint(player)
    return app
# coding:utf8

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import os

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "mysql://root:123456@localhost:3306/movie"

app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = True

db = SQLAlchemy(app)
app.config['SECRET_KEY'] = "2fc8a0378be548e083bff134553a6e3c"

app.config["UP_DIR"] = os.path.join(os.path.abspath(os.path.dirname(__file__)), "static/uploads/")
app.config["FC_DIR"] = os.path.join(os.path.abspath(os.path.dirname(__file__)), "static/uploads/users/")

app.debug = True

from app.home import home as home_blueprint
from app.admin import admin as admin_blueprint

app.register_blueprint(home_blueprint, url_prefix="/home")
app.register_blueprint(admin_blueprint, url_prefix="/admin")

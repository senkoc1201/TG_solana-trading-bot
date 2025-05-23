import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from abilities import flask_app_authenticator

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///bot.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = os.environ.get('FLASK_SECRET_KEY')

app.before_request(flask_app_authenticator(
    allowed_domains=None,
    allowed_users=None,
    logo_path=None,
    app_title="Solana Trading Bot",
    custom_styles=None,
    session_expiry=None
))

db = SQLAlchemy(app)
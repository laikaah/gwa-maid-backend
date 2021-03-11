from flask import Flask, session, url_for
from flask_session import Session
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt

from cryptography.fernet import Fernet

import secrets
import os

# Configure application
app = Flask(__name__)
app.config['SECRET_KEY'] = secrets.token_hex(256)
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['FERNET_KEY'] = Fernet.generate_key()

db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
fernet = Fernet(app.config['FERNET_KEY'])

# set session type
app.config['SESSION_TYPE'] = 'filesystem'

Session(app)

from gwa_maid import routes
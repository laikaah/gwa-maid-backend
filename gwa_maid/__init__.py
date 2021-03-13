from flask import Flask
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

db = SQLAlchemy(app)
bcrypt = Bcrypt(app)

fernet_key = os.environ.get('FERNET_KEY').encode('utf-8')
fernet = Fernet(fernet_key)

# set session type
app.config['SESSION_TYPE'] = 'filesystem'

from gwa_maid import routes
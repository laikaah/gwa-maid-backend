from gwa_maid import bcrypt, fernet
from gwa_maid.models import User
from cryptography.fernet import InvalidToken


def tokenize(id, password):
    password_crypt = fernet.encrypt(password.encode('utf-8')).decode('utf-8')
    token = f'{id}:{password_crypt}'

    return token


def get_user_from_token(token):
    token_data = token.split(':')

    if len(token_data) != 2:
        return None

    id, password_crypt = int(token_data[0]), token_data[1]

    try:
        password = fernet.decrypt(
            password_crypt.encode('utf-8')).decode('utf-8')
    except InvalidToken:
        return None

    user_from_database = User.query.get(id)

    if user_from_database is None:
        return None

    if bcrypt.check_password_hash(user_from_database.password, password):
        return user_from_database
    else:
        return None

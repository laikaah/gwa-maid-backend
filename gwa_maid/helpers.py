from gwa_maid import fernet, bcrypt
from gwa_maid.models import User


def tokenize(username, password):
    token = fernet.encrypt(f'{username}:{password}'.encode('utf-8')).decode('utf-8')
    
    return token

def get_user_from_token(token):
    user_from_token = fernet.decrypt(token.encode('utf-8')).decode('utf-8').split(':')
    
    username_from_token = user_from_token[0]
    
    user_from_database = User.query.filter(User.username == username_from_token).first()
    
    if user_from_database is None:
        return None
    
    password_from_token = user_from_token[1]
    
    if bcrypt.check_password_hash(user_from_database.password, password_from_token):
        return user_from_database
    else:
        return None
    
    
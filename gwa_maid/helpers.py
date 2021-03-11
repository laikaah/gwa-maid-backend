from gwa_maid import fernet, bcrypt
from gwa_maid.models import User


def tokenize(id, password):
    token = fernet.encrypt(f'{id}:{password}'.encode('utf-8')).decode('utf-8')
    
    return token

def get_user_from_token(token):
    user_from_token = fernet.decrypt(token.encode('utf-8')).decode('utf-8').split(':')
    
    id_from_token = int(user_from_token[0])
    
    user_from_database = User.get(id_from_token)
    
    if user_from_database is None:
        return None
    
    password_from_token = user_from_token[1]
    
    if bcrypt.check_password_hash(user_from_database.password, password_from_token):
        return user_from_database
    else:
        return None
    
    
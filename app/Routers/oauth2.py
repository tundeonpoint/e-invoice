import random
import string
from jose import JWTError,jwt
from datetime import datetime,timedelta
#the time package is required due to issues with the jwt.encode method
#not being able to natively serialize datetime into JSON which is a native
#JSON limitation
import time
from .. import schemas,database,models,utils
from fastapi.security import OAuth2PasswordBearer
from fastapi import Depends,HTTPException,status,Header
from sqlalchemy.orm import Session

oauth2_scheme = OAuth2PasswordBearer('auth')

def generate_random_string(length):
    """
    Generates a random string of a specified length containing
    both uppercase and lowercase letters, and digits.
    """
    characters = string.ascii_letters + string.digits
    random_string = ''.join(random.choice(characters) for _ in range(length))
    return random_string

SECRET_KEY = 'F9oTtd3aizjx1tWVnTFL9mb1NCAbCweqdV0eLEmFFFvd1DUV8AS7gumEbjbTntlW'
ALGORITHM = 'HS256'
TOKEN_EXPIRATION_MINUTES = 30

def create_access_token(data:dict):
    in_data = data.copy()

    exp_time = datetime.now() + timedelta(minutes=TOKEN_EXPIRATION_MINUTES)
    # the exp_time needs to be converted to a Unix timestamp to enable
    # it to work with the jwt.encode method
    exp_time = int(time.mktime(exp_time.timetuple()))
    in_data.update({"exp":exp_time})

    encoded_data = jwt.encode(in_data,key=SECRET_KEY,algorithm=ALGORITHM)

    return encoded_data

def verify_token(token:str,credential_exception):

    try:
        payload = jwt.decode(token,SECRET_KEY,ALGORITHM)
        # print(f'decoded payload:{payload}')
        user_id = payload.get('user_id')
        if user_id == None:
            raise credential_exception
        token_data = schemas.TokenData(user_id=user_id)
    except JWTError:
        raise credential_exception
    
    return token_data

def get_current_user(token:str = Depends(oauth2_scheme),db:Session = Depends(database.get_db)):
    credential_exception = HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                                         detail='Could not validate credentials',
                                         headers={'WWW-Authenticate':'Bearer'})
    
    new_token = verify_token(token,credential_exception)

    current_user = db.query(models.User).filter(models.User.email == new_token.user_id).first()
    
    return current_user

# def get_current_org(secret_key:str = Header(alias="x-api-key"),token:str = Depends(oauth2_scheme),db:Session = Depends(database.get_db)):
# def get_current_org(secret_key:str = Header(alias="x-api-key"),db:Session = Depends(database.get_db)):
#     credential_exception = HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
#                                          detail='Could not validate credentials',
#                                          headers={'WWW-Authenticate':'Bearer'})
#     # validate the current org accessing the end point using both the bearer token
#     # and the secret key. org's zoho id has to match the secret key to be valid.
#     print(f'******secret key:{secret_key}**********')
#     new_token = verify_token(token,credential_exception)

#     current_org = db.query(models.Organisation).filter(models.Organisation.zoho_org_id == new_token.user_id).first()

#     if utils.verify(current_org.org_secret,secret_key) and new_token.user_id == current_org.zoho_org_id:

#         return current_org.zoho_org_id
    
#     else:
        
#         raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail='Invalid credentials.')
    
    
import random
import string
from jose import JWTError,jwt
from datetime import datetime,timedelta
#the time package is required due to issues with the jwt.encode method
#not being able to natively serialize datetime into JSON which is a native
#JSON limitation
import time
from app import schemas,database,models,utils
from app.config import settings
from fastapi.security import OAuth2PasswordBearer
from fastapi import Depends,HTTPException,status,Request,APIRouter
from sqlalchemy import create_engine
from sqlalchemy.orm import Session,sessionmaker,declarative_base
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from fastapi.security.oauth2 import OAuth2PasswordRequestForm
from app.database import get_db
# from config import settings
# from .auth import get_current_user_bauth
DATABASE_URL = database.db_url

engine = create_engine(
    DATABASE_URL,
    connect_args={} #if "sqlite" in DATABASE_URL else {}
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

oauth2_scheme = OAuth2PasswordBearer('auth',auto_error=False)
basic_scheme = HTTPBasic(auto_error=False)
router = APIRouter(tags=['Authentication'])

def generate_random_string(length):
    """
    Generates a random string of a specified length containing
    both uppercase and lowercase letters, and digits.
    """
    characters = string.ascii_letters + string.digits
    random_string = ''.join(random.choice(characters) for _ in range(length))
    return random_string

def get_current_user_bauth(credentials: HTTPBasicCredentials | None = Depends(basic_scheme),
                           db:Session = Depends(database.get_db)):

    if credentials.username == '' or credentials.password == '':
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail='Invalid credentials.')

    result = db.query(models.User).filter(models.User.username == credentials.username).first()

    if result == None or not utils.verify(result.password,credentials.password):      
        raise HTTPException(status.HTTP_401_UNAUTHORIZED,detail='Invalid credentials')
    return credentials.username

def create_access_token(data:dict):
    in_data = data.copy()

    exp_time = datetime.now() + timedelta(minutes=settings.token_expiration_minutes)
    # the exp_time needs to be converted to a Unix timestamp to enable
    # it to work with the jwt.encode method
    exp_time = int(time.mktime(exp_time.timetuple()))
    in_data.update({"exp":exp_time})

    encoded_data = jwt.encode(in_data,key=settings.secret_key,algorithm=settings.algorithm)

    return encoded_data

@router.post('/refresh_token')
def get_refresh_token(credentials:OAuth2PasswordRequestForm = Depends(),db:Session = Depends(get_db)):

    user = db.query(models.User).filter(models.User.username == credentials.username).first()

    if user == None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="Invalid credentials")
    
    if not utils.verify(user.password,credentials.password):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="Invalid credentials")

    refresh_token = create_access_token({"user_id":credentials.username})
    # refresh_token
    return {"token" : refresh_token,"token_type":"refresh"}


def create_refresh_token(data:dict):
    in_data = data.copy()

    exp_time = datetime.now() + timedelta(minutes=settings.token_expiration_minutes * 5)
    # the exp_time needs to be converted to a Unix timestamp to enable
    # it to work with the jwt.encode method
    exp_time = int(time.mktime(exp_time.timetuple()))
    in_data.update({"exp":exp_time})
    in_data.update({"type":"refresh"})

    encoded_data = jwt.encode(in_data,key=settings.secret_key,algorithm=settings.algorithm)

    return encoded_data

def verify_token(token:str,credential_exception):

    try:
        payload = jwt.decode(token,settings.secret_key,settings.algorithm)
        # print(f'decoded payload:{payload}')
        user_id = payload.get('user_id')
        if user_id == None:
            raise credential_exception
        token_data = schemas.TokenData(user_id=user_id)
    except JWTError:
        raise credential_exception
    
    return token_data

def get_current_user(token:str = Depends(oauth2_scheme),
                     db:Session = Depends(database.get_db)):

    token_data = verify_token(token,HTTPException(status.HTTP_401_UNAUTHORIZED,
                                               detail='Invalid credentials.'))
    
    if token_data == None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail='Invalid credentials.')
    
    try:
        result = db.query(models.User).filter(models.User.username == token_data.user_id).first()
        if result == None:# or not utils.verify(result.password,credentials.password):      
            raise HTTPException(status.HTTP_401_UNAUTHORIZED,detail='Invalid credentials')

        return result.username
    
    except Exception as error:
        raise HTTPException(status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail='Error validating authentication credentials.')

def get_current_user_multi_auth(
    request: Request,
    basic: HTTPBasicCredentials | None = Depends(basic_scheme),
    token: str | None = Depends(oauth2_scheme),
):
    # print('******inside decision circle********')

    db = SessionLocal()
    # 1️⃣ Try OAuth2 first
    if token:
        # print('******attempting token auth********')
        user = get_current_user(token,db=db)
        if user:
            return user

    # 2️⃣ Fall back to Basic Auth
    if basic:
        user = get_current_user_bauth(basic,db=db)
        if user:
            return user

    # 3️⃣ If both fail
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid authentication credentials",
        headers={"WWW-Authenticate": "Bearer, Basic"},
    )    

# import fastapi,sqlalchemy
from fastapi import Depends,HTTPException,status,Response,APIRouter,Form,Request
# from app import models,utils
from ..database import get_db
from sqlalchemy.orm import Session
from .. import models,utils
from passlib.hash import pbkdf2_sha256
from fastapi.security.oauth2 import OAuth2PasswordRequestForm
from . import oauth2

router = APIRouter(tags=['Authentication'])

def verify_org(client_id,client_secret,db:Session = Depends(get_db)):

    # client_id = request.headers.get('client_id')
    # client_secret = request.headers.get('client_secret')

    if not client_id or not client_secret:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail='Invalid credentials.')
    
    result = db.query(models.User).filter(models.User.email == client_id).first()

    if result == None or not utils.verify(result.password,client_secret):      
        raise HTTPException(status.HTTP_401_UNAUTHORIZED,detail='Invalid credentials')
    
    return client_id


@router.post('/auth')
def user_auth(credentials:OAuth2PasswordRequestForm = Depends(),db:Session = Depends(get_db)):

    user = db.query(models.User).filter(models.User.email == credentials.username).first()

    if user == None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="Invalid credentials")
    
    if not utils.verify(user.password,credentials.password):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="Invalid credentials")

    access_token = oauth2.create_access_token({"user_id":credentials.username})

    return {"token" : access_token,"token_type":"bearer"}

# @router.post('/org_auth')
def org_auth(client_id:str = Form(...),client_secret:str = Form(...),
             db:Session = Depends(get_db)):

    org_id = verify_org(client_id,client_secret,db)

    if org_id == None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail='Invalid credentials.')
    
    access_token = oauth2.create_access_token({"org_id":org_id})

    return {"token" : access_token,"token_type":"bearer"}

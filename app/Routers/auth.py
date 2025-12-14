# import fastapi,sqlalchemy
from fastapi import Depends,HTTPException,status,Response,APIRouter,Form,Request
# from app import models,utils
from app.database import get_db
from sqlalchemy.orm import Session
from app import models,utils
from passlib.hash import pbkdf2_sha256
from app.Routers import oauth2
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from fastapi.security.oauth2 import OAuth2PasswordRequestForm
from app.config import settings

router = APIRouter(tags=['Authentication'])

security = HTTPBasic()

def verify_org(credentials: HTTPBasicCredentials = Depends(security),db = Depends(get_db)):

    if credentials.username == '' or credentials.password == '':
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail='Invalid credentials.')
    
    result = db.query(models.Organisation).filter(models.Organisation.zoho_org_id == credentials.username).first()

    if result == None or not utils.verify(result.org_secret,credentials.password):      
        raise HTTPException(status.HTTP_401_UNAUTHORIZED,detail='Invalid credentials')
    
    return credentials.username


@router.post('/auth')
def user_auth(credentials:OAuth2PasswordRequestForm = Depends(),db:Session = Depends(get_db)):

    user = db.query(models.User).filter(models.User.username == credentials.username).first()

    if user == None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="Invalid credentials")
    
    if not utils.verify(user.password,credentials.password):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="Invalid credentials")

    access_token = oauth2.create_access_token({"user_id":credentials.username})

    return {"token" : access_token,"token_type":"bearer"}


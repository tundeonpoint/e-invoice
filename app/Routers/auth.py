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
import httpx
from fastapi.responses import RedirectResponse
from utils import encrypt_token,decrypt_token

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

# import httpx
# from fastapi import FastAPI, Request, HTTPException
# from fastapi.responses import RedirectResponse

# Config from Zoho API Console
CLIENT_ID = settings.zoho_api_client_id
CLIENT_SECRET = settings.zoho_api_client_secret
REDIRECT_URI = "https://api.einvoice.ultieraltd.com/auth/callback"

@router.get("/auth/login")
async def login():
    # Multi-DC: Always start auth at the .com domain
    auth_url = (
        f"https://accounts.zoho.com/oauth/v2/auth"
        f"?scope=ZohoCRM.users.READ,aaaserver.profile.READ"
        f"&client_id={CLIENT_ID}&response_type=code"
        f"&access_type=offline&prompt=consent"
        f"&redirect_uri={REDIRECT_URI}"
    )
    return RedirectResponse(auth_url)

@router.get("/auth/callback")
async def callback(code: str, location: str, accounts_server: str):
    """
    Zoho sends 'location' (e.g., 'us', 'eu') and 'accounts-server' 
    back so you know which DC to talk to.
    """
    print(f"Callback received for DC: {location}, accounts server: {accounts_server}")
    print(f"Authorization code: {code}")
    # 1. Exchange Grant Code for Tokens
    token_url = f"{accounts_server}/oauth/v2/token"
    async with httpx.AsyncClient() as client:
        token_res = await client.post(token_url, params={
            "code": code,
            "client_id": CLIENT_ID,
            "client_secret": CLIENT_SECRET,
            "redirect_uri": REDIRECT_URI,
            "grant_type": "authorization_code"
        })
        tokens = token_res.json()

        # 2. Get User Info to identify who this is
        user_info_res = await client.get(
            f"{accounts_server}/oauth/user/info",
            headers={"Authorization": f"Zoho-oauthtoken {tokens['access_token']}"}
        )
        user_data = user_info_res.json()

    # 3. Encrypt and Store
    zuid = str(user_data["ZUID"])
    encrypted_refresh = encrypt_token(tokens["refresh_token"])
    
    # logic: db.upsert_user(zuid, email=user_data['Email'], refresh=encrypted_refresh, dc=accounts_server)
    
    return {"status": "Success", "user": user_data["Email"]}
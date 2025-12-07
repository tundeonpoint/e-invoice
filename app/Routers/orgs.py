# import sqlalchemy
# import fastapi
from fastapi import Depends,HTTPException,status,Response,APIRouter
from app import schemas,models,database,utils
from app.database import get_db
from sqlalchemy.orm import Session
from typing import List
from Routers import oauth2,auth
import uuid
from fastapi.security import HTTPBasic,HTTPBasicCredentials
from app.config import settings
from Routers.users import create_user

security = HTTPBasic()


router = APIRouter(
    prefix="/orgs",
    tags=['Organisations']
)


@router.get('',status_code=status.HTTP_200_OK,response_model=List[schemas.OrganisationOut])
def get_orgs(db:Session=Depends(get_db),
            current_user:int = Depends(oauth2.get_current_user)):
    
    if current_user == None:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED,detail='User not authenticated.')
    
    # try:
    result = db.query(models.Organisation).all()
    # except Exception as error:

        # raise HTTPException(status.HTTP_500_INTERNAL_SERVER_ERROR,
        #                 detail="Error retrieving records.")
    
    if result == None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"Organisation {id} not found.")
    
    return result

@router.get('/{id}',status_code=status.HTTP_200_OK,response_model=schemas.OrganisationOut)
def get_org(id:str,db:Session=Depends(get_db),
            current_user:int = Depends(oauth2.get_current_user)):
    
    if current_user == None:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED,detail='User not authenticated.')
    
    try:
        result = db.query(models.Organisation).where(models.Organisation.business_id == id).first()
    except Exception as error:
        raise HTTPException(status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail="Error retrieving record.")
    
    if result == None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"Organisation {id} not found.")
    
    return result

@router.post('',status_code=status.HTTP_200_OK)
def create_org(org:schemas.OrganisationCreate,db:Session=Depends(get_db),
               user_id:str = Depends(oauth2.get_current_user)):
    
    # if current_user == None:
    #     raise HTTPException(status.HTTP_401_UNAUTHORIZED,detail='User not authenticated.')
    # if auth.verify_org(credentials.username,credentials.password,db) == False:
    #     raise HTTPException(status.HTTP_401_UNAUTHORIZED,detail='User not authenticated.')
    
    new_org = models.Organisation(**org.model_dump())

    if not utils.arca_verify_org(new_org):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail='Invalid organisation information.')
    
    org_secret_plain = str(uuid.uuid4()).replace('-','') #this is for testing
    new_org.org_secret = utils.hash(org_secret_plain)
    
    try:
        result_state = db.query(models.State_Code).filter(models.State_Code.name == new_org.address['state']).first()
        result_lga = db.query(models.LGA_Code).filter(models.LGA_Code.name == new_org.address['lga']).filter(models.LGA_Code.state_code == result_state.code).first()
        result_country = db.query(models.Country_Code).filter(models.Country_Code.name == new_org.address['country']).first()
        new_org.address['state'] = result_state.code
        new_org.address['lga'] = result_lga.code
        new_org.address['country'] = result_country.code
    except Exception as error:
        return {"status":"Failed","message":"Error creating organisation.",
        "Exception":str(error)}    
    
    try:
        db.add(new_org)
        # create_user(schemas.UserCreate(username=new_org.zoho_org_id,
        #                            password=org_secret_plain),db)
        db.flush()
        # new_org = 
    except Exception as error:
        return {"status":"Failed","message":"Error creating organisation.",
                "Exception":str(error)}
    db.commit()
    db.refresh(new_org)
    

    return {"status":"Success","message":"Organisation added successfully.",
            "secret_key":org_secret_plain}

@router.get('/validate/{business_id}',status_code=status.HTTP_302_FOUND)
def validate_business(business_id:str,credentials: HTTPBasicCredentials = Depends(security),
                      db:Session=Depends(get_db)):
    
    if not auth.verify_org(credentials.username,credentials.password,db):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail='Invalide credentials.')
    
    return {'username':credentials.username}


@router.put('/{zoho_id}',status_code=status.HTTP_200_OK)
def regenerate_secret(zoho_id,db:Session=Depends(get_db),
            credentials: HTTPBasicCredentials = Depends(security)):
    
    # if current_user == None:
    #     raise HTTPException(status.HTTP_401_UNAUTHORIZED,detail='User not authenticated.')
    if auth.verify_org(credentials.username,credentials.password,db) == False:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED,detail='User not authenticated.')
    
@router.get('/regeneratepwd/{cli_id}',status_code=status.HTTP_302_FOUND)
def regenerate_pwd(cli_id:str,org_id : str = Depends(oauth2.get_current_user),
                   db:Session = Depends(get_db)):

    if org_id != settings.zoho_user:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED,detail='Unauthorised credentials.')
    
    try:
        o_org = db.query(models.Organisation).filter(models.Organisation.zoho_org_id==cli_id).first()

        if o_org == None:
            return {'status':'failure',
                    'message':'Unrecognised organisation. Please contact the administrator.'}

        org_secret_plain = str(uuid.uuid4()).replace('-','') #this is for testing
        o_org.org_secret = utils.hash(org_secret_plain)
        db.commit()
        return {'status':'success','password':org_secret_plain}
    except:
        return {'status':'failure','message':'Error generating new password. Please try again later.'}

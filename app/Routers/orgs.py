import sqlalchemy
# import fastapi
from fastapi import Depends,HTTPException,status,Request,APIRouter
from app import schemas,models,database,utils
from app.database import get_db
from sqlalchemy.orm import Session
from typing import List
from Routers import oauth2,auth
import uuid
from fastapi.security import HTTPBasic,HTTPBasicCredentials
from app.config import settings
from Routers.users import create_user
from app.key_gen import generate_random_string
from app.config import settings

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
               user_id:str = Depends(oauth2.get_current_user_multi_auth)):
    
    new_org = models.Organisation(**org.model_dump())
    new_user = models.User()
    # if user_id != settings.zoho_user:
    #     raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
    #                         detail='Invalid credentials.')

    if not utils.arca_verify_org(new_org):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail='Invalid organisation information.')
    
    org_secret_plain = str(uuid.uuid4()).replace('-','') #this is for testing
    new_org.org_secret = utils.hash(org_secret_plain)
    new_org.hash_key = str(uuid.uuid4()).replace('-','')
    
    # check if the user account for the org already exists
    existing_user = db.query(models.User).filter(models.User.username == new_org.zoho_org_id).first()
    if existing_user != None:
        if existing_user.scope != None:
            existing_user.scope = existing_user.scope['scope'].append(user_id)
        else:
            existing_user.scope = {'scope':[user_id]}
    else:
        new_user.scope = {'scope':[user_id]}
    # create the user account for the org

    new_user.username = new_org.zoho_org_id
    new_user.password = new_org.org_secret
    new_user.role = 'org'
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
        db.add(new_user)
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

@router.put('/{org_id}',status_code=status.HTTP_200_OK)
def update_org(org_id,org:schemas.OrganisationCreate,db:Session=Depends(get_db),
               user_id:str = Depends(oauth2.get_current_user_multi_auth)):
    
    new_org = models.Organisation(**org.model_dump())

    # ensure only the zoho_user account
    # can make these updates.
    if user_id != settings.zoho_user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail='Invalid credentials.')

    if not utils.arca_verify_org(new_org):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail='Invalid organisation information.')
    
    try:
        result = db.query(models.Organisation).filter(models.Organisation.zoho_org_id == org_id).first()
        result.business_description = new_org.business_description
        result.email = new_org.email
        result.name = new_org.name
        result.rc_number = new_org.rc_number
        result.telephone = new_org.telephone
        result.tin = new_org.tin
        result_state = db.query(models.State_Code).filter(models.State_Code.name == new_org.address['state']).first()
        result_lga = db.query(models.LGA_Code).filter(models.LGA_Code.name == new_org.address['lga']).filter(models.LGA_Code.state_code == result_state.code).first()
        result_country = db.query(models.Country_Code).filter(models.Country_Code.name == new_org.address['country']).first()
        new_org.address['state'] = result_state.code
        new_org.address['lga'] = result_lga.code
        new_org.address['country'] = result_country.code
        result.address = new_org.address
        db.commit()

        return {"status":"Success","message":"Organisation updated successfully."}
    except Exception as error:
        return {"status":"Failed","message":"Error updating organisation.",
        "Exception":str(error)}

@router.delete('/{org_id}',status_code=status.HTTP_202_ACCEPTED)
def delete_org(org_id,db:Session=Depends(get_db),
               user_id:str = Depends(oauth2.get_current_user_multi_auth)):
    
    if user_id != settings.zoho_user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail='Invalid credentials.')
    try:
        org = db.query(models.Organisation).filter(models.Organisation.zoho_org_id == org_id).first()
        if org == None:
            raise HTTPException(status.HTTP_404_NOT_FOUND,
                                detail="Organisation record not found.")
        db.delete(org)

        # delete associated user account
        user = db.query(models.User).filter(models.User.username == org_id).first()
        if user == None:
            pass
        else:
            db.delete(user)
        db.commit()
        return {"status":"Success","message":"Organisation deleted successfully."}
    except Exception as error:
        return {"status":"Failed","message":"Error deleting organisation.",
        "Exception":str(error)}

@router.get('/validate/{business_id}',status_code=status.HTTP_302_FOUND)
def validate_business(business_id:str,credentials: HTTPBasicCredentials = Depends(security),
                      db:Session=Depends(get_db)):
    
    if not auth.verify_org(credentials,db):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail='Invalide credentials.')
    
    return {'username':credentials.username}


@router.get('/regeneratepwd/{cli_id}',status_code=status.HTTP_200_OK)
def regenerate_pwd(cli_id:str,org_id : str = Depends(oauth2.get_current_user_multi_auth),
                   db:Session = Depends(get_db)):

    # ensure this request is being made by the zoho_user account
    # which is the only account allowed to make this request
    if org_id != settings.zoho_user:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED,detail='Unauthorised credentials.')
    
    try:
        o_org = db.query(models.Organisation).filter(models.Organisation.zoho_org_id==cli_id).first()

        if o_org == None:
            return {'status':'failure',
                    'message':'Unrecognised organisation. Please contact the administrator.'}

        org_secret_plain = str(uuid.uuid4()).replace('-','') #this is for testing
        o_org.org_secret = utils.hash(org_secret_plain)

        # update the organisation's password
        o_user = db.query(models.User).filter(models.User.username == cli_id).first()
        o_user.password = o_org.org_secret
        db.commit()
        return {'status':'success','password':org_secret_plain}
    except:
        return {'status':'failure','message':'Error generating new password. Please try again later.'}

@router.get('/regeneratehash/{cli_id}',status_code=status.HTTP_200_OK)
def regenerate_hash(cli_id:str,org_id : str = Depends(oauth2.get_current_user_multi_auth),
                   db:Session = Depends(get_db)):

    if org_id != settings.zoho_user:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED,detail='Unauthorised credentials.')
    
    try:
        o_org = db.query(models.Organisation).filter(models.Organisation.zoho_org_id==cli_id).first()

        if o_org == None:
            return {'status':'failure',
                    'message':'Unrecognised organisation. Please contact the administrator.'}

        o_org.hash_key = str(uuid.uuid4()).replace('-','')
        db.commit()
        return {'status':'success','password':o_org.hash_key}
    except:
        return {'status':'failure','message':'Error generating new password. Please try again later.'}

@router.post("/init_org_access/{org_id}",status_code=status.HTTP_201_CREATED)
def init_org_access(org_id,db:Session = Depends(get_db),request:Request = None):

    # return f"password is {user.password} and length is {len(user.password)}"
    # check if org_id exists
    existing_org = db.query(models.User).filter(models.User.username == org_id).first()
    if existing_org != None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail="Organisation account already initialized.")
    
    headers_dict = dict(request.headers)
    passed_init_key = headers_dict.get('zoho_init_key',None)
    # print(f"all headers received: {request.headers}")
    # print(f"Initialization key received: {passed_init_key}")
    if passed_init_key == None or passed_init_key != settings.zoho_init_key:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail="Invalid initialization key.")

    pwd = generate_random_string(64)
    hashed_password = utils.hash(pwd)
    # return hashed_password
    # user.password = hashed_password
    
    new_user = models.User(username=org_id,password=hashed_password,role='org')

    try:
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
    except sqlalchemy.exc.IntegrityError:
        # print("discovered error")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail="Error creating account.")
    return {"status":"success","password":pwd}
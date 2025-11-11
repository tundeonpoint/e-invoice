import sqlalchemy
import fastapi
from fastapi import Depends,HTTPException,status,Response,APIRouter
from .. import schemas,models,database,utils
from ..database import get_db
from sqlalchemy.orm import Session
from typing import List
from . import oauth2
import uuid

router = APIRouter(
    prefix="/orgs",
    tags=['Organisations']
)


@router.get('',status_code=status.HTTP_200_OK,response_model=List[schemas.OrganisationOut])
def get_orgs(db:Session=Depends(get_db),
            current_user:int = Depends(oauth2.get_current_user)):
    
    if current_user == None:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED,detail='User not authenticated.')
    
    try:
        result = db.query(models.Organisation).all()
    except Exception as error:

        raise HTTPException(status.HTTP_500_INTERNAL_SERVER_ERROR,
                        detail="Error retrieving records.")
    
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

@router.post('',status_code=status.HTTP_200_OK,response_model=schemas.OrganisationOut)
def create_org(org:schemas.OrganisationCreate,db:Session=Depends(get_db),
            current_user:int = Depends(oauth2.get_current_user)):
    
    if current_user == None:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED,detail='User not authenticated.')
    
    new_org = models.Organisation(**org.model_dump())
    new_org.org_secret_plain = str(uuid.uuid4()).replace('-','') #this is for testing
    new_org.org_secret = utils.hash(new_org.org_secret_plain)
    
    try:
        db.add(new_org)
        db.commit()
        # new_org = 
        db.refresh(new_org)
    except Exception as error:
        raise HTTPException(status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail="Error adding record.")
    
    return new_org
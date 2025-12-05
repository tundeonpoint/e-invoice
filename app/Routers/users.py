import sqlalchemy
# import fastapi
from fastapi import Depends,HTTPException,status,Response,APIRouter
from app import schemas,models,utils
from app.database import get_db
from sqlalchemy.orm import Session
from typing import List

router = APIRouter(
    prefix="/users",
    tags=['Users']
)

@router.get("",status_code=status.HTTP_200_OK,response_model=List[schemas.UserOut])
def get_all_users(db:Session = Depends(get_db)):

    try:
        results = db.query(models.User).all()
    except:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail="Error fetching records from database")
    
    if results == None:
        return "No records found"
    else:
        return results

@router.get("/{id}",status_code=status.HTTP_200_OK,response_model=schemas.UserOut)
def get_users(id:int,db:Session = Depends(get_db)):

    try:
        results = db.query(models.User).filter(models.User.id == id).first()
    except:
        if results == None:
            return "No records found"
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail="Error fetching record from database")
    
    if results == None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="Record not found")
    else:
        return results


@router.post("",status_code=status.HTTP_201_CREATED,response_model=schemas.UserOut)
def create_user(user:schemas.UserCreate,db:Session = Depends(get_db)):

    # return f"password is {user.password} and length is {len(user.password)}"
    hashed_password = utils.hash(user.password)
    # return hashed_password
    user.password = hashed_password
    
    new_user = models.User(**user.model_dump())

    try:
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
    except sqlalchemy.exc.IntegrityError:
        # print("discovered error")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail="Error creating account.")
    return new_user
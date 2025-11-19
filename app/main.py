from fastapi import FastAPI,Depends,Header,HTTPException,status
from app.database import get_db
# import database,sqlalchemy
from sqlalchemy.orm import Session
# import app.models
from datetime import date
from app import schemas,models,utils
# import app.utils
from typing import List,Annotated
from .Routers import users,invoice_utils,auth,oauth2,orgs,invoices
from .schemas import CommonHeaders
# from database import get_db

app = FastAPI()

app.include_router(invoice_utils.router)
app.include_router(users.router)
app.include_router(auth.router)
app.include_router(orgs.router)
app.include_router(invoices.router)


@app.get("")
def root():
    return {'message':'hello world'}

@app.get("/headertest")
def header_test(org_id:str = Header('org_id',convert_underscores=False)):
    return {'Organisation':org_id}

@app.get("/testvalidation/{biz_id}")
def test_validation(biz_id:str):

    if biz_id != '10001':
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail='Invalid business id')
    else:
        return 'Valid business id'



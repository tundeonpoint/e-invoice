from fastapi import FastAPI,Depends,Header
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


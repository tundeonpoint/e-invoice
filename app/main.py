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
from .key_gen import generate_random_string
import json
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

# @app.get("/headertest")
# def header_test(org_id:str = Header('org_id',convert_underscores=False)):
#     return {'Organisation':org_id}

@app.post("/arca_endpoint",status_code=status.HTTP_200_OK)
def test_validation(payload:dict):
    # this endpoint is to be deleted once we have
    # the endpoint for the APP
    rand_string = generate_random_string(7)
    return {"irn":"irn"+rand_string}

# following code is to be removed
# @app.get("/get_sent_invoices")#,status_code=status.HTTP_302_FOUND)
# def get_sent_invoices(db:Session = Depends(get_db)):#,
#                 #    current_user:str = Depends(auth.get_current_user_bauth)):
#     print('*******started function call*********')
    
#     # retrieve all the invoices that have been sent
#     # but are yet to be retrieved. this ensures we minimise the
#     # amount of data being retrieved on every call.
#     results = db.query(models.Invoice_Map).filter(models.Invoice_Map.retrieve_status == False).all()

#     json_result = json.dumps([r.to_dict() for r in results])

#     try:
#         for result in results:
#             result.retrieve_status = True
        
#         db.commit()
    
#     except:

#         return {"status":"failed"}
    
#     return {"status":"success","data":json_result}
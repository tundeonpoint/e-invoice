from passlib.hash import pbkdf2_sha256
from app.models import Organisation
# from passlib

def hash(password:str):
    return pbkdf2_sha256.hash(password)

def verify(val_hash:str,plain_pwd:str):
    return pbkdf2_sha256.verify(plain_pwd,val_hash)

def arca_verify_org(org_info:Organisation):
    return True
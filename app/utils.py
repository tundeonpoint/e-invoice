from passlib.hash import pbkdf2_sha256
from app.models import Organisation
# from passlib
from config import settings
import os
import base64
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

def hash(password:str):
    return pbkdf2_sha256.hash(password)

def verify(val_hash:str,plain_pwd:str):
    return pbkdf2_sha256.verify(plain_pwd,val_hash)

def arca_verify_org(org_info:Organisation):
    return True


# Store this in your .env file! Never hardcode it.
MASTER_KEY =  settings.secret_key# Must be 32 bytes for AES-256

def encrypt_token(token: str) -> str:
    aesgcm = AESGCM(MASTER_KEY.encode())
    nonce = os.urandom(12)  # GCM standard nonce size
    ciphertext = aesgcm.encrypt(nonce, token.encode(), None)
    # Store nonce + ciphertext together
    return base64.b64encode(nonce + ciphertext).decode('utf-8')

def decrypt_token(encrypted_blob: str) -> str:
    data = base64.b64decode(encrypted_blob)
    nonce, ciphertext = data[:12], data[12:]
    aesgcm = AESGCM(MASTER_KEY.encode())
    return aesgcm.decrypt(nonce, ciphertext, None).decode('utf-8')
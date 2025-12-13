from pydantic_settings import BaseSettings,SettingsConfigDict
import os


# pwd_context = pbkdf2_sha256(schemes=["bcrypt_sha256"],deprecated="auto")
class Settings (BaseSettings):
    database_type:str
    database_password:str
    database_username:str
    database_hostname:str
    database_name:str
    database_portnumber:str
    database_name:str
    secret_key:str
    algorithm:str
    token_expiration_minutes:int
    zoho_user:str
    ap_provider_post_endpoint:str
    ap_provider_put_endpoint:str

    model_config = SettingsConfigDict(env_file=os.path.join(os.path.dirname(__file__), '.env'))

settings = Settings()

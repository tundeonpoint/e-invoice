from sqlalchemy import create_engine,MetaData
from sqlalchemy.orm import declarative_base,sessionmaker
from app.config import settings

db_url = f"{settings.database_type}://{settings.database_username}:{settings.database_password}@{settings.database_hostname}:{settings.database_portnumber}/{settings.database_name}"

engine = create_engine(db_url,echo=True)

meta = MetaData()

Base = declarative_base()

new_session = sessionmaker(bind=engine)

session = new_session()

def get_db():
    db = session
    try:
        yield db
    finally:
        db.close()
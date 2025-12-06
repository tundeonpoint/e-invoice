# import os
# import sys
import string
import random

# Force project root as working directory
# BASE_DIR = os.path.dirname(os.path.abspath(__file__))
# os.chdir(BASE_DIR)

# Add project root to Python PATH
# sys.path.append(BASE_DIR)
import csv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.models import Country_Code,State_Code,LGA_Code  # import your existing model
from app.database import get_db
from app.config import settings
import pandas as pd
# ------------------------------------------------------------
# 1. Database setup
# ------------------------------------------------------------
# Example for PostgreSQL
# DATABASE_URL = "postgresql+psycopg2://username:password@localhost:5432/mydb"
db_url = settings.database_type+"://"+settings.database_username+":"+settings.database_password+"@"+settings.database_hostname+":5432/"+settings.database_name
engine = create_engine(db_url)
SessionLocal = sessionmaker(bind=engine)

# db = get_db()
# If tables are not created yet:
# Base.metadata.create_all(bind=engine)

# ------------------------------------------------------------
# 2. Function to upload CSV
# ------------------------------------------------------------
def upload_countries_from_csv(csv_path: str):
    session = SessionLocal()
    
    try:
        df = pd.read_csv(csv_path)
        
        # --- 💡 Data Cleaning Step ---
        # Drop rows where the 'code' column is null (NaN or None)
        df_clean = df.dropna(subset=['code']) 
        
        # Report how many rows were dropped
        rows_dropped = len(df) - len(df_clean)
        if rows_dropped > 0:
            print(f"⚠️ Warning: Dropped {rows_dropped} rows due to missing 'code' value.")
        # -----------------------------

        print(f"Attempting to upload {len(df_clean)} clean rows...")

        df_clean.to_sql(
            name=Country_Code.__tablename__, 
            con=engine,
            if_exists="append", 
            index=False,
            method="multi", 
        )
        
        session.commit()
        print("✅ Upload complete and transaction committed!")
        
    except Exception as e:
        print(f"🛑 Error during upload: {e}")
        session.rollback()
        
    finally:
        session.close()

def upload_states_from_csv(csv_path: str):
    session = SessionLocal()
    
    try:
        df = pd.read_csv(csv_path)
        
        # --- 💡 Data Cleaning Step ---
        # Drop rows where the 'code' column is null (NaN or None)
        df_clean = df.dropna(subset=['code']) 
        
        # Report how many rows were dropped
        rows_dropped = len(df) - len(df_clean)
        if rows_dropped > 0:
            print(f"⚠️ Warning: Dropped {rows_dropped} rows due to missing 'code' value.")
        # -----------------------------

        print(f"Attempting to upload {len(df_clean)} clean rows...")

        df_clean.to_sql(
            name=State_Code.__tablename__, 
            con=engine,
            if_exists="append", 
            index=False,
            method="multi", 
        )
        
        session.commit()
        print("✅ Upload complete and transaction committed!")
        
    except Exception as e:
        print(f"🛑 Error during upload: {e}")
        session.rollback()
        
    finally:
        session.close()

def upload_lgas_from_csv(csv_path: str):
    session = SessionLocal()
    
    try:
        df = pd.read_csv(csv_path)
        
        # --- 💡 Data Cleaning Step ---
        # Drop rows where the 'code' column is null (NaN or None)
        df_clean = df.dropna(subset=['code']) 
        
        # Report how many rows were dropped
        rows_dropped = len(df) - len(df_clean)
        if rows_dropped > 0:
            print(f"⚠️ Warning: Dropped {rows_dropped} rows due to missing 'code' value.")
        # -----------------------------

        print(f"Attempting to upload {len(df_clean)} clean rows...")

        df_clean.to_sql(
            name=LGA_Code.__tablename__, 
            con=engine,
            if_exists="append", 
            index=False,
            method="multi", 
        )
        
        session.commit()
        print("✅ Upload complete and transaction committed!")
        
    except Exception as e:
        print(f"🛑 Error during upload: {e}")
        session.rollback()
        
    finally:
        session.close()


# ------------------------------------------------------------
# 3. Run the upload
# ------------------------------------------------------------
if __name__ == "__main__":
    upload_lgas_from_csv("List_of_LGAs.csv")

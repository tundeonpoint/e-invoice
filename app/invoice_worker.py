import time
# import json
import httpx
from sqlalchemy import create_engine#, Column, Integer, Boolean, JSON
from sqlalchemy.orm import sessionmaker, declarative_base, Session
from app.models import Zoho_Invoice 
import database
from fastapi import HTTPException,status
from Routers import invoices

# --------------------------------------------------
#  DATABASE SETUP
# --------------------------------------------------

DATABASE_URL = database.db_url

engine = create_engine(
    DATABASE_URL,
    connect_args={} #if "sqlite" in DATABASE_URL else {}
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


# --------------------------------------------------
#  MODEL
# --------------------------------------------------


# Create table if not exists
Base.metadata.create_all(bind=engine)


# --------------------------------------------------
#  WORKER LOOP
# --------------------------------------------------

API_ENDPOINT = "http://127.0.0.1:8000/arca_endpoint"   # change to your actual API
INTERVAL_SECONDS = 30  # run every 30 seconds


def process_pending_records(db: Session):
    """Selects all records with status=False, sends them to the API, marks sent."""
    pending = db.query(Zoho_Invoice).filter(Zoho_Invoice.send_status == False).all()

    if not pending:
        print("No pending records found.")
        return

    print(f"Found {len(pending)} pending records… sending…")

    with httpx.Client(timeout=10) as client:
        for record in pending:
            try:
                send_data = invoices.create_arca_invoice(record,db)

                if record.send_treatment == 1:
                    response = client.post(API_ENDPOINT, json=send_data)
                elif record.send_treatment == 2:
                    response = client.post(API_ENDPOINT, json=send_data)
                else:
                    raise HTTPException(status.HTTP_422_UNPROCESSABLE_CONTENT,
                                        detail=f'Unknown treatment request for invoice {record.invoice_id}.')
                
                if response.status_code == 200:
                    # Mark record as processed
                    record.send_status = True
                    db.commit()
                    print(f"Record {record.invoice_id} forwarded successfully.")
                else:
                    print(f"Record {record.invoice_id} failed -> HTTP {response.status_code}")

            except Exception as e:
                print(f"Error sending record {record.invoice_id}: {e}")
                print(record)

def run_worker():
    print("Worker started... polling database every", INTERVAL_SECONDS, "seconds")

    # db = SessionLocal()
    while True:
        try:
            db = SessionLocal()
            process_pending_records(db)
        except Exception as e:
            print("Worker error:", e)
        finally:
            db.close()

        time.sleep(INTERVAL_SECONDS)


# --------------------------------------------------
#  MAIN ENTRY
# --------------------------------------------------

if __name__ == "__main__":
    run_worker()

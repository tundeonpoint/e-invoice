import fastapi
from fastapi import Depends,HTTPException,status,Response,APIRouter
from .. import schemas,models
# import database
from ..database import get_db
# import database,sqlalchemy
from sqlalchemy.orm import Session
import pandas as pd
from app.models import State_Code,LGA_Code,Country_Code

router = APIRouter(
    tags=['Invoice Supporting Data'],
    prefix='/utils'
)

@router.get("/invoice_types",status_code=status.HTTP_200_OK)
def get_invoice_types(response:Response,db:Session = Depends(get_db)):
    results = db.query(models.Invoice_Type).all()
    return {"data":results}

@router.post("/invoice_types",status_code=status.HTTP_201_CREATED)
def create_invoice_type(invoice_type:schemas.InvoiceType,db:Session = Depends(get_db)):
    new_invoice_type = models.Invoice_Type(**invoice_type.model_dump())
    try:
        db.add(new_invoice_type)
        db.commit()
    except Exception as error:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
                            detail='Error adding new invoice type')
    return "Invoice type added successfully"

@router.get("/payment_means")
def get_payment_means(db:Session = Depends(get_db)):
    try:
        payment_means = db.query(models.Payment_Means).all()
        return {"data" : payment_means}
    except Exception as error:
        print("Error retrieving payment means")
        return "Error retrieving payment means"

@router.post("/payment_means",status_code=status.HTTP_201_CREATED)
def create_payment_means(payment_means:schemas.PaymentMeans,db:Session = Depends(get_db)):
    new_payment_means = models.Payment_Means(**payment_means.model_dump())
    try:
        db.add(new_payment_means)
        db.commit()
    except Exception as error:
        print(error)
        return "Error adding new payment means"
    return "Payment means added successfully"

@router.get("/tax_categories")
def get_tax_category(db:Session = Depends(get_db)):
    try:
        tax_categories = db.query(models.Tax_Category).all()
        return {"data" : tax_categories}
    except Exception as error:
        print(error)
        return "Error retrieving tax categories"

@router.post("/tax_categories",status_code=status.HTTP_201_CREATED)
def create_tax_category(tax_category:schemas.TaxCategory,db:Session = Depends(get_db)):
    new_tax_category = models.Tax_Category(**tax_category.model_dump())
    try:
        db.add(new_tax_category)
        db.commit()
    except Exception as error:
        print(error)
        return "Error adding new tax category"
    return "Tax category added successfully"

# resume from here
@router.get("/states")
def get_state_codes(db:Session = Depends(get_db)):
    try:
        state_codes = db.query(models.State_Code).all()
        return {"data" : state_codes}
    except Exception as error:
        print(error)
        return "Error retrieving state codes"

@router.post("/states",status_code=status.HTTP_201_CREATED)
def create_state_code(state_code:schemas.StateCode,db:Session = Depends(get_db)):
    new_state_code = models.State_Code(**state_code.model_dump())
    try:
        db.add(new_state_code)
        db.commit()
    except Exception as error:
        print(error)
        return "Error adding new state code"
    return "State code added successfully"

@router.get("/lgas")
def get_lga_codes(db:Session = Depends(get_db)):
    try:
        lga_codes = db.query(models.LGA_Code).all()
        return {"data" : lga_codes}
    except Exception as error:
        print(error)
        return "Error retrieving lga codes"

@router.post("/lgas",status_code=status.HTTP_201_CREATED)
def create_lga_code(lga_code:schemas.LGACode,db:Session = Depends(get_db)):
    new_lga_code = models.LGA_Code(**lga_code.model_dump())
    try:
        db.add(new_lga_code)
        db.commit()
    except Exception as error:
        print(error)
        return "Error adding new LGA code"
    return "LGA code added successfully"

@router.get("/countries")
def get_country_codes(db:Session = Depends(get_db)):
    try:
        country_codes = db.query(models.Country_Code).all()
        return {"data" : country_codes}
    except Exception as error:
        print(error)
        return "Error retrieving country codes"

@router.get("/vat_exemptions")
def get_vat_exemptions(db:Session = Depends(get_db)):
    try:
        vat_exemptions = db.query(models.VAT_Exemption).all()
        return {"data" : vat_exemptions}
    except Exception as error:
        print(error)
        return "Error retrieving VAT exemptions"

@router.post("/vat_exemptions",status_code=status.HTTP_201_CREATED)
def create_vat_exemption(vat_exemption:schemas.VATExemption,db:Session = Depends(get_db)):
    new_vat_exemption = models.VAT_Exemption(**vat_exemption.model_dump())
    try:
        db.add(new_vat_exemption)
        db.commit()
    except Exception as error:
        print(error)
        return "Error adding new vat exemption"
    return "VAT exemption added successfully"

@router.get("/currencies")
def get_currencies(db:Session = Depends(get_db)):
    try:
        currencies = db.query(models.Currency).all()
        return currencies
    except Exception as error:
        print(error)
        return "Error retrieving currencies"

@router.post("/currencies",status_code=status.HTTP_201_CREATED,response_model=schemas.Currency)
def create_currency(currency:schemas.CurrencyCreate,db:Session = Depends(get_db)):
    new_currency = models.Currency(**currency.model_dump())
    try:
        db.add(new_currency)
        db.commit()
        db.refresh(new_currency)
    except Exception as error:
        print(error)
        return "Error adding new currency."
    return new_currency

@router.get("/product_codes")
def get_product_codes(db:Session = Depends(get_db)):
    try:
        product_codes = db.query(models.Product_Code).all()
        return {"data" : product_codes}
    except Exception as error:
        print(error)
        return "Error retrieving product codes"

@router.post("/product_codes",status_code=status.HTTP_201_CREATED)
def create_product_code(product_code:schemas.ProductCode,db:Session = Depends(get_db)):
    new_product_code = models.Product_Code(**product_code.model_dump())
    try:
        db.add(new_product_code)
        db.commit()
    except Exception as error:
        print(error)
        return "Error adding new product code"
    return "Product code added successfully"

@router.get("/service_codes")
def get_service_codes(db:Session = Depends(get_db)):
    try:
        service_codes = db.query(models.Service_Code).all()
        return service_codes
    except Exception as error:
        print(error)
        return "Error retrieving service codes"

@router.post("/service_codes",status_code=status.HTTP_201_CREATED)
def create_service_code(service_code:schemas.ServiceCode,db:Session = Depends(get_db)):
    new_service_code = models.Service_Code(**service_code.model_dump())
    try:
        db.add(new_service_code)
        db.commit()
    except Exception as error:
        print(error)
        return "Error adding new service code"
    return "Service code added successfully"

@router.post("/states/bulk")
def insert_states(db:Session = Depends(get_db)):
    # CSV -> DataFrame
    df = pd.read_csv("List_of_States.csv")
    # db = get_db()
    # Insert using ORM
    with db:#Session(engine) as session:
        for _, row in df.iterrows():
            record = State_Code(**row.to_dict())
            db.add(record)
            print(record)
        db.commit()

@router.post("/lgas/bulk")
def insert_lgas(db:Session = Depends(get_db)):
    # CSV -> DataFrame
    df = pd.read_csv("List_of_LGAs.csv")
    # db = get_db()
    # Insert using ORM
    with db:#Session(engine) as session:
        for _, row in df.iterrows():
            record = LGA_Code(**row.to_dict())
            db.add(record)
            print(record)
        db.commit()

@router.post("/countries/bulk")
def insert_countries(db:Session = Depends(get_db)):
    # CSV -> DataFrame
    df = pd.read_csv("List_of_Countries.csv")
    # db = get_db()
    # Insert using ORM
    with db:#Session(engine) as session:
        for _, row in df.iterrows():
            record = Country_Code(**row.to_dict())
            db.add(record)
            print(record)
        db.commit()


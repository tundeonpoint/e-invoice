import os
import sys

# Force project root as working directory
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
# os.chdir(BASE_DIR)

# Add project root to Python PATH
sys.path.append(BASE_DIR)

from sqlalchemy import create_engine,Integer,String,Column,Date,DateTime,ForeignKey,DATETIME
from sqlalchemy import Float,JSON,Boolean
from sqlalchemy.orm import declarative_base,relationship
from datetime import datetime
from database import Base

class Organisation(Base):
    __tablename__ = 'organisations'
    id = Column(Integer,primary_key=True)
    business_id = Column(String,nullable=False,unique=True)
    rc_number = Column(String,nullable=False,unique=True)
    tin = Column(String,nullable=False,unique=True)
    name = Column(String,nullable=False,unique=True)
    email = Column(String,nullable=False)
    telephone = Column(String,nullable=False)
    business_description = Column(String)
    zoho_org_id = Column(String,nullable=False,unique=True)
    date_created = Column(DateTime,default=datetime.now())
    address = Column(JSON,default={
            "street_name": "",
            "city_name": "",
            "postal_zone": "",
            "lga": "",
            "state": "",
            "country": ""})
    invoices = relationship('Zoho_Invoice',back_populates='owner',cascade='all,delete-orphan')
    org_secret = Column(String,nullable=False)
    # the hash key is for examining the signature from zoho
    hash_key = Column(String,nullable=False)
    

class Currency(Base):
    __tablename__ = 'currencies'
    id = Column(Integer,primary_key=True)
    symbol = Column(String,nullable=False,unique=True)
    name = Column(String,nullable=False,unique=True)
    symbol_native = Column(String,nullable=False)
    decimal_digits = Column(Float,default=2,nullable=False)
    rounding = Column(Integer,default=0,nullable=False)
    code = Column(String,nullable=False,unique=True)
    name_plural = Column(String,nullable=False,unique=True)

class Invoice_Type(Base):
    __tablename__ = 'invoice_types'
    key = Column(String,primary_key=True)
    value = Column(String,nullable=False)
    description = Column(String,nullable=False)

class Payment_Means(Base):
    __tablename__ = 'payment_means'
    key = Column(String,primary_key=True)
    value = Column(String,nullable=False)
    description = Column(String,nullable=False)

class Tax_Category(Base):
    __tablename__ = 'tax_categories'
    key = Column(String,primary_key=True)
    value = Column(String,nullable=False)
    description = Column(String,nullable=False)

class VAT_Exemption(Base):
    __tablename__ = 'vat_exemptions'
    heading_no = Column(Float,primary_key=True,unique=True)
    harmonized_system_code = Column(Float,nullable=False)
    tarrif_category = Column(String,nullable=False)
    tarrif = Column(String,nullable=False)
    description = Column(String,nullable=False)

class Product_Code(Base):
    __tablename__ = 'product_codes'
    code = Column(String,primary_key=True,unique=True)
    description = Column(String,nullable=False)

class Service_Code(Base):
    __tablename__ = 'service_codes'
    code = Column(String,primary_key=True,unique=True)
    description = Column(String,nullable=False)

class LGA_Code(Base):
    __tablename__ = 'lga_codes'
    name = Column(String,nullable=False,unique=False)
    code = Column(String,primary_key=True)
    state_code = Column(String,ForeignKey('state_codes.code',ondelete='CASCADE'),nullable=False)

class State_Code(Base):
    __tablename__ = 'state_codes'
    name = Column(String,nullable=False,unique=True)
    code = Column(String,primary_key=True)

class Country_Code(Base):
    __tablename__ = 'country_codes'
    name = Column(String,nullable=False,unique=True)
    code = Column(String,primary_key=True)

class User(Base):
    __tablename__ = 'users'
    id = Column(Integer,primary_key=True)
    username = Column(String,nullable=False,unique=True)
    password = Column(String,nullable=True)
    role = Column(String,nullable=False)
    created_at = Column(DateTime,default=datetime.now())

class Zoho_Invoice(Base):
    __tablename__ = 'zoho_invoices'

    # this model will be able to take multiple invoices with the same invoice_id
    # and the same invoice_number because the system will be able to receive updates for
    # each invoice.
    id = Column(Integer,nullable=False,primary_key=True,unique=True)
    business_id = Column(String,ForeignKey('organisations.business_id',ondelete='CASCADE'))
    invoice_id = Column(String,nullable=False)
    invoice_number = Column(String,nullable=False)
    date = Column(DateTime,nullable=False)
    currency_code = Column(String,ForeignKey('currencies.code'),nullable=False)
    tax_type = Column(String,nullable=False,default='tax')
    tax_total = Column(Float,nullable=False,default=0)
    discount_total = Column(Float,nullable=False,default=0)
    total = Column(Float,nullable=False)
    created_at = Column(DateTime,default=datetime.now())
    zoho_org_id = Column(String,nullable=False,unique=False)
    # line_items = relationship('Zoho_Invoice_Line_Item',back_populates='invoice')
    line_items = Column(JSON,nullable=False)
    sub_total = Column(Float,nullable=False)
    bcy_discount_total = Column(Float,nullable=False)
    bcy_total = Column(Float,nullable=False)
    total = Column(Float,nullable=False)
    due_date = Column(Date)
    accounting_cost = Column(String,default='')
    customer_name = Column(String,default='')
    customer_id = Column(String)
    email = Column(String,default='')
    notes = Column(String,default='')
    customer_default_billing_address = Column(JSON,default={
        "zip": "",
        "country": "",
        "address": "",
        "city": "",
        "phone": "",
        "street2": "",
        "state": "",
        "fax": "",
        "state_code": ""})
    # full_invoice = Column(JSON)#this is for an experiment to view the entire structure
    status = Column(String)# this is one of paid,sent,rejected etc
    send_status = Column(Boolean,default=False)
    send_treatment = Column(Integer,default=1)#actions can either be 1 (for create) or 2 (for update)
    owner = relationship('Organisation',back_populates='invoices')

    def __init__(self, **kwargs):
        # Define the fields to include in the constructor
        allowed_fields = ['business_id','invoice_id','invoice_number','date','currency_code','tax_type','tax_total','discount_total','total','created_at','zoho_org_id','sub_total','bcy_discount_total','bcy_total','total','due_date','accounting_cost','customer_name','email','customer_default_billing_address','notes','customer_id','status'] 
    

        # Iterate through allowed fields and assign if present in kwargs
        for field in allowed_fields:
            if field in kwargs:
                setattr(self, field, kwargs[field])

class Invoice_Map(Base):
    __tablename__ = 'invoice_maps'
    id = Column(Integer,primary_key=True,nullable=False)
    zoho_org_id = Column(String,nullable=False)
    zoho_invoice_number = Column(String,nullable=False)
    irn = Column(String,nullable=False)
    retrieve_status = Column(Boolean,default=False)
    submission_date = Column(DateTime)

    def to_dict(self):
        return {
            "id":self.id,
            "zoho_org_id":self.zoho_org_id,
            "zoho_invoice_number":self.zoho_invoice_number,
            "irn":self.irn,
            "retrieve_status":self.retrieve_status,
            "submission_date":self.submission_date
        }
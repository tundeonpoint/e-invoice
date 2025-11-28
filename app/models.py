import os
import sys

# Force project root as working directory
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
# os.chdir(BASE_DIR)

# Add project root to Python PATH
sys.path.append(BASE_DIR)

from sqlalchemy import create_engine,Table,MetaData,Integer,String,Column,Date,DateTime,ForeignKey,DATETIME
from sqlalchemy import Float,JSON,Time,Boolean
from sqlalchemy.orm import declarative_base,sessionmaker,relationship,Session
import psycopg2
from datetime import date,datetime
import time
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
    invoices = relationship('Zoho_Invoice',back_populates='owner')
    org_secret = Column(String,nullable=False)

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
    state_code = Column(String,ForeignKey('state_codes.code'),nullable=False)

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
    email = Column(String,nullable=False,unique=True)
    password = Column(String,nullable=False)
    created_at = Column(DateTime,default=datetime.now())

class Zoho_Invoice(Base):
    __tablename__ = 'zoho_invoices'

    # this model will be able to take multiple invoices with the same invoice_id
    # and the same invoice_number because the system will be able to receive updates for
    # each invoice.
    id = Column(Integer,nullable=False,primary_key=True,unique=True)
    business_id = Column(String,ForeignKey('organisations.business_id'))
    invoice_id = Column(String,nullable=False)
    invoice_number = Column(String,nullable=False)
    date = Column(DateTime,nullable=False)
    currency_code = Column(String,nullable=False)
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
     
   
# class Zoho_Invoice_Line_Item(Base):
#     __tablename__ = 'zoho_invoice_line_items'

#     invoice_id = Column(String,ForeignKey('zoho_invoices.invoice_id'),nullable=False)
#     line_item_id = Column(String,primary_key=True,nullable=False,unique=True)
#     # "documents": [],
#     item_type = Column(String)
#     item_type_formatted = Column(String)#: "Sales Items (Service)",
#     discount = Column(Float,default=0,nullable=False)
#     # "mapped_items": [],
#     internal_name = Column(String,default="")#: "",
#     sales_rate_formatted = Column(String,default="")
#     # "discounts": [],
#     project_id = Column(String,default="")
#     pricing_scheme = Column(String,default="")#: "unit",
#     pricebook_id = Column(String,default="")
#     bill_id = Column(String,default="")
#     bcy_rate_formatted = Column(String,default="")
#     image_document_id = Column(String,default="")
#     expense_receipt_name = Column(String,default="")
#     item_total = Column(Float,default=0)
#     tax_id = Column(String,default="")
#     # "tags": [],
#     unit = Column(String,default="")
#     cost_amount = Column(Float,default=0)
#     tax_type = Column(String,default="")
#     # "time_entry_ids": [],
#     cost_amount_formatted = Column(String,default="")
#     name = Column(String,default="")# description of line item: "Consulting Services",
#     markup_percent_formatted = Column(String,default="")#: "0.00%",
#     bcy_rate = Column(Float,default="")#: 100000,
#     item_total_formatted = Column(String,default="")#: "NGN100,000.00",
#     salesorder_item_id = Column(String,default="")#: "",
#     discount_account_name = Column(String,default="")#: "",
#     rate_formatted = Column(String,default="")#: "NGN100,000.00",
#     header_id = Column(String,default="")#: "",
#     discount_account_id = Column(String,default="")#: "",
#     description = Column(String,default="")#: "",
#     item_order = Column(Float,default=0)#: 1,
#     bill_item_id = Column(String,default="")#: "",
#     rate = Column(Float,default=0)#: 100000,
#     account_name = Column(String,default="")#: "Sales",
#     sales_rate = Column(Float,default=0)#: 100000,
#     quantity = Column(Float,default=1)#: 1,
#     item_id = Column(String,default="")#: "7228477000000096025",
#     tax_name = Column(String,default="")#: "",
#     header_name = Column(String,default="")#: "",
#     # "item_custom_fields": [],
#     # "line_item_taxes": [],
#     markup_percent = Column(Float,default=0)#: 0,
#     account_id = Column(String,default="")# "7228477000000000388",
#     tax_percentage = Column(Float,default=0)#: 0,
#     expense_id = Column(String,default="")#: ""

#     # invoice = relationship('Zoho_Invoice',back_populates='line_items')
#     # line_item_taxes = relationship('Zoho_Invoice_Line_Item_Tax',back_populates='line_item')

#     def __init__(self, **kwargs):
#         # Define the fields to include in the constructor
#         allowed_fields = ['line_item_id', 'item_type', 'item_type_formatted',
#                           'discount', 'internal_name', 'sales_rate_formatted',
#                           'project_id', 'pricing_scheme', 'pricebook_id', 'bill_id',
#                           'bcy_rate_formatted', 'image_document_id', 'expense_receipt_name',
#                           'item_total', 'tax_id', 'unit', 'cost_amount', 'tax_type',
#                           'cost_amount_formatted', 'name', 'markup_percent_formatted',
#                           'bcy_rate', 'item_total_formatted', 'salesorder_item_id',
#                           'discount_account_name', 'rate_formatted', 'header_id', 'discount_account_id',
#                           'description', 'item_order', 'bill_item_id', 'rate', 'account_name',
#                           'sales_rate', 'quantity', 'item_id', 'tax_name', 'header_name',
#                           'markup_percent', 'account_id','tax_percentage', 'expense_id'] 
        
#         # Iterate through allowed fields and assign if present in kwargs
#         for field in allowed_fields:
#             if field in kwargs:
#                 setattr(self, field, kwargs[field])

# class Zoho_Invoice_Line_Item_Tax(Base):
#     __tablename__ = 'zoho_invoice_line_item_taxes'

#     id = Column(Integer,primary_key=True,nullable=False,unique=True)
#     line_item_id = Column(String,ForeignKey('zoho_invoice_line_items.line_item_id'),nullable=False)
#     tax_amount = Column(Float,nullable=False)
#     tax_specific_type = Column(String)
#     tax_name = Column(String) #"VAT (7.5%)"
#     tax_amount_formatted =Column(String)# "NGN900.00",
#     tax_percentage = Column(Float,nullable=False)#: 7.5
#     tax_id = Column(String,nullable=False)
    # line_item = relationship('Zoho_Invoice_Line_Item',back_populates='line_item_taxes')

# while True:
#     try:
#         Base.metadata.create_all(engine)
#         print('Database connection successful')
#         break
#     except Exception as error:
#         print('Connecting to database failed')
#         print(error)
#         time.sleep(2)

# new_invoice = Invoice(

# business_id = 'azt126',irn = '20251017VVB3006',issue_date = date(2025,10,17),
# document_currency_code = 'NGN',invoice_type_code = 'TLO',tax_currency_code = 'NGN',
# accounting_supplier_party = 'azt125',tax_total = 500.00,legal_monetary_total = 500.00
# ) 


# class InvoiceRecord(Base):
#     __tablename__ = "invoice_records"

#     id = Column(Integer, primary_key=True, index=True)
#     payload = Column(JSON, nullable=False)        # JSON payload
#     send_status = Column(Boolean, default=False)       # False = unprocessed, True = sent

# class Invoice(Base):
#     __tablename__ = 'invoices'
#     id = Column(Integer,primary_key=True)
#     business_id = Column(String,ForeignKey('organisations.business_id',ondelete='CASCADE'),nullable=False)
#     irn = Column(String,nullable=False,unique=True)
#     issue_date = Column(Date,nullable=False)#this date needs to be converted to YYYY-MM-DD
#     due_date = Column(Date,default=datetime.now().date())#this date needs to be converted to YYYY-MM-DD
#     issue_time = Column(Time)#extract the time component of the issue date from this
#     invoice_type_code = Column(String,ForeignKey('invoice_types.key'),nullable=False)
#     payment_status = Column(String,nullable=False,default='PENDING') 
#     note = Column(String,default='')
#     tax_point_date = Column(Date,default=datetime.now().date())
#     document_currency_code = Column(String,ForeignKey('currencies.code'),nullable=False,default='NGN')
#     tax_currency_code = Column(String,ForeignKey('currencies.code'),nullable=False,default='NGN')
#     accounting_cost = Column(String,default='')
#     buyer_reference = Column(String,default='')
#     invoice_delivery_period = Column(String,default='')
#     order_reference = Column(String,default='')
#     billing_reference = Column(String,default='') 
#     dispatch_document_reference = Column(String,default='') 
#     receipt_document_reference = Column(String,default='')
#     originator_document_reference = Column(String,default='')
#     contract_document_reference = Column(String,default='')
#     additional_document_reference = Column(String,default='')
#     accounting_customer_party = Column(JSON,default={
#                 "party_name": "",
#                 "tin": "",
#                 "email": "",
#                 "telephone": "",
#                 "business_description": "",
#                 "postal_address": {
#                     "street_name": "",
#                     "city_name": "",
#                     "postal_zone": "",
#                     "lga": "",
#                     "state": "",
#                     "country": ""
#                 }
#                 })
#     accounting_supplier_party = Column(JSON,nullable=False,default={
#                 "party_name": "",
#                 "tin": "",
#                 "email": "",
#                 "telephone": "",
#                 "business_description": "",
#                 "postal_address": {
#                     "street_name": "",
#                     "city_name": "",
#                     "postal_zone": "",
#                     "lga": "",
#                     "state": "",
#                     "country": ""
#                 }
#                 })
#     payee_party = Column(JSON,default={
#                 "party_name": "",
#                 "tin": "",
#                 "email": "",
#                 "telephone": "",
#                 "business_description": "",
#                 "postal_address": {
#                     "street_name": "",
#                     "city_name": "",
#                     "postal_zone": "",
#                     "lga": "",
#                     "state": "",
#                     "country": ""
#                 }
#                 }) #this should reference the organisation table
#     bill_party = Column(JSON,default={
#                 "party_name": "",
#                 "tin": "",
#                 "email": "",
#                 "telephone": "",
#                 "business_description": "",
#                 "postal_address": {
#                     "street_name": "",
#                     "city_name": "",
#                     "postal_zone": "",
#                     "lga": "",
#                     "state": "",
#                     "country": ""
#                 }
#                 }) #this should reference the organisation table 
#     ship_party = Column(JSON,default={
#                 "party_name": "",
#                 "tin": "",
#                 "email": "",
#                 "telephone": "",
#                 "business_description": "",
#                 "postal_address": {
#                     "street_name": "",
#                     "city_name": "",
#                     "postal_zone": "",
#                     "lga": "",
#                     "state": "",
#                     "country": ""
#                 }
#                 }) #this should reference the organisation table 
#     tax_representative_party = Column(JSON,default={
#                 "party_name": "",
#                 "tin": "",
#                 "email": "",
#                 "telephone": "",
#                 "business_description": "",
#                 "postal_address": {
#                     "street_name": "",
#                     "city_name": "",
#                     "postal_zone": "",
#                     "lga": "",
#                     "state": "",
#                     "country": ""
#                 }
#                 }) #this should reference the organisation table 
#     actual_delivery_date = Column(Date) #this should reference the organisation table 
#     payment_means = Column(String,ForeignKey('payment_means.key'),nullable=False,default='30') #a list of dictionaries containing payment means code, and payment due date in yyyy-mm-dd format 
#     payment_terms_note = Column(String,default='') 
#     allowance_charge = Column(JSON,default=[]) #a list of dictionaries containing charge_indicator (bolean) and amount (float) 
#     tax_total = Column(JSON)#references a table which should contain a breakdown of taxes charged against a particular invoice 
#     legal_monetary_total = Column(JSON,nullable=False)#references a structure containing a breakedown of the total to be remitted 
#     created_at = Column(DateTime,default=datetime.now())
#     owner = relationship('Organisation',back_populates='invoices')
#     # creator = Column(Integer,nullable=False)
#     line_items = Column(JSON)#relationship('Invoice_Line_Item',back_populates='invoice')

# class Invoice_Submission_Status(Base):
#     __tablename__ = 'invoice_submission_status'
#     # this class is required to eliminate any additional work
#     # involved in stripping out the following columns before submission to
#     # e-invoice platform
#     irn = Column(String,ForeignKey('invoices.irn'),nullable=False,unique=True,primary_key=True)
#     submission_status = Column(Boolean,default=False)
#     submission_datetime = Column(DateTime)

# class Invoice_Line_Item(Base):
#     __tablename__ = 'invoice_line_items'
#     id = Column(Integer,primary_key=True)
#     hsn_code = Column(String,nullable=False)#mandatory field
#     product_category = Column(String,nullable=False)#mandatory
#     isic_code =	Column(Integer,nullable=False)#mandatory
#     service_category = Column(String,nullable=False)#mandatory
#     discount_rate =	Column(Float,default=0,nullable=False)#mandatory
#     discount_amount = Column(Float,default=0,nullable=False)#mandatory
#     fee_rate = Column(Float,default=0,nullable=False)#mandatory
#     fee_amount = Column(Float,default=0,nullable=False)#	mandatory
#     invoiced_quantity = Column(Float,nullable=False)#mandatory
#     line_extension_amount =	Column(Float,nullable=False)#mandatory
#     item = Column(JSON,nullable=False)#	mandatory
#     price =	Column(JSON,nullable=False)#mandatory
#     invoice_id = Column(String,ForeignKey('invoices.irn'),nullable=False)
#     # invoice = relationship('Invoice',back_populates='line_items')



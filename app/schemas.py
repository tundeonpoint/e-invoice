from pydantic import BaseModel,EmailStr,ConfigDict,Field
from datetime import datetime,date,time
from typing import Optional
import json


class Invoice(BaseModel):
    business_id : str
    irn : str
    issue_date : date
    issue_time : time
    due_date : date
    note : str
    tax_point_date : date
    accounting_cost : str
    buyer_reference : str
    invoice_delivery_period : str
    dispatch_document_reference : str 
    receipt_document_reference : str
    originator_document_reference : str
    contract_document_reference : str
    additional_document_reference : str 
    accounting_customer_party : dict
    accounting_supplier_party : dict
    payee_party : dict #this should reference the organisation table
    bill_party : dict #this should reference the organisation table 
    ship_party : dict #this should reference the organisation table 
    tax_representative_party : dict #this should reference the organisation table 
    # actual_delivery_date : date #this should reference the organisation table 
    payment_means : str #a list of dictionaries containing payment means code, and payment due date in yyyy-mm-dd format 
    payment_terms_note : str 
    allowance_charge : list #a list of dictionaries containing charge_indicator (bolean) and amount (float) 
    tax_total : dict#references a table which should contain a breakdown of taxes charged against a particular invoice 
    legal_monetary_total : dict#references a structure containing a breakedown of the total to be remitted 
    created_at : datetime
    # owner = relationship('Organisation',back_populates='invoices')
    # creator = Column(Integer,nullable=False)
    line_items : list#relationship('Invoice_Line_Item',back_populates='invoice')
    document_currency_code : str
    invoice_type_code : str
    tax_currency_code : str
    accounting_supplier_party : dict
    tax_total : list
    legal_monetary_total : dict
    payment_means : str
    payment_status : str
    # creator : int

    model_config = ConfigDict(from_attributes=True)


class InvoiceCreate(BaseModel):
    business_id : str
    irn : str
    issue_date : date
    document_currency_code : str
    invoice_type_code : str
    tax_currency_code : str
    accounting_supplier_party : str
    tax_total : float
    legal_monetary_total : float
    payment_means : str
    payment_status : str

    model_config = ConfigDict(from_attributes=True)

class ZohoInvoiceCreate(BaseModel):
    invoice_id : str
    invoice_number : str
    date : date
    currency_code : str
    tax_type : str
    tax_total : float
    discount_total : float
    total : float
    # currency_code = Column(String,nullable=False)
    # tax_type = Column(String,nullable=False,default='tax')
    # tax_total = Column(Float,nullable=False,default=0)
    # discount_total = Column(Float,nullable=False,default=0)
    # total = Column(Float,nullable=False)
    # created_at = Column(DateTime,default=datetime.now())
    # zoho_org_id = Column(String,nullable=False,unique=False)
    # line_items = relationship('Zoho_Invoice_Line_Item',back_populates='invoice')
    # sub_total = Column(Float,nullable=False)
    # bcy_discount_total = Column(Float,nullable=False)
    # bcy_total = Column(Float,nullable=False)
    # total = Column(Float,nullable=False)
    # due_date = Column(Date)
    # accounting_cost = Column(String,default='')
    # customer_name = Column(String,default='')
    # email = Column(String,default='')
    # customer_default_billing_address = Column(JSON,default={
    #     "zip": "",
    #     "country": "",
    #     "address": "",
    #     "city": "",
    #     "phone": "",
    #     "street2": "",
    #     "state": "",
    #     "fax": "",
    #     "state_code": ""})


class ZohoInvoice(BaseModel):
    business_id : str
    invoice_id : str
    invoice_number : str
    date : date
    currency_code : str
    tax_type : str
    tax_total : float
    discount_total : float
    total : float
    created_at : datetime

class ZohoInvoiceLineItem(BaseModel):
    invoice_id : str# Column(String,ForeignKey('zoho_invoices.invoice_id'),nullable=False)
    line_item_id : str#= Column(String,primary_key=True,nullable=False)
    # "documents": [],
    item_type : str#= Column(String)
    item_type_formatted : str#= Column(String)#: "Sales Items (Service)",
    discount : float#= Column(Float,default=0,nullable=False)
    # "mapped_items": [],
    internal_name : str#= Column(String,default="")#: "",
    sales_rate_formatted : str#= Column(String,default="")
    # "discounts": [],
    project_id : str#= Column(String,default="")
    pricing_scheme : str#= Column(String,default="")#: "unit",
    pricebook_id : str#= Column(String,default="")
    bill_id : str#= Column(String,default="")
    bcy_rate_formatted : str#= Column(String,default="")
    image_document_id : str#= Column(String,default="")
    expense_receipt_name : str#= Column(String,default="")
    item_total : float#= Column(Float,default=0)
    tax_id : str#= Column(String,default="")
    # "tags": [],
    unit : str#= Column(String,default="")
    cost_amount : float#= Column(Float,default=0)
    tax_type : str#= Column(String,default="")
    # "time_entry_ids": [],
    cost_amount_formatted : str#= Column(String,default="")
    name : str#= Column(String,default="")# description of line item: "Consulting Services",
    markup_percent_formatted : str#= Column(String,default="")#: "0.00%",
    bcy_rate : float#= Column(Float,default="")#: 100000,
    item_total_formatted : str#= Column(String,default="")#: "NGN100,000.00",
    salesorder_item_id : str#= Column(String,default="")#: "",
    discount_account_name : str#= Column(String,default="")#: "",
    rate_formatted : str#= Column(String,default="")#: "NGN100,000.00",
    header_id : str#= Column(String,default="")#: "",
    discount_account_id : str#= Column(String,default="")#: "",
    description : str#= Column(String,default="")#: "",
    item_order : float#= Column(Float,default=0)#: 1,
    bill_item_id : str#= Column(String,default="")#: "",
    rate : float#= Column(Float,default=0)#: 100000,
    account_name : str# = Column(String,default="")#: "Sales",
    sales_rate : float#= Column(Float,default=0)#: 100000,
    quantity : str#= Column(String,default=1)#: 1,
    item_id : str#]= Column(String,default="")#: "7228477000000096025",
    tax_name : str#= Column(String,default="")#: "",
    header_name : str#= Column(String,default="")#: "",
    # "item_custom_fields": [],
    # "line_item_taxes": [],
    markup_percent : float#= Column(Float,default=0)#: 0,
    account_id : str#= Column(String,default="")# "7228477000000000388",
    tax_percentage : float#= Column(Float,default=0)#: 0,
    expense_id : str#= Column(String,default="")#: ""


class InvoiceType(BaseModel):
    key : str
    value : str
    description : str

class PaymentMeans(BaseModel):
    key : str
    value : str
    description : str

class TaxCategory(BaseModel):
    key : str
    value : str
    description : str

class StateCode(BaseModel):
    name : str
    code : str

class LGACode(BaseModel):
    name : str
    code : str
    state_code : str

class VATExemption(BaseModel):
    heading_no:float
    harmonized_system_code:float
    tarrif_category:str
    tarrif:str
    description:str

class ProductCode(BaseModel):
    code:str
    description:str

class ServiceCode(BaseModel):
    code:str
    description:str

class Currency(BaseModel):
    id : int
    symbol : str
    name : str
    symbol_native : str
    decimal_digits : float
    rounding : int
    code : str
    name_plural : str

class CurrencyCreate(BaseModel):
    symbol : str
    name : str
    symbol_native : str
    decimal_digits : float
    rounding : int
    code : str
    name_plural : str

class UserCreate(BaseModel):
    email:EmailStr
    password:str
    
    model_config = ConfigDict(from_attributes=True)

class UserOut(BaseModel):
    id:int
    email:EmailStr
    created_at:datetime

class UserLogin(BaseModel):
    email:EmailStr
    password:str

class Token(BaseModel):
    access_token:str
    token_type:str

class TokenData(BaseModel):
    user_id: Optional[str] = None
    
class OrganisationCreate(BaseModel):
    business_id : str
    rc_number : str
    tin : str
    name : str
    email : EmailStr
    telephone : str
    business_description : str
    zoho_org_id : str
    address : dict
    # org_secret : str

class OrganisationOut(BaseModel):
    id : int
    business_id : str
    rc_number : str
    tin : str
    name : str
    email : EmailStr
    telephone : str
    business_description : str
    zoho_org_id : str
    address : dict

class CommonHeaders(BaseModel):
    host : str
    org_id : Optional[str] = Field(None,alias="Org-Id")
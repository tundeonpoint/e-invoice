# import fastapi,sqlalchemy
from fastapi import Depends,HTTPException,status,Response,APIRouter,Header,Request
# from app import models,utils
from ..database import get_db
from sqlalchemy.orm import Session,declarative_base
from .. import models,utils,schemas
from passlib.hash import pbkdf2_sha256
from fastapi.security.oauth2 import OAuth2PasswordRequestForm
from . import oauth2,auth
from typing import List
from sqlalchemy import Date,Time,cast
import json
import re
from datetime import datetime

router = APIRouter(tags=['Invoices'],
                   prefix="/invoices")

@router.get("",status_code=status.HTTP_200_OK,response_model=List[schemas.Invoice])
def get_invoices(db:Session = Depends(get_db),
                 current_user:int = Depends(oauth2.get_current_user)):
    results = db.query(models.Invoice).all()
    print(f'current user: {current_user.email}')
    return results

@router.get("/{inv_id}",status_code=status.HTTP_200_OK,response_model=schemas.Invoice)
def get_spec_invoices(inv_id,response:Response,
                      db:Session = Depends(get_db),current_user:int = Depends(oauth2.get_current_user)):
    # get_invoices(par_id)
    result = db.query(models.Invoice).where(models.Invoice.irn==inv_id).first()
    if result == None:
        raise HTTPException(status.HTTP_404_NOT_FOUND,
                            detail = f'Invoice number {inv_id} not found')
    
    return result

@router.get("/{inv_id}/orgs/{org_id}",status_code=status.HTTP_200_OK)
def get_org_invoice(inv_id = None,org_id = None,db:Session=Depends(get_db)):

    result = db.query(models.Zoho_Invoice).filter(models.Zoho_Invoice.zoho_org_id == org_id).filter(models.Zoho_Invoice.invoice_number == inv_id).first()

    if result == None:
        return "No invoices found"
    else:
        return result#create_arca_invoice(result,db)

    # return f"invoice id {inv_id} returned for {org_id} "
@router.post("/full_invoice",status_code=status.HTTP_200_OK)
def post_full_invoice(inv_id = None,org_id = None,db:Session=Depends(get_db)):

    result = db.query(models.Zoho_Invoice).filter(models.Zoho_Invoice.zoho_org_id == org_id).filter(models.Zoho_Invoice.invoice_number == inv_id).first()

    if result == None:
        return "No invoices found"
    else:
        return result#create_arca_invoice(result,db)

    # return f"invoice id {inv_id} returned for {org_id} "

def convert_zoho_invoice(zoho_invoice:models.Zoho_Invoice,db:Session) -> models.Invoice:

    # convert the zoho invoice to FIRS invoice format

    n_invoice = models.Invoice()
    result = db.query(models.Organisation).filter(models.Organisation.zoho_org_id == zoho_invoice.zoho_org_id).first()
    
    # populate the invoice components
    n_invoice.business_id = result.business_id
    n_invoice.issue_date = zoho_invoice.date.date()
    n_invoice.issue_time = zoho_invoice.date.time()
    n_invoice.irn = zoho_invoice.invoice_number+'-'+n_invoice.business_id+'-'+n_invoice.issue_date.strftime('%Y%m%d')
    n_invoice.document_currency_code = zoho_invoice.currency_code
    n_invoice.tax_currency_code = zoho_invoice.currency_code#this is a default value which needs to be updated
    n_invoice.invoice_type_code = '550' #this is a default value which needs to be updated
    n_invoice.payment_means = '30' #this is a default value which needs to be updated
    n_invoice.legal_monetary_total = {
        "line_extension_amount": zoho_invoice.sub_total,
        "tax_exclusive_amount": zoho_invoice.sub_total,
        "tax_inclusive_amount": zoho_invoice.total,
        "payable_amount": zoho_invoice.total

    }
    n_invoice.accounting_customer_party = {
            "party_name": zoho_invoice.customer_name,
            # "tin": "",
            "email": zoho_invoice.email,
            "telephone": zoho_invoice.customer_default_billing_address['phone'],
            "business_description": "",
            "postal_address": {
                "street_name": zoho_invoice.customer_default_billing_address['address'] + " " +
                zoho_invoice.customer_default_billing_address['street2'],
                "city_name": zoho_invoice.customer_default_billing_address['city'],
                "postal_zone": zoho_invoice.customer_default_billing_address['zip'],
                "lga": "",
                "state": zoho_invoice.customer_default_billing_address['state'],
                "country": zoho_invoice.customer_default_billing_address['country']
            }
    }
    #construct the e-invoice tax_total object
    tax_total_list = []
    tax_total = {}
    invoice_line_items = []
    
    for line_item in zoho_invoice.line_items:
        
        tax_subtotal_list = []

        tax_total['tax_amount'] = 0

        invoice_line_items.append(

            {
                # "id": idx,  # or item.get("line_item_id") if you prefer Zoho ID
                "hsn_code": "hsn code placeholder",#item.get("item_id", "UNKNOWN"),  # No explicit HSN in JSON, so using item_id
                "product_category": "product category placeholder",#item.get("item_type_formatted", "General"),
                "isic_code": 9999,  # Placeholder: ISIC not in Zoho JSON
                "service_category": "service category placeholder",#item.get("name", "Unknown Service"),
                "discount_rate": 0.0,
                "discount_amount": line_item.discount,  # Not directly in JSON; can be computed if needed
                "fee_rate": 0.0,  # No such field in Zoho JSON
                "fee_amount": 0.0,
                "invoiced_quantity": line_item.quantity,#float(item.get("quantity", 0)),
                "line_extension_amount": line_item.item_total,#float(item.get("item_total", 0)),
                "invoice_id" : n_invoice.irn,
                "item": {
                    "name": line_item.name,
                    "description": line_item.description,
                    "sellers_item_identification": line_item.name
                },
                "price": {
                    "price_amount": line_item.rate,
                    "base_quantity": 1,
                    "price_unit": n_invoice.document_currency_code + " per 1"
                }
            }

        
        )

        # create the line_items for the FIRS e-invoice

        line_item_tax_total = 0

        for line_item_tax in line_item.line_item_taxes:
            
            line_item_tax_total += line_item_tax.tax_amount

            tax_subtotal_list.append({
                "taxable_amount": line_item.item_total,
                "tax_amount": line_item_tax.tax_amount,
                "tax_category": {
                    "id": str.strip(re.sub(r'\([^)]*\)', '', line_item_tax.tax_name)),
                    "percent": line_item_tax.tax_percentage
                }
            })
               
        tax_total_list.append(
            {
                "tax_amount":line_item_tax_total,
                "tax_subtotal":tax_subtotal_list
            }
        )
    n_invoice.note = zoho_invoice.notes
    n_invoice.line_items = invoice_line_items
    n_invoice.tax_total = tax_total_list

    # add invoice supplier party info
    n_invoice.accounting_supplier_party = {
        "party_name": result.name,
        "tin": result.tin,
        "email": result.email,
        "telephone": result.telephone,
        "business_description": result.business_description,
        "postal_address": {
            "street_name": result.address['line_1'],
            "city_name": result.address['line_2'],
            "postal_zone": result.address['postal_code'],
            "lga": result.address['lga'],
            "state": result.address['state'],
            "country": result.address['country']
        }

    }

    db.add(n_invoice)
    db.commit()
    
    return n_invoice

def create_arca_invoice(zoho_invoice:models.Zoho_Invoice,db:Session) -> dict:

    n_invoice = models.Invoice()
    result = db.query(models.Organisation).filter(models.Organisation.zoho_org_id == zoho_invoice.zoho_org_id).first()
    arca_invoice = {}
    payment_status = ''
    # capture the payment status value
    match zoho_invoice.status:
        case 'paid':
            payment_status = 'PAID'
        case 'void':
            payment_status = 'REJECTED'
        case 'rejected':
            payment_status = 'REJECTED'
        case _:
            payment_status = 'PENDING'
    # populate the invoice components
    arca_invoice = {

        "requestType": "MINIMAL",
        "invoiceNumber": str.strip(re.sub(r'\([^)]*\)', '', zoho_invoice.invoice_number)),#zoho_invoice.invoice_number,
        "invoiceBusinessId": result.business_id,
        "invoiceEntityId": "entity_id_placeholder",
        "invoiceIssueDate": zoho_invoice.date.date(),
        "invoiceDueDate": zoho_invoice.due_date,
        "invoiceIssueTime": zoho_invoice.date.time(),
        "invoiceTypeCode": "550",
        "invoiceNote":zoho_invoice.notes,
        "invoicePaymentStatus": payment_status,
        "invoiceTaxPointDate": datetime.now().date(),
        "invoiceDocumentCurrencyCode": zoho_invoice.currency_code,
        "invoiceTaxCurrencyCode": zoho_invoice.currency_code,
        # n_invoice.irn = zoho_invoice.invoice_number+'-'+result.business_id+'-'+zoho_invoice.date.cast(Date).strftime('%Y%m%d')
        # n_invoice.payment_means : '30' #this is a default value which needs to be updated
        "invoiceCustomerPartyId":zoho_invoice.customer_id,
        "invoiceCustomerPartyName": zoho_invoice.customer_name,
        # "tin": "",
        "invoiceCustomerPartyEmail": zoho_invoice.email,
        "invoiceCustomerPartyTelephone": zoho_invoice.customer_default_billing_address['phone'],
        "invoiceCustomerPartyBusinessDescription": "",
        "invoiceCustomerStreetName": zoho_invoice.customer_default_billing_address['address'] + " " +
        zoho_invoice.customer_default_billing_address['street2'],
        "invoiceCustomerCityName": zoho_invoice.customer_default_billing_address['city'],
        "invoiceCustomerPostalZone": zoho_invoice.customer_default_billing_address['zip'],
        "invoiceCustomerLga": "N/A",
        "invoiceCustomerState": zoho_invoice.customer_default_billing_address['state'],
        "invoiceCustomerCountry": zoho_invoice.customer_default_billing_address['country'],

        "invoiceSupplierPartyId": result.business_id,
        "invoiceSupplierPartyName": result.name,
        "invoiceSupplierPartyTin": result.tin,
        "invoiceSupplierPartyEmail": result.email,
        "invoiceSupplierPartyTelephone": result.telephone,
        "invoiceSupplierPartyBusinessDescription": 'business description placeholder',#result.business_description,
        "invoiceSupplierStreetName": result.address['line_1'],
        "invoiceSupplierCityName": result.address['line_2'],
        "invoiceSupplierPostalZone": result.address['postal_code'],
        "invoiceSupplierLga": result.address['lga'],
        "invoiceSupplierState": result.address['state'],
        "invoiceSupplierCountry": result.address['country'],

        "invoiceLineExtensionAmount": zoho_invoice.sub_total,
        "invoiceTaxExclusiveAmount": zoho_invoice.sub_total,
        "invoiceTaxInclusiveAmount": zoho_invoice.total,
        "invoicePayableAmount": zoho_invoice.total,

        # "allowance_charge":[],#to be revisited


    }
    n_invoice.legal_monetary_total = {
        "line_extension_amount": zoho_invoice.sub_total,
        "tax_exclusive_amount": zoho_invoice.sub_total,
        "tax_inclusive_amount": zoho_invoice.total,
        "payable_amount": zoho_invoice.total

    }
    #construct the e-invoice tax_total object
    tax_total_list = []
    tax_total = {}
    invoice_line_items = []
    allowance_charges = []

    for line_item in zoho_invoice.line_items:
        
        tax_subtotal_list = []

        tax_total['tax_amount'] = 0

        invoice_line_items.append(

            {
                "invoiceLineHsnCode": "hsn code placeholder",#item.get("item_id", "UNKNOWN"),  # 
                "invoiceLineProductCategory": "product category placeholder",#item.get("item_type_formatted", "General
                "invoiceLineInvoicedQuantity": line_item['quantity'],#float(item.get("quantity", 0)),
                "invoiceLineExtensionAmount": line_item['item_total'],#float(item.get("item_total", 0)),
                "invoiceLineItemName": line_item['name'],
                "invoiceLineItemDescription": line_item['description'],
                "invoiceLinePriceAmount": line_item['rate'],
                "invoiceLinePriceBaseQuantity": 1.0,
                "invoiceLinePriceUnit": zoho_invoice.currency_code + " per 1"
            }

        
        )

        for discount in line_item['discounts']:

            allowance_charges.append(
            {
                "invoiceAllowanceChargeIndicator": False,
                "invoiceAllowanceChargeAmount": float(discount['discount_amount']),
            }
        )
    # invoice_line_items
    
        # create the line_items for the FIRS e-invoice

        line_item_tax_total = 0

        for line_item_tax in line_item['line_item_taxes']:
            
            line_item_tax_total += line_item_tax['tax_amount']

            tax_subtotal_list.append({
                # "tax_amount": line_item_tax['tax_amount'],
                "tax_subtotal": {
                    "taxSubTotalTaxAmount": line_item_tax['tax_amount'],
                    "taxSubTotalTaxableAmount": line_item['item_total'],
                    "taxSubTotalCategoryId": str.strip(re.sub(r'\([^)]*\)', '', line_item_tax['tax_name'])),
                    "taxSubTotalCategoryPercent": line_item_tax['tax_percentage']
                }
            })
               
        tax_total_list.append(
            {
                "invoiceTaxTotalAmount":line_item_tax_total,
                "invoiceTaxTotalSubTotal":tax_subtotal_list
            }
        )
    arca_invoice["invoiceLine"] = invoice_line_items
    arca_invoice["invoiceTaxTotal"] = tax_total_list
    arca_invoice["invoiceAllowanceCharge"] = allowance_charges
    
    return arca_invoice


@router.post("",status_code=status.HTTP_201_CREATED)#,response_model=schemas.Invoice)
async def create_zoho_invoice(request:Request,invoice:dict,org_id : str = Depends(auth.verify_org),
                              db:Session = Depends(get_db)):

    org_info = db.query(models.Organisation).filter(models.Organisation.zoho_org_id == org_id).first()
    if org_info == None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail='Invalid Org Id.')
    
    n_zohoinvoice = models.Zoho_Invoice(**invoice['invoice'])#['invoice'])
    # print(f'*******due date:{n_zohoinvoice.du}')
    n_zohoinvoice.zoho_org_id = org_id
    n_zohoinvoice.business_id = org_info.business_id
    n_zohoinvoice.line_items = invoice["invoice"]["line_items"]
    # n_zohoinvoice.full_invoice = invoice

    # db.
    try:
        db.add(n_zohoinvoice)

        db.commit()
    except Exception as error:
        print(error)
        raise HTTPException(status_code=status.HTTP_406_NOT_ACCEPTABLE,
                            detail='Error adding invoice.')
    
    # convert the invoice to an e-invoice format and store it
    # c_invoice = convert_zoho_invoice(n_zohoinvoice,db)
    arca_invoice = create_arca_invoice(n_zohoinvoice,db)
    # print(f'********* invoice comps - {c_invoice}')
    return arca_invoice

# @router.post("",status_code=status.HTTP_201_CREATED,response_model=schemas.Invoice)

# async def create_inv_line_item(line_item)

@router.put("/{id}",status_code=status.HTTP_202_ACCEPTED)
def update_invoice(id,invoice:dict,db:Session = Depends(get_db),
                   org_id : str = Depends(auth.verify_org)):
    
    print(invoice)
    n_zohoinvoice = models.Zoho_Invoice(**invoice['invoice'])#assimilate the new invoice data

    # extract the old invoice record
    o_zohoinvoice = db.query(models.Zoho_Invoice).filter(models.Zoho_Invoice.invoice_id == id).first()
    
    # validate invoice existence and access rights
    if o_zohoinvoice == None:
        # this scenario captures invoices created prior to implementing
        # e-invoice integration. these invoices will be created afresh.
        db.add(n_zohoinvoice)
        db.commit()
        submit_invoice_arca(n_zohoinvoice)
    elif org_id != o_zohoinvoice.zoho_org_id:
        # attempt at gaining unauthorised access to an invoice 
        raise HTTPException(status.HTTP_401_UNAUTHORIZED,
                            detail='Unauthorised to access this invoice.')
    else:

        for key,value in invoice['invoice'].items():
            
            #the try - except block is required since the the zoho_invoice object
            #won't haveo_zohoinvoice,key all the attributes of the zoho invoice passed in the dictionary
            if hasattr(o_zohoinvoice,key):
                try:
                    setattr(o_zohoinvoice,key,value)
                    #add calls to the ARCA update function here
                except:
                    pass
        db.commit()
        update_invoice_arca(o_zohoinvoice)
    #add code to include the updated data to the queue
    #for sending to ARCA

    return 'Updated Completed'

@router.delete("/{id}",status_code=status.HTTP_204_NO_CONTENT)
def delete_invoice(id:str,db:Session = Depends(get_db),
                   current_user:int = Depends(oauth2.get_current_user)):
    # invoice_data = invoice.model_dump()
    try:
        result = db.query(models.Invoice).filter(models.Invoice.irn == id).first()
    except:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail='Unable to query database.')

    if result == None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f'Record {id} not found')
    elif result.creator != current_user.id:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail='Not authorised to delete this record')
    
    try:
        db.query(models.Invoice).filter(models.Invoice.irn == id).delete()
        db.commit()
    except Exception as error:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail='Unable to delete record {id}.')
    
    return f"invoice number {id} deleted successfully"



def submit_invoice_arca(invoice:models.Zoho_Invoice):

    # code for submission of invoice to arca

    response = {}

    return response

def update_invoice_arca(invoice:models.Zoho_Invoice):

    # code for updating invoice status

    # match o_zohoinvoice.status:
    #     case 'paid':
    #         o_zohoinvoice.status = 'PAID'
    #     case 'void':
    #         o_zohoinvoice.status = 'REJECTED'
    #     case 'rejected':
    #         o_zohoinvoice.status = 'REJECTED'
    #     case _:
    #         o_zohoinvoice.status = 'PENDING'
    response = {}

    return response
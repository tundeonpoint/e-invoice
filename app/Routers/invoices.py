# import fastapi,sqlalchemy
from fastapi import Depends,HTTPException,status,Response,APIRouter,Header,Request
# from app import models,utils
from app.database import get_db
from sqlalchemy.orm import Session,declarative_base
from app import models,utils,schemas
from passlib.hash import pbkdf2_sha256
from fastapi.security.oauth2 import OAuth2PasswordRequestForm
from . import oauth2,auth
from typing import List
from sqlalchemy import Date,Time,cast
import json
import re
from datetime import datetime
import json

router = APIRouter(tags=['Invoices'],
                   prefix="/invoices")

@router.get("",status_code=status.HTTP_200_OK,response_model=List[schemas.ZohoInvoice])
def get_invoices(db:Session = Depends(get_db),
                 current_user:str = Depends(oauth2.get_current_user_multi_auth)):
    results = db.query(models.Zoho_Invoice).all()
    # print(f'current user: {current_user.email}')
    return results

@router.get("/{inv_id}/orgs/{org_id}",status_code=status.HTTP_200_OK)
def get_org_invoice(inv_id = None,org_id = None,db:Session=Depends(get_db),
                    current_user:str = Depends(oauth2.get_current_user_multi_auth)):

    result = db.query(models.Zoho_Invoice).filter(models.Zoho_Invoice.zoho_org_id == org_id).filter(models.Zoho_Invoice.invoice_number == inv_id).first()

    if result == None:
        return "No invoices found"
    else:
        return result#create_arca_invoice(result,db)


def create_arca_invoice(zoho_invoice:models.Zoho_Invoice,db:Session) -> dict:

    # n_invoice = models.Invoice()
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
        "invoiceIssueDate": str(zoho_invoice.date.date()),
        "invoiceDueDate": str(zoho_invoice.due_date),
        "invoiceIssueTime": str(zoho_invoice.date.time()),
        "invoiceTypeCode": "550",
        "invoiceNote":zoho_invoice.notes,
        "invoicePaymentStatus": payment_status,
        "invoiceTaxPointDate": str(datetime.now().date()),
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
    # n_invoice.legal_monetary_total = {
    #     "line_extension_amount": zoho_invoice.sub_total,
    #     "tax_exclusive_amount": zoho_invoice.sub_total,
    #     "tax_inclusive_amount": zoho_invoice.total,
    #     "payable_amount": zoho_invoice.total

    # }
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

def save_zoho_invoice(invoice:dict,db,org_id,send_treatment:int):
    
    org_info = db.query(models.Organisation).filter(models.Organisation.zoho_org_id == org_id).first()
    
    if org_info == None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail='Invalid Org Id.')
    
    n_zohoinvoice = models.Zoho_Invoice(**invoice['invoice'])#['invoice'])
    # print(f'*******due date:{n_zohoinvoice.du}')
    n_zohoinvoice.zoho_org_id = org_id
    n_zohoinvoice.business_id = org_info.business_id
    n_zohoinvoice.line_items = invoice["invoice"]["line_items"]
    n_zohoinvoice.send_treatment = send_treatment#create a new invoice
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


@router.post("",status_code=status.HTTP_201_CREATED)#,response_model=schemas.Invoice)
async def create_zoho_invoice(invoice:dict,org_id : str = Depends(oauth2.get_current_user_multi_auth),
                              db:Session = Depends(get_db)):
    
    # check that the org_id is valid
    result = db.query(models.Organisation.zoho_org_id == org_id)
    if result == None:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED,detail='Invalid credentials.')
    arca_invoice = save_zoho_invoice(invoice,db,org_id,send_treatment=1)

    return arca_invoice

@router.put("/{id}",status_code=status.HTTP_202_ACCEPTED)
async def update_invoice(id,invoice:dict,db:Session = Depends(get_db),
                   org_id : str = Depends(oauth2.get_current_user_multi_auth)):

    # check that the org_id is valid
    result = db.query(models.Organisation.zoho_org_id == org_id)
    if result == None:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED,detail='Invalid credentials.')

    result = db.query(models.Zoho_Invoice).filter(models.Zoho_Invoice.zoho_org_id==org_id).filter(models.Zoho_Invoice.invoice_id==id).first()
    
    # if the invoice doesn't exist, it will be created afresh.
    arca_invoice = save_zoho_invoice(invoice,db,org_id,send_treatment=2)

    return arca_invoice

# the following end point needs to be reviewed before exposure
# @router.delete("/{id}",status_code=status.HTTP_204_NO_CONTENT)
def delete_invoice(id:str,db:Session = Depends(get_db),
                   current_user:int = Depends(oauth2.get_current_user_multi_auth)):
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

@router.get("/get_sent_invoices",status_code=status.HTTP_200_OK)
def get_sent_invoices(db:Session = Depends(get_db),
                   current_user:str = Depends(oauth2.get_current_user_multi_auth)):
    # print('*******started function call*********')
    
    # retrieve all the invoices that have been sent
    # but are yet to be retrieved. this ensures we minimise the
    # amount of data being retrieved on every call.
    results = db.query(models.Invoice_Map).filter(models.Invoice_Map.retrieve_status == False).all()

    json_result = [r.to_dict() for r in results]
    # print(f'******results - {json_result}')
    try:
        for result in results:
            result.retrieve_status = True
        
        db.commit()
    
    except:

        return {"status":"failed"}
    
    return {"status":"success","data":json_result}

@router.get("/_debug")
def debug():
    return {"ok": True}
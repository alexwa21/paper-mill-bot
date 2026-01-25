# api.py
from fastapi import FastAPI, Request, Form
from models import create_db_and_tables
from logic import process_order
from twilio.twiml.messaging_response import MessagingResponse
import uvicorn

app = FastAPI()

@app.on_event("startup")
def on_startup():
    create_db_and_tables()

@app.get("/")
def home():
    return {"status": "Active", "system": "Paper Mill Bot"}

@app.post("/whatsapp")
async def reply_whatsapp(Body: str = Form(), From: str = Form()):
    # 1. Clean the phone number (remove whatsapp: prefix)
    customer_phone = From.replace("whatsapp:", "")
    
    # 2. Parse the message (Expected: Grade GSM Size Qty)
    try:
        parts = Body.split()
        if len(parts) < 4:
            response_text = "❌ Format Error. Send: Grade GSM Size Qty\nExample: Kraft 120 50 500"
        else:
            grade = parts[0]
            gsm = int(parts[1])
            size = int(parts[2])
            qty = int(parts[3])
            
            # 3. Validate and Save to Supabase
            response_text = process_order(customer_phone, grade, gsm, size, qty)
            
    except Exception as e:
        response_text = f"❌ System Error: {str(e)}"

    # 4. Send Reply back to WhatsApp
    resp = MessagingResponse()
    resp.message(response_text)
    return str(resp)
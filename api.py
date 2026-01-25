from fastapi import FastAPI, Form
from models import create_db_and_tables, engine, Order, Product
from sqlmodel import Session, select
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
    customer_phone = From.replace("whatsapp:", "")
    parts = Body.split()
    
    if len(parts) < 4:
        msg = "❌ Format: Grade GSM Size Qty\nExample: Kraft 120 50 500"
    else:
        grade, gsm, size, qty = parts[0], int(parts[1]), int(parts[2]), int(parts[3])
        
        with Session(engine) as session:
            # Logic: Check Rules
            rule = session.exec(select(Product).where(Product.grade == grade).where(Product.gsm == gsm)).first()
            if not rule:
                msg = f"❌ Error: We don't make {grade} {gsm} GSM."
            elif not (rule.min_size <= size <= rule.max_size):
                msg = f"❌ Error: Size must be {rule.min_size}-{rule.max_size}."
            else:
                # Save Order
                order = Order(customer_phone=customer_phone, paper_grade=grade, gsm=gsm, reel_size=size, quantity_kg=qty, status="Approved")
                session.add(order)
                session.commit()
                msg = f"✅ SUCCESS: Order #{order.id} Confirmed!"

    resp = MessagingResponse()
    resp.message(msg)
    return str(resp)
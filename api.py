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
    
    # 1. Clean the incoming message (lowercase, remove spaces)
    msg = Body.lower().strip()
    
    # 2. GREETING LOGIC: Check if user said Hi/Hello
    if msg in ["hi", "hello", "hey", "start", "menu"]:
        response_text = (
            "👋 *Welcome to Paper Mill Bot!*\n\n"
            "To place a new order, please send details in this format:\n"
            "📝 *Grade GSM Size Qty*\n\n"
            "Example:\n"
            "Kraft 120 50 500"
        )
    
    # 3. ORDER LOGIC: If not greeting, try to process as order
    else:
        parts = Body.split()
        if len(parts) < 4:
            response_text = "❌ *Format Error.*\n\nPlease send: Grade GSM Size Qty\nExample: Kraft 120 50 500\n\nOr say 'Hi' for help."
        else:
            grade = parts[0]
            try:
                gsm = int(parts[1])
                size = int(parts[2])
                qty = int(parts[3])
                
                with Session(engine) as session:
                    # Validate against Database Rules
                    rule = session.exec(select(Product).where(Product.grade == grade).where(Product.gsm == gsm)).first()
                    
                    if not rule:
                        response_text = f"❌ Error: We do not manufacture {grade} in {gsm} GSM."
                    elif not (rule.min_size <= size <= rule.max_size):
                        response_text = f"❌ Error: For {grade} {gsm}, size must be between {rule.min_size} and {rule.max_size}."
                    else:
                        # Save the Order
                        order = Order(customer_phone=customer_phone, paper_grade=grade, gsm=gsm, reel_size=size, quantity_kg=qty, status="Approved")
                        session.add(order)
                        session.commit()
                        response_text = f"✅ *SUCCESS: Order Confirmed!*\n\n🆔 Order ID: #{order.id}\n📄 {grade} {gsm} GSM\n📏 {size} inches\n⚖️ {qty} kg"
            except ValueError:
                response_text = "❌ Error: GSM, Size, and Qty must be numbers."

    # 4. Send Reply back to WhatsApp
    resp = MessagingResponse()
    resp.message(response_text)
    return str(resp)
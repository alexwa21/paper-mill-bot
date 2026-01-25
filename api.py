from fastapi import FastAPI, Form, Response
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
    
    # 1. Clean the incoming message (Fixes Case Sensitivity)
    # This turns "Kraft" -> "kraft" to match your database
    msg = Body.lower().strip()
    
    # 2. GREETING LOGIC
    if msg in ["hi", "hello", "hey", "start", "menu", "join"]:
        response_text = (
            "👋 *Welcome to Paper Mill Bot!*\n\n"
            "To place a new order, please send details in this format:\n"
            "📝 *Grade GSM Size Qty*\n\n"
            "Example:\n"
            "Kraft 120 50 500"
        )
    
    # 3. ORDER LOGIC
    else:
        parts = msg.split()
        if len(parts) < 4:
            response_text = "❌ *Format Error.*\n\nPlease send: Grade GSM Size Qty\nExample: Kraft 120 50 500\n\nOr say 'Hi' for help."
        else:
            grade = parts[0] # This is now lowercase (e.g., 'kraft')
            try:
                gsm = int(parts[1])
                size = int(parts[2])
                qty = int(parts[3])
                
                with Session(engine) as session:
                    # Check database for the product
                    rule = session.exec(select(Product).where(Product.grade == grade).where(Product.gsm == gsm)).first()
                    
                    if not rule:
                        response_text = f"❌ Error: We do not manufacture '{parts[0]}' in {gsm} GSM."
                    elif not (rule.min_size <= size <= rule.max_size):
                        response_text = f"❌ Error: For {parts[0]} {gsm}, size must be between {rule.min_size} and {rule.max_size}."
                    else:
                        # SAFETY NET: Try to save, catch errors if it fails
                        try:
                            order = Order(customer_phone=customer_phone, paper_grade=grade, gsm=gsm, reel_size=size, quantity_kg=qty, status="Approved")
                            session.add(order)
                            session.commit()
                            # Success Message
                            response_text = f"✅ *SUCCESS: Order Confirmed!*\n\n🆔 Order ID: #{order.id}\n📄 {parts[0].title()} {gsm} GSM\n📏 {size} inches\n⚖️ {qty} kg"
                        except Exception as e:
                            print(f"DATABASE ERROR: {e}") # Print to server logs
                            response_text = "⚠️ System Error: The database refused to save the order. Please try again."
                            
            except ValueError:
                response_text = "❌ Error: GSM, Size, and Qty must be numbers."

    # 4. RETURN XML RESPONSE
    resp = MessagingResponse()
    resp.message(response_text)
    return Response(content=str(resp), media_type="application/xml")
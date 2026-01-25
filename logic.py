from sqlmodel import Session, select
from models import engine, Product, Order

def process_order(phone, grade, gsm, size, qty):
    with Session(engine) as session:
        # Validate GSM
        statement = select(Product).where(Product.grade == grade).where(Product.gsm == gsm)
        product_rule = session.exec(statement).first()
        
        if not product_rule:
            return f"❌ ERROR: We do not manufacture {grade} paper in {gsm} GSM. Available GSMs: 100, 120, 200."

        # Validate Size
        if not (product_rule.min_size <= size <= product_rule.max_size):
            return f"❌ ERROR: For {gsm} GSM, valid Reel Size is between {product_rule.min_size} and {product_rule.max_size} inches."

        # Save Valid Order
        new_order = Order(
            customer_phone=phone,
            paper_grade=grade,
            gsm=gsm,
            reel_size=size,
            quantity_kg=qty,
            status="Approved"
        )
        session.add(new_order)
        session.commit()
        return f"✅ SUCCESS: Order #{new_order.id} Confirmed! {qty}kg of {grade} {gsm}GSM."
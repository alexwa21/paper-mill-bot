import streamlit as st
import pandas as pd
from sqlmodel import Session, select
from models import engine, Order, create_db_and_tables, seed_rules
from logic import process_order

# Init DB
create_db_and_tables()
seed_rules()

st.set_page_config(page_title="Paper Mill Dispatch", layout="wide")

st.title("🏭 Mill Owner Dashboard")
st.markdown("### Zero-Error Dispatch System")

# Sidebar Simulator
with st.sidebar:
    st.header("📱 WhatsApp Simulator")
    st.info("Test the validation logic here:")
    phone = st.text_input("Phone Number", "9876543210")
    grade = st.selectbox("Paper Grade", ["Kraft", "Duplex", "InvalidGrade"])
    gsm = st.number_input("GSM", value=120)
    size = st.number_input("Reel Size (Inch)", value=50)
    qty = st.number_input("Quantity (kg)", value=500)
    
    if st.button("Send Order"):
        response = process_order(phone, grade, gsm, size, qty)
        if "ERROR" in response:
            st.error(response)
        else:
            st.success(response)

# Main Dashboard
def load_data():
    with Session(engine) as session:
        orders = session.exec(select(Order)).all()
        return [o.dict() for o in orders]

data = load_data()

if data:
    df = pd.DataFrame(data)
    col1, col2, col3 = st.columns(3)
    col1.metric("📦 Total Orders", len(df))
    col2.metric("⚖️ Total Tonnage (kg)", f"{df['quantity_kg'].sum():,}")
    col3.metric("✅ Approved Orders", len(df[df['status']=="Approved"]))
    
    st.subheader("Live Order Feed")
    st.dataframe(df.sort_values("timestamp", ascending=False), use_container_width=True)
else:
    st.info("No orders yet. Use the sidebar to create one.")

if st.button("Refresh Data"):
    st.rerun()
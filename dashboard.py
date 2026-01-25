import streamlit as st
import pandas as pd
from sqlmodel import Session, select
from models import engine, Order, create_db_and_tables

st.set_page_config(page_title="Mill Dashboard", layout="wide")
create_db_and_tables()

st.title("🏭 Mill Owner Dashboard")

# Refresh Button
if st.button("🔄 Refresh Data"):
    st.rerun()

# Load Data
with Session(engine) as session:
    orders = session.exec(select(Order).order_by(Order.timestamp.desc())).all()
    data = [o.dict() for o in orders]

if data:
    df = pd.DataFrame(data)
    st.dataframe(df, use_container_width=True)
else:
    st.info("No orders yet. Waiting for WhatsApp...")
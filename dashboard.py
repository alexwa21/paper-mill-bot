import streamlit as st
import pandas as pd
from sqlmodel import Session, select
from models import Order, Product, create_db_and_tables, engine 

# 1. Setup Page
st.set_page_config(page_title="Paper Mill Dashboard", layout="wide")
st.title("🏭 Mill Owner Dashboard")

# 2. Initialize DB (Using the imported engine from models.py)
try:
    create_db_and_tables()
except Exception as e:
    st.error(f"Database Connection Error: {e}")
    st.stop()

# --- SECTION 1: STOCK THE SHELVES ---
with st.expander("➕ Add New Product / Stock", expanded=True):
    st.write("Manage your Inventory")
    with st.form("add_product_form"):
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            grade = st.text_input("Item Name", placeholder="e.g. Groom Kit")
        with col2:
            gsm = st.number_input("Price (₹)", min_value=1, value=500)
        with col3:
            min_s = st.number_input("Min Qty", value=1)
        with col4:
            max_s = st.number_input("Current Stock", value=50)
        
        submitted = st.form_submit_button("✅ Update Inventory")
        
        if submitted:
            if grade:
                with Session(engine) as session:
                    # Clean the input
                    clean_grade = grade.strip()
                    # Add to DB
                    new_product = Product(grade=clean_grade, gsm=gsm, min_size=min_s, max_size=max_s)
                    session.add(new_product)
                    session.commit()
                st.success(f"Added: {grade} (Price: ₹{gsm}, Stock: {max_s})")
            else:
                st.error("Please enter an Item Name.")

# --- SECTION 2: LIVE DATA ---
st.divider()
col_left, col_right = st.columns([2, 1])

with col_left:
    st.subheader("📦 Live Orders")
    if st.button("🔄 Refresh"):
        st.rerun()

    with Session(engine) as session:
        orders = session.exec(select(Order).order_by(Order.id.desc())).all()
        if orders:
            df = pd.DataFrame([o.dict() for o in orders])
            st.dataframe(df, use_container_width=True)
        else:
            st.info("No orders yet.")

with col_right:
    st.subheader("📋 Inventory")
    with Session(engine) as session:
        products = session.exec(select(Product)).all()
        if products:
            df_p = pd.DataFrame([p.dict() for p in products])
            st.dataframe(df_p[["grade", "gsm", "max_size"]].rename(columns={"gsm": "Price", "max_size": "Stock"}), hide_index=True)
        else:
            st.warning("Inventory empty.")
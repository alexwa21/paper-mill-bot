import streamlit as st
import pandas as pd
from sqlmodel import Session, select, create_engine
from models import Order, Product, create_db_and_tables

# 1. Setup Page
st.set_page_config(page_title="Paper Mill Dashboard", layout="wide")
st.title("🏭 Mill Owner Dashboard")

# 2. Connect to Database
# This automatically grabs the "Golden Key" you saved in Streamlit Secrets
try:
    if "DATABASE_URL" in st.secrets:
        connection_string = st.secrets["DATABASE_URL"]
    else:
        # Fallback for some toml formats
        connection_string = st.secrets["general"]["DATABASE_URL"]
except:
    # Safe fallback if running on laptop without secrets
    connection_string = "sqlite:///database.db"

engine = create_engine(connection_string)

# 3. Initialize DB (Create tables if missing)
create_db_and_tables()

# --- SECTION 1: STOCK THE SHELVES (Main Area) ---
# We moved this from the sidebar to the main page so it is visible
with st.expander("➕ Add New Product Rule (Click to Open)", expanded=True):
    st.write("Tell the bot what you manufacture.")
    with st.form("add_product_form"):
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            grade = st.text_input("Grade Name", placeholder="e.g. Kraft")
        with col2:
            gsm = st.number_input("GSM", min_value=50, max_value=500, value=120)
        with col3:
            min_s = st.number_input("Min Size (inch)", value=40)
        with col4:
            max_s = st.number_input("Max Size (inch)", value=100)
        
        submitted = st.form_submit_button("✅ Add Product to Database")
        
        if submitted:
            if grade:
                with Session(engine) as session:
                    # Clean input to ensure matching works
                    clean_grade = grade.strip().lower()
                    new_product = Product(grade=clean_grade, gsm=gsm, min_size=min_s, max_size=max_s)
                    session.add(new_product)
                    session.commit()
                st.success(f"Added Rule: {grade} {gsm} GSM ({min_s}-{max_s} inch)")
            else:
                st.error("Please enter a Grade Name.")

# --- SECTION 2: SHOW LIVE DATA ---
st.divider() # Visual separator
col_left, col_right = st.columns([2, 1])

with col_left:
    st.subheader("📦 Live Incoming Orders")
    if st.button("🔄 Refresh Orders"):
        st.rerun()

    with Session(engine) as session:
        orders = session.exec(select(Order).order_by(Order.id.desc())).all()
        if orders:
            # Show table nicely
            df = pd.DataFrame([o.dict() for o in orders])
            # Reorder columns for readability
            display_cols = ["id", "status", "paper_grade", "gsm", "reel_size", "quantity_kg", "customer_phone"]
            st.dataframe(df[display_cols], use_container_width=True)
        else:
            st.info("No orders yet. Waiting for WhatsApp...")

with col_right:
    st.subheader("📋 Product Rules")
    with Session(engine) as session:
        products = session.exec(select(Product)).all()
        if products:
            df_p = pd.DataFrame([p.dict() for p in products])
            st.dataframe(df_p[["grade", "gsm", "min_size", "max_size"]], hide_index=True)
        else:
            st.warning("No products defined yet. Add one above!")
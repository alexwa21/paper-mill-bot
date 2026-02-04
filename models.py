from sqlmodel import SQLModel, Field, create_engine
from typing import Optional
import os

# 1. DATABASE MODELS
class Product(SQLModel, table=True):
    __tablename__ = "products"
    __table_args__ = {"extend_existing": True} 
    id: Optional[int] = Field(default=None, primary_key=True)
    grade: str
    gsm: int
    min_size: int
    max_size: int

class Order(SQLModel, table=True):
    __tablename__ = "orders"
    __table_args__ = {"extend_existing": True}
    id: Optional[int] = Field(default=None, primary_key=True)
    customer_phone: str
    paper_grade: str
    gsm: int
    reel_size: int
    quantity_kg: int
    status: str = "Pending"

# 2. SMART CONNECTION ENGINE
def get_db_url():
    # A. Check Render/Cloud Environment Variable
    url = os.environ.get("DATABASE_URL")
    
    # B. If not found, check Streamlit Secrets
    if not url:
        try:
            import streamlit as st
            if "DATABASE_URL" in st.secrets:
                url = st.secrets["DATABASE_URL"]
            elif "general" in st.secrets and "DATABASE_URL" in st.secrets["general"]:
                url = st.secrets["general"]["DATABASE_URL"]
        except:
            pass # Streamlit not installed or no secrets found

    # C. Fallback to Local Database (if nothing else works)
    if not url:
        return "sqlite:///database.db"

    # D. FIX: Convert 'postgres://' to 'postgresql://' for SQLAlchemy
    if url.startswith("postgres://"):
        url = url.replace("postgres://", "postgresql://", 1)
        
    return url

# Create the Global Engine
db_url = get_db_url()
engine = create_engine(db_url)

def create_db_and_tables():
    # Uses the smart engine defined above
    SQLModel.metadata.create_all(engine)
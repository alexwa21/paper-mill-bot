from sqlmodel import SQLModel, Field, create_engine
from typing import Optional
import os

# 1. DATABASE SETUP
# We use a special setting here to prevent the "Table already exists" crash
class Product(SQLModel, table=True):
    __table_args__ = {"extend_existing": True}  # <--- THIS IS THE FIX
    id: Optional[int] = Field(default=None, primary_key=True)
    grade: str
    gsm: int
    min_size: int
    max_size: int

class Order(SQLModel, table=True):
    __table_args__ = {"extend_existing": True}  # <--- THIS IS THE FIX
    id: Optional[int] = Field(default=None, primary_key=True)
    customer_phone: str
    paper_grade: str
    gsm: int
    reel_size: int
    quantity_kg: int
    status: str = "Pending"

# 2. CONNECTION ENGINE
# We check if we are on the cloud (Render/Streamlit) or local
DATABASE_URL = os.environ.get("DATABASE_URL")
if not DATABASE_URL:
    # Fallback for local testing
    DATABASE_URL = "sqlite:///database.db"

# Create the engine
engine = create_engine(DATABASE_URL)

def create_db_and_tables():
    SQLModel.metadata.create_all(engine)
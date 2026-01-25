from sqlmodel import SQLModel, Field, create_engine
from typing import Optional
import os

# 1. DATABASE MODELS
class Product(SQLModel, table=True):
    __tablename__ = "products"  # <--- Plural name (Safe)
    __table_args__ = {"extend_existing": True} 
    id: Optional[int] = Field(default=None, primary_key=True)
    grade: str
    gsm: int
    min_size: int
    max_size: int

class Order(SQLModel, table=True):
    __tablename__ = "orders"   # <--- Plural name (Safe from 'ORDER' keyword)
    __table_args__ = {"extend_existing": True}
    id: Optional[int] = Field(default=None, primary_key=True)
    customer_phone: str
    paper_grade: str
    gsm: int
    reel_size: int
    quantity_kg: int
    status: str = "Pending"

# 2. CONNECTION ENGINE
def get_engine(db_url=None):
    if not db_url:
        db_url = os.environ.get("DATABASE_URL")
    if not db_url:
        db_url = "sqlite:///database.db"
    return create_engine(db_url)

engine = get_engine()

def create_db_and_tables():
    SQLModel.metadata.create_all(engine)
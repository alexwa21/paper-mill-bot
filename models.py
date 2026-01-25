# models.py (Updated for Production)
import os
from typing import Optional
from sqlmodel import Field, SQLModel, create_engine, Session
from datetime import datetime

# (Keep your Class definitions for Product and Order exactly the same)
class Product(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    grade: str
    gsm: int
    min_size: int
    max_size: int

class Order(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    customer_phone: str
    paper_grade: str
    gsm: int
    reel_size: int
    quantity_kg: int
    status: str = "Pending"
    timestamp: datetime = Field(default_factory=datetime.now)

# --- THE CHANGE: Real DB Connection ---
# If we are on the cloud, get the secure password. If local, use sqlite for testing.
DATABASE_URL = os.environ.get("DATABASE_URL", "postgresql://postgres:gJ3+YLv&H6VAhz/@db.crgbhzecdpodnaxjpsom.supabase.co:5432/postgres")

# Fix for some postgres drivers requiring 'postgresql://' instead of 'postgres://'
if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

engine = create_engine(DATABASE_URL)

def create_db_and_tables():
    SQLModel.metadata.create_all(engine)
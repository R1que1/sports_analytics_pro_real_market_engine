
from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, Text
from sqlalchemy.orm import declarative_base, sessionmaker
from datetime import datetime
import os

DATABASE_URL = os.environ.get("DATABASE_URL", "sqlite:///sports_pro_cloud.db")

engine = create_engine(DATABASE_URL, pool_pre_ping=True)
SessionLocal = sessionmaker(bind=engine)
Base = declarative_base()

class CloudUser(Base):
    __tablename__ = "cloud_users"
    id = Column(Integer, primary_key=True)
    name = Column(String(120))
    email = Column(String(180), unique=True, index=True)
    password_hash = Column(String(255))
    plan = Column(String(50), default="VIP")
    role = Column(String(50), default="user")
    created_at = Column(DateTime, default=datetime.utcnow)

class CloudPrediction(Base):
    __tablename__ = "cloud_predictions"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer)
    home = Column(String(120))
    away = Column(String(120))
    favorite = Column(String(120))
    confidence = Column(Integer)
    markets = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)

class CloudEntry(Base):
    __tablename__ = "cloud_entries"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer)
    fixture = Column(String(255))
    market = Column(String(255))
    odd = Column(Float)
    stake = Column(Float)
    result = Column(String(50), default="open")
    profit = Column(Float, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)

def init_cloud_db():
    Base.metadata.create_all(bind=engine)

if __name__ == "__main__":
    init_cloud_db()
    print("Cloud database initialized:", DATABASE_URL)

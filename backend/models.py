from sqlalchemy import Column, Integer, String, ARRAY, Float, ForeignKey
from database import Base

class Admin(Base):
    __tablename__ = "admins"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    password = Column(String, nullable=False)

class Courier(Base):
    __tablename__ = "couriers_auth"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    password = Column(String, nullable=False)
    courier_type = Column(String, nullable=False)
    regions = Column(ARRAY(Integer), nullable=False)
    working_hours = Column(ARRAY(String), nullable=False)
    rating = Column(Float, default=0.0)

class Order(Base):
    __tablename__ = "orders"
    order_id = Column(Integer, primary_key=True, index=True)
    weight = Column(Float, nullable=False)
    region = Column(Integer, nullable=False)
    delivery_hours = Column(ARRAY(String), nullable=False)
    courier_id = Column(Integer, ForeignKey("couriers_auth.id"), nullable=True)
    assign_time = Column(String, nullable=True)
    status = Column(String, default="new")
    completed_time = Column(String, nullable=True)
    cancelled_time = Column(String, nullable=True)
    price = Column(Float, nullable=False)
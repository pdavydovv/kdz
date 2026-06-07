from sqlalchemy import Column, Integer, String, ARRAY, Float
from database import Base

class Courier(Base):
    __tablename__ = "couriers"

    courier_id = Column(Integer, primary_key=True, index=True)
    courier_type = Column(String, nullable=False)
    regions = Column(ARRAY(Integer), nullable=False)
    working_hours = Column(ARRAY(String), nullable=False)

class Order(Base):
    __tablename__ = "orders"

    order_id = Column(Integer, primary_key=True, index=True)
    weight = Column(Float, nullable=False)
    regions = Column(Integer, nullable=False)
    delivery_hours = Column(ARRAY(String), nullable=False)
    cost = Column(Integer, nullable=False)
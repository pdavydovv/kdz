from sqlalchemy import Column, Integer, String, ARRAY, Float, ForeignKey
from database import Base


class Courier(Base):
    __tablename__ = "couriers"

    courier_id = Column(Integer, primary_key=True, index=True)
    courier_type = Column(String, nullable=False)  # 'foot', 'bike', 'car'
    regions = Column(ARRAY(Integer), nullable=False)
    working_hours = Column(ARRAY(String), nullable=False)


class Order(Base):
    __tablename__ = "orders"

    order_id = Column(Integer, primary_key=True, index=True)
    weight = Column(Float, nullable=False)
    region = Column(Integer, nullable=False)  # Строго одно число по ТЗ
    delivery_hours = Column(ARRAY(String), nullable=False)

    # Логика трекинга доставки
    courier_id = Column(Integer, ForeignKey("couriers.courier_id"), nullable=True)
    assign_time = Column(String, nullable=True)
    complete_time = Column(String, nullable=True)
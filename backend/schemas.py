from pydantic import BaseModel, Field, field_validator
from typing import List
from enum import Enum
import re

class CourierType(str, Enum):
    FOOT = "foot"
    BIKE = "bike"
    CAR = "car"

class CourierItem(BaseModel):
    courier_id: int = Field(..., gt=0)
    courier_type: CourierType
    regions: List[int]
    working_hours: List[str]

    @field_validator('working_hours')
    @classmethod
    def validate_hours(cls, hours: List[str]) -> List[str]:
        time_regex = r"^\d{2}:\d{2}-\d{2}:\d{2}$"
        for hour in hours:
            if not re.match(time_regex, hour):
                raise ValueError("Format must be HH:MM-HH:MM")
        return hours

class OrderItem(BaseModel):
    order_id: int = Field(..., gt=0)
    weight: float = Field(..., gt=0)
    regions: int = Field(..., gt=0)
    delivery_hours: List[str]
    cost: int = Field(..., gt=0)

    @field_validator('delivery_hours')
    @classmethod
    def validate_delivery_hours(cls, hours: List[str]) -> List[str]:
        time_regex = r"^\d{2}:\d{2}-\d{2}:\d{2}$"
        for hour in hours:
            if not re.match(time_regex, hour):
                raise ValueError("Format must be HH:MM-HH:MM")
        return hours

class OrdersPostRequest(BaseModel):
    orders: List[OrderItem]

class CouriersPostRequest(BaseModel):
    couriers: List[CourierItem]

class CourierResponse(BaseModel):
    courier_id: int
    courier_type: CourierType
    regions: List[int]
    working_hours: List[str]

    class Config:
        from_attributes = True

class OrderResponse(BaseModel):
    order_id: int
    weight: float
    regions: int
    delivery_hours: List[str]
    cost: int

    class Config:
        from_attributes = True
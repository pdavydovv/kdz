from pydantic import BaseModel, Field, field_validator, ConfigDict
from typing import List, Optional
from enum import Enum
import re

class CourierType(str, Enum):
    FOOT = "foot"
    BIKE = "bike"
    CAR = "car"

class CourierItem(BaseModel):
    user_id: int = Field(..., gt=0)
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
    region: int = Field(..., gt=0)
    delivery_hours: List[str]

    @field_validator('delivery_hours')
    @classmethod
    def validate_delivery_hours(cls, hours: List[str]) -> List[str]:
        time_regex = r"^\d{2}:\d{2}-\d{2}:\d{2}$"
        for hour in hours:
            if not re.match(time_regex, hour):
                raise ValueError("Format must be HH:MM-HH:MM")
        return hours

class CouriersPostRequest(BaseModel):
    data: List[CourierItem]

class OrdersPostRequest(BaseModel):
    data: List[OrderItem]

class CourierIdItem(BaseModel):
    id: int

class CouriersIdsResponse(BaseModel):
    couriers: List[CourierIdItem]

class OrderIdItem(BaseModel):
    id: int

class OrdersIdsResponse(BaseModel):
    orders: List[OrderIdItem]

class CourierGetResponse(BaseModel):
    user_id: int
    courier_type: CourierType
    regions: List[int]
    working_hours: List[str]
    rating: Optional[float] = None
    earnings: Optional[int] = 0

    model_config = ConfigDict(from_attributes=True)

class CourierUpdateRequest(BaseModel):
    courier_type: Optional[CourierType] = None
    regions: Optional[List[int]] = None
    working_hours: Optional[List[str]] = None

class OrdersAssignPostRequest(BaseModel):
    user_id: int

class OrdersAssignResponse(BaseModel):
    orders: List[OrderIdItem]
    assign_time: str

class OrdersCompletePostRequest(BaseModel):
    user_id: int
    order_id: int
    complete_time: str

class OrdersCompletePostResponse(BaseModel):
    order_id: int



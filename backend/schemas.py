from pydantic import BaseModel, Field, field_validator, ConfigDict
from typing import List, Optional
from enum import Enum
import re

class CourierType(str, Enum):
    FOOT = "foot"
    BIKE = "bike"
    CAR = "car"

class OrderStatus(str, Enum):
    NEW = "new"
    ASSIGNED = "assigned"
    COMPLETED = "completed"
    CANCELLED = "cancelled"

class CourierItem(BaseModel):
    id: int = Field(..., gt=0)
    username: str
    password: str
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
    price: float = Field(..., gt=0)
    delivery_hours: List[str]

    @field_validator('delivery_hours')
    @classmethod
    def validate_delivery_hours(cls, hours: List[str]) -> List[str]:
        time_regex = r"^\d{2}:\d{2}-\d{2}:\d{2}$"
        for hour in hours:
            if not re.match(time_regex, hour):
                raise ValueError("Format must be HH:MM-HH:MM")
        return hours

class LoginRequest(BaseModel):
    username: str
    password: str

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
    id: int
    username: str
    courier_type: CourierType
    regions: List[int]
    working_hours: List[str]
    rating: float = 0.0
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

class OrderCompleteRequest(BaseModel):
    courier_id: int
    order_id: int
    complete_time: str

class OrderCancelRequest(BaseModel):
    courier_id: int
    order_id: int

class OrderResponse(BaseModel):
    order_id: int
    weight: float
    region: int
    delivery_hours: List[str]
    courier_id: Optional[int] = None
    assign_time: Optional[str] = None
    status: OrderStatus
    completed_time: Optional[str] = None
    cancelled_time: Optional[str] = None
    price: float

    model_config = ConfigDict(from_attributes=True)
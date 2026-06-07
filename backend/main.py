from fastapi import FastAPI, Depends, status, HTTPException
from sqlalchemy.orm import Session
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime

from schemas import (
    CouriersPostRequest, OrdersPostRequest, CouriersIdsResponse, OrdersIdsResponse,
    CourierGetResponse, CourierUpdateRequest, OrdersAssignPostRequest, OrdersAssignResponse,
    OrdersCompletePostRequest, OrdersCompletePostResponse
)
import models
from database import engine, get_db
from utils import is_overlapping, get_max_weight

models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="Candy Delivery App")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"status": "Strict T-Z Compliant Running"}


@app.post("/couriers", status_code=status.HTTP_201_CREATED, response_model=CouriersIdsResponse)
def import_couriers(payload: CouriersPostRequest, db: Session = Depends(get_db)):
    imported_ids = []
    for courier_data in payload.data:
        db_courier = models.Courier(
            courier_id=courier_data.courier_id,
            courier_type=courier_data.courier_type.value,
            regions=courier_data.regions,
            working_hours=courier_data.working_hours
        )
        db.add(db_courier)
        imported_ids.append({"id": courier_data.courier_id})
    db.commit()
    return {"couriers": imported_ids}


@app.get("/couriers/{courier_id}", response_model=CourierGetResponse)
def get_courier_by_id(courier_id: int, db: Session = Depends(get_db)):
    courier = db.query(models.Courier).filter(models.Courier.courier_id == courier_id).first()
    if not courier:
        raise HTTPException(status_code=404, detail="Courier not found")

    completed_orders = db.query(models.Order).filter(
        models.Order.courier_id == courier_id,
        models.Order.complete_time.isnot(None)
    ).all()

    coefficients = {"foot": 2, "bike": 3, "car": 4}
    coef = coefficients.get(courier.courier_type, 2)
    earnings = sum(150 * coef for _ in completed_orders)

    rating = None
    if completed_orders:
        rating = round(len(completed_orders) / 1.0, 2)

    return {
        "courier_id": courier.courier_id,
        "courier_type": courier.courier_type,
        "regions": courier.regions,
        "working_hours": courier.working_hours,
        "rating": rating,
        "earnings": earnings
    }


@app.patch("/couriers/{courier_id}", response_model=CourierGetResponse)
def update_courier(courier_id: int, payload: CourierUpdateRequest, db: Session = Depends(get_db)):
    courier = db.query(models.Courier).filter(models.Courier.courier_id == courier_id).first()
    if not courier:
        raise HTTPException(status_code=404, detail="Courier not found")

    if payload.courier_type is not None:
        courier.courier_type = payload.courier_type.value
    if payload.regions is not None:
        courier.regions = payload.regions
    if payload.working_hours is not None:
        courier.working_hours = payload.working_hours

    db.commit()
    db.refresh(courier)
    completed_orders = db.query(models.Order).filter(
        models.Order.courier_id == courier_id,
        models.Order.complete_time.isnot(None)
    ).all()
    coefficients = {"foot": 2, "bike": 3, "car": 4}
    coef = coefficients.get(courier.courier_type, 2)
    earnings = sum(150 * coef for _ in completed_orders)
    rating = round(len(completed_orders) / 1.0, 2) if completed_orders else None

    return {
        "courier_id": courier.courier_id,
        "courier_type": courier.courier_type,
        "regions": courier.regions,
        "working_hours": courier.working_hours,
        "rating": rating,
        "earnings": earnings
    }


@app.post("/orders", status_code=status.HTTP_201_CREATED, response_model=OrdersIdsResponse)
def import_orders(payload: OrdersPostRequest, db: Session = Depends(get_db)):
    imported_ids = []
    for order_data in payload.data:
        db_order = models.Order(
            order_id=order_data.order_id,
            weight=order_data.weight,
            region=order_data.region,
            delivery_hours=order_data.delivery_hours
        )
        db.add(db_order)
        imported_ids.append({"id": order_data.order_id})
    db.commit()
    return {"orders": imported_ids}


@app.post("/orders/assign", response_model=OrdersAssignResponse)
def assign_orders_to_courier(payload: OrdersAssignPostRequest, db: Session = Depends(get_db)):
    courier = db.query(models.Courier).filter(models.Courier.courier_id == payload.courier_id).first()
    if not courier:
        raise HTTPException(status_code=400, detail="Courier not found")

    available_orders = db.query(models.Order).filter(
        models.Order.courier_id.is_(None),
        models.Order.region.in_(courier.regions)
    ).all()

    max_weight = get_max_weight(courier.courier_type.lower())
    current_weight = 0.0
    assigned_orders = []

    current_time_str = datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%S.%fZ")

    for order in available_orders:
        if is_overlapping(courier.working_hours, order.delivery_hours):
            if current_weight + order.weight <= max_weight:
                order.courier_id = courier.courier_id
                order.assign_time = current_time_str
                assigned_orders.append({"id": order.order_id})
                current_weight += order.weight

    db.commit()
    return {
        "orders": assigned_orders,
        "assign_time": current_time_str
    }


@app.post("/orders/complete", response_model=OrdersCompletePostResponse)
def complete_order(payload: OrdersCompletePostRequest, db: Session = Depends(get_db)):
    order = db.query(models.Order).filter(
        models.Order.order_id == payload.order_id,
        models.Order.courier_id == payload.courier_id
    ).first()

    if not order:
        raise HTTPException(status_code=400, detail="Order or assignment not found")

    order.complete_time = payload.complete_time
    db.commit()

    return {"order_id": order.order_id}
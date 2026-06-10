from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime
from typing import List, Optional

import models
from database import engine, get_db
from schemas import (
    LoginRequest,
    CourierGetResponse,
    OrderResponse,
    OrderCompleteRequest,
    OrderCancelRequest,
)

models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="Candy Delivery App")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def update_courier_rating(db: Session, courier_id: int):
    courier = db.query(models.Courier).filter(models.Courier.id == courier_id).first()
    if not courier:
        return
    completed_count = db.query(models.Order).filter(
        models.Order.courier_id == courier_id,
        models.Order.status == 'completed'
    ).count()
    cancelled_count = db.query(models.Order).filter(
        models.Order.courier_id == courier_id,
        models.Order.status == 'cancelled'
    ).count()
    total = completed_count + cancelled_count
    if total == 0:
        rating = 0.0
    else:
        rating = 5.0 * (completed_count / total)
    courier.rating = round(rating, 2)
    db.commit()

@app.post("/auth/login")
def login(payload: LoginRequest, role: str, db: Session = Depends(get_db)):
    if role == "admin":
        user = db.query(models.Admin).filter(
            models.Admin.username == payload.username,
            models.Admin.password == payload.password
        ).first()
    else:
        user = db.query(models.Courier).filter(
            models.Courier.username == payload.username,
            models.Courier.password == payload.password
        ).first()
    if not user:
        raise HTTPException(status_code=401, detail="Неверный логин или пароль")
    return {"status": "success", "username": user.username, "id": user.id, "role": role}

@app.post("/couriers")
def register_courier(payload: dict, db: Session = Depends(get_db)):
    data = payload.get('data', payload)
    new_courier = models.Courier(
        username=data['username'],
        password=data['password'],
        courier_type=data['courier_type'],
        regions=data['regions'],
        working_hours=data['working_hours']
    )
    db.add(new_courier)
    db.commit()
    return {"id": new_courier.id}

@app.get("/users/all", response_model=List[CourierGetResponse])
def get_all_couriers(db: Session = Depends(get_db)):
    return db.query(models.Courier).all()

@app.get("/orders/all", response_model=List[OrderResponse])
def get_all_orders(db: Session = Depends(get_db)):
    return db.query(models.Order).all()

@app.post("/orders")
def import_orders(payload: dict, db: Session = Depends(get_db)):
    for o in payload['data']:
        existing = db.query(models.Order).filter(models.Order.order_id == o['order_id']).first()
        if not existing:
            new_order = models.Order(
                order_id=o['order_id'],
                weight=o['weight'],
                region=o['region'],
                delivery_hours=o['delivery_hours'],
                status='new',
                price = o['price']
            )
            db.add(new_order)
    db.commit()
    return {"status": "success"}

@app.post("/orders/assign/single")
def assign_single_order(payload: dict, db: Session = Depends(get_db)):
    courier = db.query(models.Courier).filter(models.Courier.id == payload['courier_id']).first()
    order = db.query(models.Order).filter(models.Order.order_id == payload['order_id']).first()
    if not courier or not order:
        raise HTTPException(status_code=404, detail="Курьер или заказ не найден")
    if order.courier_id is not None or order.status != 'new':
        raise HTTPException(status_code=400, detail="Заказ уже назначен или не в статусе new")
    if order.region in courier.regions:
        order.courier_id = courier.id
        order.status = 'assigned'
        order.assign_time = datetime.now().isoformat()
        db.commit()
        return {"status": "success", "order_id": order.order_id, "courier_id": courier.id}
    else:
        raise HTTPException(status_code=400, detail="Курьер не работает в этом регионе")

@app.post("/orders/complete")
def complete_order(payload: OrderCompleteRequest, db: Session = Depends(get_db)):
    order = db.query(models.Order).filter(
        models.Order.order_id == payload.order_id,
        models.Order.courier_id == payload.courier_id,
        models.Order.status == 'assigned'
    ).first()
    if not order:
        raise HTTPException(
            status_code=404,
            detail="Заказ не найден, не назначен этому курьеру или уже завершён/отменён"
        )
    order.status = 'completed'
    order.completed_time = payload.complete_time
    db.commit()
    update_courier_rating(db, payload.courier_id)
    return {"order_id": order.order_id}

@app.post("/orders/cancel")
def cancel_order(payload: OrderCancelRequest, db: Session = Depends(get_db)):
    order = db.query(models.Order).filter(
        models.Order.order_id == payload.order_id,
        models.Order.courier_id == payload.courier_id,
        models.Order.status == 'assigned'
    ).first()
    if not order:
        raise HTTPException(
            status_code=404,
            detail="Заказ не найден, не назначен этому курьеру или уже завершён/отменён"
        )
    order.status = 'cancelled'
    order.cancelled_time = datetime.now().isoformat()
    db.commit()
    update_courier_rating(db, payload.courier_id)
    return {"status": "cancelled", "order_id": order.order_id}

@app.get("/couriers/{courier_id}/orders", response_model=List[OrderResponse])
def get_courier_orders(
    courier_id: int,
    status: Optional[str] = None,
    db: Session = Depends(get_db)
):
    query = db.query(models.Order).filter(models.Order.courier_id == courier_id)
    if status:
        if status not in ['assigned', 'completed', 'cancelled']:
            raise HTTPException(status_code=400, detail="Недопустимый статус. Допустимые: assigned, completed, cancelled")
        query = query.filter(models.Order.status == status)
    orders = query.all()
    return orders
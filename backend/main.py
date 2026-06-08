from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import models
from database import engine, get_db

models.Base.metadata.create_all(bind=engine)
app = FastAPI(title="Candy Delivery App")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"],
)


class LoginRequest(BaseModel):
    username: str
    password: str

@app.post("/auth/login")
def login(payload: LoginRequest, role: str, db: Session = Depends(get_db)):
    if role == "admin":
        user = db.query(models.Admin).filter(models.Admin.username == payload.username,
                                             models.Admin.password == payload.password).first()
    else:
        user = db.query(models.Courier).filter(models.Courier.username == payload.username,
                                               models.Courier.password == payload.password).first()

    if not user:
        raise HTTPException(status_code=401, detail="Неверный логин или пароль")
    return {"status": "success", "username": user.username, "user_id": user.id, "role": role}

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


@app.get("/users/all")
def get_all_couriers(db: Session = Depends(get_db)):
    return db.query(models.Courier).all()

@app.get("/orders/all")
def get_all_orders(db: Session = Depends(get_db)):
    return db.query(models.Order).all()


@app.post("/orders")
def import_orders(payload: dict, db: Session = Depends(get_db)):
    for o in payload['data']:
        db.add(models.Order(**o))
    db.commit()
    return {"status": "success"}


@app.post("/orders/assign/single")
def assign_single_order(payload: dict, db: Session = Depends(get_db)):
    courier = db.query(models.Courier).filter(models.Courier.id == payload['courier_id']).first()
    order = db.query(models.Order).filter(models.Order.order_id == payload['order_id']).first()

    if not courier or not order:
        raise HTTPException(status_code=404, detail="Курьер или заказ не найден")
    if order.courier_id is not None:
        raise HTTPException(status_code=400, detail="Заказ уже назначен")
    if order.region in courier.regions:
        order.courier_id = courier.id
        db.commit()
        return {"status": "success", "order_id": order.order_id, "courier_id": courier.id}
    else:
        raise HTTPException(status_code=400, detail="Курьер не работает в этом регионе")
from fastapi import FastAPI, Depends, status
from sqlalchemy.orm import Session
from schemas import CouriersPostRequest, OrdersPostRequest
import models
from database import engine, get_db

models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="KDZ Candy Delivery App")

@app.get("/")
def read_root():
    return {"status": "Running and connected to DB kdz"}

@app.post("/couriers", status_code=status.HTTP_201_CREATED)
def import_couriers(payload: CouriersPostRequest, db: Session = Depends(get_db)):
    imported_couriers = []
    for courier_data in payload.couriers:
        db_courier = models.Courier(
            courier_id=courier_data.courier_id,
            courier_type=courier_data.courier_type,
            regions=courier_data.regions,
            working_hours=courier_data.working_hours
        )
        db.add(db_courier)
        imported_couriers.append({"id": courier_data.courier_id})
    db.commit()
    return {"couriers": imported_couriers}

@app.post("/orders", status_code=status.HTTP_201_CREATED)
def import_orders(payload: OrdersPostRequest, db: Session = Depends(get_db)):
    imported_orders = []
    for order_data in payload.orders:
        db_order = models.Order(
            order_id=order_data.order_id,
            weight=order_data.weight,
            regions=order_data.regions,
            delivery_hours=order_data.delivery_hours,
            cost=order_data.cost
        )
        db.add(db_order)
        imported_orders.append({"id": order_data.order_id})
    db.commit()
    return {"orders": imported_orders}
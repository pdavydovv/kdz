import requests

BASE_URL = "http://127.0.0.1:8000"

def test_api():
    courier_data = {
        "username": "курьер12345",
        "password": "password123",
        "courier_type": "bike",
        "regions": [1, 2],
        "working_hours": ["09:00-18:00"]
    }
    response = requests.post(f"{BASE_URL}/couriers", json=courier_data)
    print(f"Регистрация курьера: {response.status_code}, {response.json()}")
    courier_id = response.json().get("id")

    orders_data = {
        "data": [
            {
                "order_id": 1023123,
                "weight": 5.0,
                "region": 1,
                "delivery_hours": ["10:00-12:00"]
            },
            {
                "order_id": 10512512,
                "weight": 15.0,
                "region": 5,
                "delivery_hours": ["14:00-16:00"]
            }
        ]
    }
    response = requests.post(f"{BASE_URL}/orders", json=orders_data)
    print(f"Импорт заказов: {response.status_code}, {response.json()}")

    assign_data = {
        "courier_id": courier_id,
        "order_id": 101
    }
    response = requests.post(f"{BASE_URL}/orders/assign/single", json=assign_data)
    print(f"Назначение заказа (успех): {response.status_code}, {response.json()}")

    assign_data_fail = {
        "courier_id": courier_id,
        "order_id": 102
    }
    response = requests.post(f"{BASE_URL}/orders/assign/single", json=assign_data_fail)
    print(f"Назначение заказа: {response.status_code}, {response.json()}")


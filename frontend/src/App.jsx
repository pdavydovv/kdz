import React, { useState } from 'react';
import axios from 'axios';
import './App.css';

const API_URL = 'http://localhost:8000';

function App() {
  const [courierId, setCourierId] = useState('');
  const [courierType, setCourierType] = useState('foot');
  const [courierRegions, setCourierRegions] = useState('');
  const [courierHours, setCourierHours] = useState('');

  const [orderId, setOrderId] = useState('');
  const [orderWeight, setOrderWeight] = useState('');
  const [orderRegion, setOrderRegion] = useState('');
  const [orderHours, setOrderHours] = useState('');

  const [assignCourierId, setAssignCourierId] = useState('');
  const [assignOrderId, setAssignOrderId] = useState('');

  const [message, setMessage] = useState('');
  const [error, setError] = useState('');

  const handleCourierSubmit = async (e) => {
    e.preventDefault();
    setMessage(''); setError('');
    const regionsArray = courierRegions.split(',').map(r => parseInt(r.trim())).filter(r => !isNaN(r));
    const hoursArray = courierHours.split(',').map(h => h.trim()).filter(h => h !== '');

    const payload = {
      data: [{ courier_id: parseInt(courierId), courier_type: courierType, regions: regionsArray, working_hours: hoursArray }]
    };

    try {
      await axios.post(`${API_URL}/couriers`, payload);
      setMessage(`Курьер ID ${courierId} успешно добавлен`);
      setCourierId(''); setCourierRegions(''); setCourierHours('');
    } catch (err) {
      setError(err.response?.data?.detail || 'Ошибка при добавлении курьера');
    }
  };

  const handleOrderSubmit = async (e) => {
    e.preventDefault();
    setMessage(''); setError('');
    const hoursArray = orderHours.split(',').map(h => h.trim()).filter(h => h !== '');

    const payload = {
      data: [{ order_id: parseInt(orderId), weight: parseFloat(orderWeight), region: parseInt(orderRegion), delivery_hours: hoursArray }]
    };

    try {
      await axios.post(`${API_URL}/orders`, payload);
      setMessage(`Заказ ID ${orderId} успешно добавлен`);
      setOrderId(''); setOrderWeight(''); setOrderRegion(''); setOrderHours('');
    } catch (err) {
      setError(err.response?.data?.detail || 'Ошибка при добавлении заказа');
    }
  };

  const handleAssignOrders = async (e) => {
    e.preventDefault();
    setMessage(''); setError('');
    if (!assignCourierId || !assignOrderId) return setError('Необходимо заполнить оба поля');

    try {
      const res = await axios.post(`${API_URL}/orders/assign`, {
        courier_id: parseInt(assignCourierId)
      });

      const assignedOrdersCount = res.data.orders ? res.data.orders.length : 0;

      if (assignedOrdersCount > 0) {
        setMessage(`Успешно. Количество назначенных заказов для курьера ID ${assignCourierId}: ${assignedOrdersCount}`);
      } else {
        setError(`Система вернула 0 назначенных заказов для курьера ID ${assignCourierId}. Проверьте соответствие параметров для заказа ID ${assignOrderId}`);
      }

      setAssignCourierId(''); setAssignOrderId('');
    } catch (err) {
      setError(err.response?.data?.detail || 'Ошибка при распределении заказов');
    }
  };

  return (
    <div className="container">
      <h1> Candy Delivery — Панель управления менеджера</h1>

      {message && <div className="alert success">{message}</div>}
      {error && <div className="alert danger">{error}</div>}

      <div className="grid">
        <div className="card">
          <h2>Регистрация курьера</h2>
          <form onSubmit={handleCourierSubmit} className="vertical-form">
            <label>ID Курьера:</label>
            <input type="number" required value={courierId} onChange={(e) => setCourierId(e.target.value)} />

            <label>Тип курьера:</label>
            <select value={courierType} onChange={(e) => setCourierType(e.target.value)}>
              <option value="foot">Пешком (foot)</option>
              <option value="bike">Велосипед (bike)</option>
              <option value="car">Автомобиль (car)</option>
            </select>

            <label>Регионы:</label>
            <input type="text" required value={courierRegions} onChange={(e) => setCourierRegions(e.target.value)} />

            <label>Часы работы:</label>
            <input type="text" required value={courierHours} onChange={(e) => setCourierHours(e.target.value)} />

            <button type="submit" className="btn-primary">Зарегистрировать курьера</button>
          </form>
        </div>

        <div className="card">
          <h2>Создание заказа</h2>
          <form onSubmit={handleOrderSubmit} className="vertical-form">
            <label>ID Заказа:</label>
            <input type="number" required value={orderId} onChange={(e) => setOrderId(e.target.value)} />

            <label>Вес заказа (кг):</label>
            <input type="number" step="0.1" required value={orderWeight} onChange={(e) => setOrderWeight(e.target.value)} />

            <label>Регион доставки:</label>
            <input type="number" required value={orderRegion} onChange={(e) => setOrderRegion(e.target.value)} />

            <label>Часы доставки:</label>
            <input type="text" required value={orderHours} onChange={(e) => setOrderHours(e.target.value)} />

            <button type="submit" className="btn-primary">Создать заказ</button>
          </form>
        </div>
      </div>

      <div className="card">
        <h2>Назначение заказа курьеру</h2>
        <form onSubmit={handleAssignOrders} className="inline-form">
          <input
            type="number"
            required
            placeholder="ID Курьера"
            value={assignCourierId}
            onChange={(e) => setAssignCourierId(e.target.value)}
          />
          <input
            type="number"
            required
            placeholder="ID Заказа"
            value={assignOrderId}
            onChange={(e) => setAssignOrderId(e.target.value)}
            style={{ marginLeft: '10px' }}
          />
          <button type="submit" className="btn-success" style={{ marginLeft: '10px' }}>Выполнить распределение</button>
        </form>
      </div>
    </div>
  );
}

export default App;
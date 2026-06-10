import React, { useState, useEffect } from 'react';
import axios from 'axios';
import './App.css';

const API_URL = 'http://localhost:8000';

function App() {
  // Состояния для входа и роли
  const [role, setRole] = useState(null);
  const [user, setUser] = useState(null);
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');

  // Общие данные
  const [allCouriers, setAllCouriers] = useState([]);
  const [allOrders, setAllOrders] = useState([]);

  // Для курьера: активная вкладка (active / completed / cancelled)
  const [activeTab, setActiveTab] = useState('active');

  // Состояния форм
  const [regData, setRegData] = useState({ username: '', password: '', type: 'foot', regions: '', hours: '' });
  const [orderData, setOrderData] = useState({ id: '', weight: '', region: '', hours: '', price: '' });
  const [selectedCourierId, setSelectedCourierId] = useState('');
  const [selectedOrderId, setSelectedOrderId] = useState('');

  const [message, setMessage] = useState('');
  const [error, setError] = useState('');

  const timeRegex = /^([01]\d|2[0-3]):([0-5]\d)-([01]\d|2[0-3]):([0-5]\d)$/;

  const formatError = (err) => err.response?.data?.detail || err.message;

  // Загрузка курьеров и заказов
  const fetchData = async () => {
    try {
      const [cRes, oRes] = await Promise.all([
        axios.get(`${API_URL}/users/all`),
        axios.get(`${API_URL}/orders/all`)
      ]);
      setAllCouriers(cRes.data);
      setAllOrders(oRes.data);
      setError('');
    } catch (err) {
      setError('Ошибка загрузки: ' + formatError(err));
    }
  };

  // Логин
  const handleLogin = async (e) => {
    e.preventDefault();
    try {
      const res = await axios.post(`${API_URL}/auth/login?role=${role}`, { username, password });
      setUser(res.data);
      fetchData();
    } catch (err) {
      setError(formatError(err));
    }
  };

  // Регистрация курьера (админ)
  const handleRegisterCourier = async () => {
    if (!timeRegex.test(regData.hours)) {
      setError("Ошибка времени: формат должен быть HH:MM-HH:MM");
      return;
    }
    try {
      await axios.post(`${API_URL}/couriers`, {
        username: regData.username,
        password: regData.password,
        courier_type: regData.type,
        regions: regData.regions.split(',').map(Number),
        working_hours: [regData.hours]
      });
      setMessage('Курьер зарегистрирован!');
      setError('');
      fetchData();
    } catch (err) {
      setError('Ошибка регистрации: ' + formatError(err));
    }
  };

  // Создание заказа (админ)
  const handleCreateOrder = async () => {
    if (!timeRegex.test(orderData.hours)) {
      setError("Ошибка времени: формат должен быть HH:MM-HH:MM");
      return;
    }
    try {
      await axios.post(`${API_URL}/orders`, {
        data: [{
          order_id: parseInt(orderData.id),
          weight: parseFloat(orderData.weight),
          region: parseInt(orderData.region),
          delivery_hours: [orderData.hours],
          price: parseFloat(orderData.price)
        }]
      });
      setMessage('Заказ создан!');
      setError('');
      setOrderData({ id: '', weight: '', region: '', hours: '', price: '' });
      fetchData();
    } catch (err) {
      setError('Ошибка: ' + formatError(err));
    }
  };

  // Назначение заказа (админ)
  const handleAssignSingle = async () => {
    try {
      await axios.post(`${API_URL}/orders/assign/single`, {
        courier_id: parseInt(selectedCourierId),
        order_id: parseInt(selectedOrderId)
      });
      setMessage(`Заказ #${selectedOrderId} назначен курьеру`);
      fetchData();
    } catch (err) {
      setError('Ошибка: ' + formatError(err));
    }
  };

  // Завершение заказа (курьер)
  const handleCompleteOrder = async (orderId) => {
    try {
      await axios.post(`${API_URL}/orders/complete`, {
        courier_id: user.id,
        order_id: orderId,
        complete_time: new Date().toISOString()
      });
      setMessage(`Заказ #${orderId} доставлен!`);
      setError('');
      fetchData();
    } catch (err) {
      setError('Ошибка завершения: ' + formatError(err));
    }
  };

  // Отмена заказа (курьер)
  const handleCancelOrder = async (orderId) => {
    if (window.confirm(`Отменить заказ #${orderId}?`)) {
      try {
        await axios.post(`${API_URL}/orders/cancel`, {
          courier_id: user.id,
          order_id: orderId
        });
        setMessage(`Заказ #${orderId} отменён.`);
        setError('');
        fetchData();
      } catch (err) {
        setError('Ошибка отмены: ' + formatError(err));
      }
    }
  };

  // Получение текущего курьера и цены
  const currentCourier = allCouriers.find(c => c.id === user?.id);
  const completedOrders = allOrders.filter(o =>
  o.courier_id === user?.id && o.status === 'completed');
  const totalEarnings = completedOrders.reduce((sum, order) => sum + (order.price || 0), 0);

  // Фильтрация заказов курьера по статусу
  const getFilteredOrders = () => {
    const myOrders = allOrders.filter(o => o.courier_id === user?.id);
    if (activeTab === 'active') return myOrders.filter(o => o.status === 'assigned');
    if (activeTab === 'completed') return myOrders.filter(o => o.status === 'completed');
    if (activeTab === 'cancelled') return myOrders.filter(o => o.status === 'cancelled');
    return [];
  };

  // Если роль не выбрана – экран выбора
  if (!role) return (
    <div className="container">
      <h1>Candy Delivery</h1>
      <div style={{ display: 'flex', gap: '20px', justifyContent: 'center' }}>
        <button onClick={() => setRole('admin')}>Администратор</button>
        <button onClick={() => setRole('courier')}>Курьер</button>
      </div>
    </div>
  );

  // Форма входа
  if (!user) return (
    <div className="container">
      <h2>Вход ({role === 'admin' ? 'Администратор' : 'Курьер'})</h2>
      <form onSubmit={handleLogin} className="vertical-form">
        <input placeholder="Логин" value={username} onChange={e => setUsername(e.target.value)} required />
        <input type="password" placeholder="Пароль" value={password} onChange={e => setPassword(e.target.value)} required />
        <button type="submit">Войти</button>
        <button type="button" onClick={() => setRole(null)}>Назад</button>
      </form>
      {error && <div className="alert danger">{error}</div>}
    </div>
  );

  // Основной интерфейс после входа
  return (
    <div className="container">
      <h1>Привет, {user.username}</h1>
      <button onClick={() => { setUser(null); setRole(null); }}>Выйти</button>

      {message && <div className="alert success">{message}</div>}
      {error && <div className="alert danger">{error}</div>}

      {role === 'admin' ? (
        <div className="admin-panel">
          <div className="grid">
            <div className="card">
              <h3>Регистрация курьера</h3>
              <input placeholder="Логин" onChange={e => setRegData({...regData, username: e.target.value})} />
              <input placeholder="Пароль" onChange={e => setRegData({...regData, password: e.target.value})} />
              <select onChange={e => setRegData({...regData, type: e.target.value})}>
                <option value="foot">Пешком</option>
                <option value="bike">Вело</option>
                <option value="car">Авто</option>
              </select>
              <input placeholder="Регионы (1,2,3)" onChange={e => setRegData({...regData, regions: e.target.value})} />
              <input placeholder="Время (09:00-18:00)" onChange={e => setRegData({...regData, hours: e.target.value})} />
              <button onClick={handleRegisterCourier}>Зарегистрировать</button>
            </div>

            <div className="card">
              <h3>Создать заказ</h3>
              <input placeholder="ID Заказа" onChange={e => setOrderData({...orderData, id: e.target.value})} />
              <input placeholder="Вес" onChange={e => setOrderData({...orderData, weight: e.target.value})} />
              <input placeholder="Регион" onChange={e => setOrderData({...orderData, region: e.target.value})} />
              <input placeholder="Время (10:00-12:00)" onChange={e => setOrderData({...orderData, hours: e.target.value})} />
              <input type="number" step="0.01" placeholder="Цена заказа (₽)" onChange={e => setOrderData({...orderData, price: e.target.value})} required />
              <button onClick={handleCreateOrder}>Создать заказ</button>
            </div>
          </div>

          <div className="card">
            <h3>Назначить заказ</h3>
            <select onChange={e => setSelectedCourierId(e.target.value)}>
              <option value="">Выберите курьера</option>
              {allCouriers.map(c => (
                <option key={c.id} value={c.id}>
                  {c.username} (рейтинг: {c.rating})
                </option>
              ))}
            </select>
            <select onChange={e => setSelectedOrderId(e.target.value)}>
              <option value="">Выберите свободный заказ (new)</option>
              {allOrders.filter(o => o.status === 'new').map(o => (
                <option key={o.order_id} value={o.order_id}>Заказ #{o.order_id}</option>
              ))}
            </select>
            <button onClick={handleAssignSingle} className="btn-success">Назначить</button>
          </div>

          <div className="card">
            <h3>Список курьеров с рейтингом</h3>
            <table style={{ width: '100%' }}>
              <thead>
                <tr><th>ID</th><th>Логин</th><th>Тип</th><th>Рейтинг</th><th>Выполнено</th></tr>
              </thead>
              <tbody>
                {allCouriers.map(c => (
                  <tr key={c.id}>
                    <td>{c.id}</td>
                    <td>{c.username}</td>
                    <td>{c.courier_type}</td>
                    <td>{c.rating}</td>
                    <td>{allOrders.filter(o => o.courier_id === c.id && o.status === 'completed').length}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      ) : (
        <div className="courier-panel">
          <div className="card info-tile">
            <h3>⭐ Ваш рейтинг: {currentCourier?.rating ?? '—'}</h3>
            <h3>💰 Заработано: {totalEarnings} ₽</h3>
          </div>

          <div className="tabs" style={{ display: 'flex', gap: '10px', marginBottom: '20px' }}>
            <button className={activeTab === 'active' ? 'btn-primary' : ''} onClick={() => setActiveTab('active')}>
              Активные ({allOrders.filter(o => o.courier_id === user?.id && o.status === 'assigned').length})
            </button>
            <button className={activeTab === 'completed' ? 'btn-primary' : ''} onClick={() => setActiveTab('completed')}>
              Выполненные ({allOrders.filter(o => o.courier_id === user?.id && o.status === 'completed').length})
            </button>
            <button className={activeTab === 'cancelled' ? 'btn-primary' : ''} onClick={() => setActiveTab('cancelled')}>
              Отменённые ({allOrders.filter(o => o.courier_id === user?.id && o.status === 'cancelled').length})
            </button>
          </div>

          <div className="card">
            <h3>
              {activeTab === 'active' && '📦 Активные заказы'}
              {activeTab === 'completed' && '✅ Выполненные заказы'}
              {activeTab === 'cancelled' && '❌ Отменённые заказы'}
            </h3>
            {getFilteredOrders().length === 0 ? (
              <p>Нет заказов</p>
            ) : (
              <table style={{ width: '100%' }}>
                <thead>
                  <tr>
                    <th>ID заказа</th>
                    <th>Вес</th>
                    <th>Регион</th>
                    <th>Время доставки</th>
                    <th>Цена</th>
                    <th>Статус</th>
                    {activeTab === 'active' && <th>Действия</th>}
                  </tr>
                </thead>
                <tbody>
                  {getFilteredOrders().map(order => (
                    <tr key={order.order_id}>
                      <td>{order.order_id}</td>
                      <td>{order.weight} кг</td>
                      <td>{order.region}</td>
                      <td>{order.delivery_hours?.join(', ')}</td>
                      <td>{order.price} ₽</td>
                      <td>
                        {order.status === 'assigned' && '🔄 В работе'}
                        {order.status === 'completed' && '✅ Доставлен'}
                        {order.status === 'cancelled' && '❌ Отменён'}
                      </td>
                      {activeTab === 'active' && (
                        <td>
                          <button onClick={() => handleCompleteOrder(order.order_id)} style={{ marginRight: '8px', backgroundColor: '#10b981' }}>Доставлен</button>
                          <button onClick={() => handleCancelOrder(order.order_id)} style={{ backgroundColor: '#ef4444' }}>Отменить</button>
                        </td>
                      )}
                    </tr>
                  ))}
                </tbody>
              </table>
            )}
          </div>
        </div>
      )}
    </div>
  );
}

export default App;
import React, { useState } from 'react';
import axios from 'axios';
import './App.css';

const API_URL = 'http://localhost:8000';

function App() {
  const [role, setRole] = useState(null);
  const [user, setUser] = useState(null);
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');

  const [allCouriers, setAllCouriers] = useState([]);
  const [allOrders, setAllOrders] = useState([]);

  // Состояния форм
  const [regData, setRegData] = useState({ username: '', password: '', type: 'foot', regions: '', hours: '' });
  const [orderData, setOrderData] = useState({ id: '', weight: '', region: '', hours: '' });
  const [selectedCourierId, setSelectedCourierId] = useState('');
  const [selectedOrderId, setSelectedOrderId] = useState('');

  const [message, setMessage] = useState('');
  const [error, setError] = useState('');

  const timeRegex = /^([01]\d|2[0-3]):([0-5]\d)-([01]\d|2[0-3]):([0-5]\d)$/;

  const formatError = (err) => err.response?.data?.detail || err.message;

  const fetchData = async () => {
    try {
      const [cRes, oRes] = await Promise.all([
        axios.get(`${API_URL}/users/all`),
        axios.get(`${API_URL}/orders/all`)
      ]);
      setAllCouriers(cRes.data);
      setAllOrders(oRes.data);
    } catch (err) { setError('Ошибка загрузки: ' + formatError(err)); }
  };

  const handleLogin = async (e) => {
    e.preventDefault();
    try {
      const res = await axios.post(`${API_URL}/auth/login?role=${role}`, { username, password });
      setUser(res.data);
      fetchData();
    } catch (err) { setError(formatError(err)); }
  };

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
    } catch (err) { setError('Ошибка регистрации: ' + formatError(err)); }
  };

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
          delivery_hours: [orderData.hours]
        }]
      });
      setMessage('Заказ создан!');
      setError('');
      fetchData();
    } catch (err) { setError('Ошибка: ' + formatError(err)); }
  };

  const handleAssignSingle = async () => {
    try {
      await axios.post(`${API_URL}/orders/assign/single`, {
        courier_id: parseInt(selectedCourierId),
        order_id: parseInt(selectedOrderId)
      });
      setMessage(`Заказ #${selectedOrderId} назначен курьеру ${selectedCourierId}`);
      fetchData();
    } catch (err) { setError('Ошибка: ' + formatError(err)); }
  };

  if (!role) return (
    <div className="container">
      <h1>Candy Delivery</h1>
      <button onClick={() => setRole('admin')}>Администратор</button>
      <button onClick={() => setRole('courier')}>Курьер</button>
    </div>
  );

  if (!user) return (
    <div className="container">
      <h2>Вход ({role})</h2>
      <form onSubmit={handleLogin}>
        <input placeholder="Логин" onChange={e => setUsername(e.target.value)} />
        <input type="password" placeholder="Пароль" onChange={e => setPassword(e.target.value)} />
        <button type="submit">Войти</button>
        <button onClick={() => setRole(null)}>Назад</button>
      </form>
      {error && <div className="alert danger">{error}</div>}
    </div>
  );

  return (
    <div className="container">
      <h1>Привет, {user.username}</h1>
      <button onClick={() => {setUser(null); setRole(null);}}>Выйти</button>

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
                <option value="foot">Пешком</option><option value="bike">Вело</option><option value="car">Авто</option>
              </select>
              <input placeholder="Регионы (1,2)" onChange={e => setRegData({...regData, regions: e.target.value})} />
              <input placeholder="Время (09:00-18:00)" onChange={e => setRegData({...regData, hours: e.target.value})} />
              <button onClick={handleRegisterCourier}>Зарегистрировать</button>
            </div>

            <div className="card">
              <h3>Создать заказ</h3>
              <input placeholder="ID Заказа" onChange={e => setOrderData({...orderData, id: e.target.value})} />
              <input placeholder="Вес" onChange={e => setOrderData({...orderData, weight: e.target.value})} />
              <input placeholder="Регион" onChange={e => setOrderData({...orderData, region: e.target.value})} />
              <input placeholder="Время (10:00-12:00)" onChange={e => setOrderData({...orderData, hours: e.target.value})} />
              <button onClick={handleCreateOrder}>Создать заказ</button>
            </div>
          </div>

          <div className="card">
            <h3>Назначить заказ</h3>
            <select onChange={e => setSelectedCourierId(e.target.value)}>
              <option value="">Выберите курьера</option>
              {allCouriers.map(c => <option key={c.id} value={c.id}>{c.username}</option>)}
            </select>
            <select onChange={e => setSelectedOrderId(e.target.value)}>
              <option value="">Выберите свободный заказ</option>
              {allOrders.filter(o => !o.courier_id).map(o => <option key={o.order_id} value={o.order_id}>Заказ #{o.order_id}</option>)}
            </select>
            <button onClick={handleAssignSingle} className="btn-success">Назначить</button>
          </div>
        </div>
      ) : (
        <div className="courier-panel">
          <h2>Ваши заказы</h2>
          <table>
            <thead><tr><th>ID</th><th>Регион</th></tr></thead>
            <tbody>
              {allOrders.filter(o => o.courier_id === user.user_id).map(o => (
                <tr key={o.order_id}><td>{o.order_id}</td><td>{o.region}</td></tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}

export default App;
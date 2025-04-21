import React from 'react';
import ReactDOM from 'react-dom/client';
import { Provider } from 'react-redux';
import { store } from './features/store';
import './index.css';
import App from './App';
import { setAuthToken } from './api';

// Set auth token if available in localStorage
const token = localStorage.getItem('token');
if (token) {
  setAuthToken(token);
}

ReactDOM.createRoot(document.getElementById('root')).render(
  <React.StrictMode>
    <Provider store={store}>
      <App />
    </Provider>
  </React.StrictMode>
);

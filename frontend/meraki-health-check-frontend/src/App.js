import React from 'react';
import { BrowserRouter as Router, Route, Routes, Navigate } from 'react-router-dom';
import Dashboard from './components/healthchecks/Dashboard';
import Login from './components/healthchecks/Login';
import Register from './components/healthchecks/Register';
import SwitchChecks from './components/healthchecks/SwitchChecks';
import WirelessChecks from './components/healthchecks/WirelessChecks';

function App() {
  return (
    <Router>
      <Routes>
        <Route path="/login" element={<Login />} />
        <Route path="/register" element={<Register />} />
        <Route path="/" element={<PrivateRoute><Dashboard /></PrivateRoute>} />
        <Route path="/switch-checks" element={<PrivateRoute><SwitchChecks /></PrivateRoute>} />
        <Route path="/wireless-checks" element={<PrivateRoute><WirelessChecks /></PrivateRoute>} />
      </Routes>
    </Router>
  );
}

function PrivateRoute({ children }) {
  const isAuthenticated = localStorage.getItem('token');
  return isAuthenticated ? children : <Navigate to="/login" replace />;
}

export default App;
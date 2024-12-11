import React from 'react';
import { Routes, Route } from 'react-router-dom';
import Dashboard from './components/dashboard';
import Login from './components/Login';
import Register from './components/Register';
import TransactionHistory from './components/TransactionHistory';
import ComplianceDashboard from './components/ComplianceDashboard';
import Profile from './components/Profile';

const AppRoutes = () => {
  return (
    <Routes>
      <Route path="/" element={<Dashboard />} />
      <Route path="/login" element={<Login />} />
      <Route path="/register" element={<Register />} />
      <Route path="/transactions" element={<TransactionHistory />} />
      <Route path="/compliance" element={<ComplianceDashboard />} />
      <Route path="/profile" element={<Profile />} />
    </Routes>
  );
};

export default AppRoutes;

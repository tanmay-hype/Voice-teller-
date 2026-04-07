import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';

import Login from './pages/Login';
import Register from './pages/Register';
import Dashboard from './pages/Dashboard';
import Voices from './pages/Voices';
import Stories from './pages/Stories';
import Chat from './pages/Chat';

import Layout from './components/Layout';
import { useAuthStore } from './store/authStore';

/* =========================
   Protected Route Wrapper
========================= */

const ProtectedRoute = ({ children }: { children: React.ReactNode }) => {
  const isAuthenticated = useAuthStore((state) => state.isAuthenticated);

  if (!isAuthenticated) {
    return <Navigate to="/login" replace />;
  }

  return <Layout>{children}</Layout>;
};

/* =========================
   Public Route Guard (NEW)
   Prevent logged-in users from going back to login/register
========================= */

const PublicRoute = ({ children }: { children: React.ReactNode }) => {
  const isAuthenticated = useAuthStore((state) => state.isAuthenticated);

  if (isAuthenticated) {
    return <Navigate to="/dashboard" replace />;
  }

  return children;
};

/* =========================
   APP ROUTES
========================= */

function App() {
  return (
    <Router>
      <div className="min-h-screen bg-slate-950 text-white">
        <Routes>
          
          {/* Public Routes */}
          <Route path="/login" element={<PublicRoute><Login /></PublicRoute>} />
          <Route path="/register" element={<PublicRoute><Register /></PublicRoute>} />

          {/* Protected Routes */}
          <Route path="/dashboard" element={<ProtectedRoute><Dashboard /></ProtectedRoute>} />
          <Route path="/dashboard/voices" element={<ProtectedRoute><Voices /></ProtectedRoute>} />
          <Route path="/dashboard/stories" element={<ProtectedRoute><Stories /></ProtectedRoute>} />
          <Route path="/dashboard/chat" element={<ProtectedRoute><Chat /></ProtectedRoute>} />

          {/* Redirects */}
          <Route path="/" element={<Navigate to="/dashboard" replace />} />
          <Route path="*" element={<Navigate to="/dashboard" replace />} />

        </Routes>
      </div>
    </Router>
  );
}

export default App;


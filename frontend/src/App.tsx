import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';

import Login from './pages/Login';
import Register from './pages/Register';
import Dashboard from './pages/Dashboard';
import Voices from './pages/Voices';
import Stories from './pages/Stories';
import Chat from './pages/Chat';

import Layout from './components/Layout';
import { useAuthStore } from './store/authStore';

/* Pure route guards that receive auth from App (avoid store reads inside guards) */
const ProtectedRoute = ({ children, isAuthenticated, token }: { children: React.ReactNode; isAuthenticated: boolean; token: string | null }) => {
  if (!isAuthenticated || !token) return <Navigate to="/login" replace />;
  return <Layout>{children}</Layout>;
};

const PublicRoute = ({ children, isAuthenticated, token }: { children: React.ReactNode; isAuthenticated: boolean; token: string | null }) => {
  if (isAuthenticated && token) return <Navigate to="/dashboard" replace />;
  return <>{children}</>;
};

function App() {
  const hasHydrated = useAuthStore((s) => s.hasHydrated);
  const isAuthenticated = useAuthStore((s) => s.isAuthenticated);
  const token = useAuthStore((s) => s.token);

  if (!hasHydrated) {
    return (
      <div className="min-h-screen relative flex items-center justify-center">
        <div className="animated-gradient" />
        <div className="animate-spin h-8 w-8 rounded-full border-2 border-white/70 border-t-transparent" />
      </div>
    );
  }

  return (
    <Router>
      <div className="min-h-screen relative text-[var(--text-primary)]">
        <div className="animated-gradient" />
        <Routes>
          <Route path="/login" element={<PublicRoute isAuthenticated={isAuthenticated} token={token}><Login /></PublicRoute>} />
          <Route path="/register" element={<PublicRoute isAuthenticated={isAuthenticated} token={token}><Register /></PublicRoute>} />

          <Route path="/dashboard" element={<ProtectedRoute isAuthenticated={isAuthenticated} token={token}><Dashboard /></ProtectedRoute>} />
          <Route path="/dashboard/voices" element={<ProtectedRoute isAuthenticated={isAuthenticated} token={token}><Voices /></ProtectedRoute>} />
          <Route path="/dashboard/stories" element={<ProtectedRoute isAuthenticated={isAuthenticated} token={token}><Stories /></ProtectedRoute>} />
          <Route path="/dashboard/chat" element={<ProtectedRoute isAuthenticated={isAuthenticated} token={token}><Chat /></ProtectedRoute>} />

          <Route path="/" element={<Navigate to="/login" replace />} />
          <Route path="*" element={<Navigate to="/login" replace />} />
        </Routes>
      </div>
    </Router>
  );
}

export default App;


import React, { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import axios from 'axios';
import apiClient from '../services/apiClient';
import { Mic2, Loader2 } from 'lucide-react';

const Register: React.FC = () => {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();

  const handleRegister = async (e: React.FormEvent) => {
    e.preventDefault();

    if (password !== confirmPassword) {
      return setError('Passwords do not match');
    }

    if (!email || !password) {
      return setError('Please fill in all fields');
    }

    setError('');
    setLoading(true);

    try {
      await apiClient.post('/auth/register', {
        email,
        password,
      });

      navigate('/login', { state: { message: 'Registration successful! Please login.' } });
    } catch (err: unknown) {
      if (axios.isAxiosError<{ detail?: string }>(err)) {
        setError(err.response?.data?.detail || 'Failed to register. Please try again.');
      } else {
        setError('Failed to register. Please try again.');
      }
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-[var(--bg-primary)] flex flex-col justify-center py-12 sm:px-6 lg:px-8 bg-gradient-to-br from-white via-[var(--bg-primary)] to-blue-50 page-enter">
      <div className="sm:mx-auto sm:w-full sm:max-w-md scale-in">
        <div className="flex justify-center">
          <div className="w-16 h-16 bg-[var(--accent)] rounded-2xl flex items-center justify-center shadow-lg shadow-[var(--accent)]/20">
            <Mic2 className="w-8 h-8 text-white" />
          </div>
        </div>
        <h2 className="mt-6 text-center text-3xl font-extrabold text-[var(--text-strong)] tracking-tight">
          Create an account
        </h2>
        <p className="mt-2 text-center text-sm text-[var(--text-muted)]">
          Join us to start generating voice stories
        </p>
      </div>

      <div className="mt-8 sm:mx-auto sm:w-full sm:max-w-md slide-up" style={{ animationDelay: '0.1s' }}>
        <div className="card bg-white border border-[var(--border)] shadow-xl sm:rounded-2xl">
          <form className="space-y-6" onSubmit={handleRegister}>
            {error && (
              <div className="bg-red-50 border border-red-200 text-red-700 p-3 rounded-lg text-sm">
                {error}
              </div>
            )}

            <div>
              <label className="block text-sm font-medium text-[var(--text-strong)]">Email address</label>
              <div className="mt-1">
                <input
                  type="email"
                  required
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  className="input-field"
                  placeholder="you@example.com"
                />
              </div>
            </div>

            <div>
              <label className="block text-sm font-medium text-[var(--text-strong)]">Password</label>
              <div className="mt-1">
                <input
                  type="password"
                  required
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  className="input-field"
                  placeholder="••••••••"
                />
              </div>
            </div>

            <div>
              <label className="block text-sm font-medium text-[var(--text-strong)]">Confirm Password</label>
              <div className="mt-1">
                <input
                  type="password"
                  required
                  value={confirmPassword}
                  onChange={(e) => setConfirmPassword(e.target.value)}
                  className="input-field"
                  placeholder="••••••••"
                />
              </div>
            </div>

            <div>
              <button
                type="submit"
                disabled={loading}
                className="btn-primary w-full flex justify-center items-center gap-2 text-white font-medium hover:shadow-lg disabled:opacity-50 disabled:cursor-not-allowed"
              >
                {loading ? <Loader2 className="w-5 h-5 animate-spin" /> : 'Register'}
              </button>
            </div>
          </form>

          <div className="mt-6 text-center text-sm text-[var(--text-muted)]">
            Already have an account?{' '}
            <Link to="/login" className="font-medium text-[var(--accent)] hover:text-[var(--accent-hover)]">
              Sign in
            </Link>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Register;

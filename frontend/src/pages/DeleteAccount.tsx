import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { AlertTriangle, ArrowLeft, Loader2 } from 'lucide-react';
import apiClient from '../services/apiClient';
import { useAuthStore } from '../store/authStore';

const DeleteAccount: React.FC = () => {
  const navigate = useNavigate();
  const logout = useAuthStore((s) => s.logout);
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const handleDelete = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    try {
      await apiClient.delete('/users/me', {
        data: { password },
      });
      logout();
      navigate('/login');
    } catch {
      setError('Password is incorrect or the account could not be deleted.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="max-w-2xl mx-auto space-y-6">
      <div>
        <Link to="/dashboard/account" className="inline-flex items-center gap-2 text-sm text-[var(--text-muted)] hover:text-[var(--text-strong)] transition">
          <ArrowLeft className="w-4 h-4" /> Back to account
        </Link>
        <h1 className="mt-3 text-3xl font-bold text-[var(--text-strong)]">Delete Account</h1>
        <p className="text-[var(--text-muted)] mt-2">This action will deactivate your account and mark it as deleted. Your record will remain in the database.</p>
      </div>

      <div className="rounded-3xl border border-red-200 bg-red-50 p-6 shadow-xl space-y-5">
        <div className="flex items-start gap-3 text-red-700">
          <AlertTriangle className="w-5 h-5 mt-0.5" />
          <div>
            <h2 className="font-semibold">Are you sure?</h2>
            <p className="text-sm text-red-700/90">To delete your account, confirm your password below. The account will be marked as deleted instead of removing the row.</p>
          </div>
        </div>

        {error && <div className="rounded-xl border border-red-200 bg-white p-4 text-sm text-red-700">{error}</div>}

        <form onSubmit={handleDelete} className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-[var(--text-strong)] mb-2">Password</label>
            <input
              type="password"
              required
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              className="input-field bg-white"
              placeholder="Enter your password"
            />
          </div>

          <div className="flex flex-col sm:flex-row gap-3 justify-end">
            <Link
              to="/dashboard/account"
              className="inline-flex items-center justify-center rounded-xl border border-[var(--border)] bg-white px-5 py-3 text-sm font-semibold text-[var(--text-strong)] hover:bg-[var(--hover-bg)] transition"
            >
              Cancel
            </Link>
            <button
              type="submit"
              disabled={loading}
              className="inline-flex items-center justify-center gap-2 rounded-xl bg-red-600 px-6 py-3 text-sm font-semibold text-white hover:bg-red-700 disabled:opacity-50"
            >
              {loading ? <Loader2 className="w-4 h-4 animate-spin" /> : 'Confirm Delete'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

export default DeleteAccount;

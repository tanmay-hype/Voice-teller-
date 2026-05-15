import React, { useState, useEffect } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import axios from 'axios';
import apiClient from '../services/apiClient';
import { Mic2, Loader2, ShieldCheck } from 'lucide-react';

const Register: React.FC = () => {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [otp, setOtp] = useState('');
  const [step, setStep] = useState<'register' | 'verify'>('register');
  const [error, setError] = useState('');
  const [message, setMessage] = useState('');
  const [loading, setLoading] = useState(false);
  const [cooldownRemaining, setCooldownRemaining] = useState<number>(0);
  const navigate = useNavigate();

  useEffect(() => {
    if (cooldownRemaining <= 0) return;
    const id = setInterval(() => setCooldownRemaining((c) => Math.max(0, c - 1)), 1000);
    return () => clearInterval(id);
  }, [cooldownRemaining]);

  const handleSendOtp = async (e: React.FormEvent) => {
    e.preventDefault();

    if (password !== confirmPassword) {
      return setError('Passwords do not match');
    }

    if (!email || !password) {
      return setError('Please fill in all fields');
    }

    setError('');
    setMessage('');
    setLoading(true);

    try {
      const response = await apiClient.post('/auth/register', {
        email,
        password,
      });

      setStep('verify');
      setMessage(response.data?.message || 'OTP sent to your email.');
    } catch (err: unknown) {
      if (axios.isAxiosError<{ detail?: string }>(err)) {
        const status = err.response?.status;
        const detail = err.response?.data?.detail || '';
        if (status === 429) {
          const m = /(?:(\d+)\s*seconds?)?/i.exec(detail);
          if (m && m[1]) setCooldownRemaining(parseInt(m[1], 10));
          setError(detail || 'Please wait before requesting another code.');
        } else {
          setError(detail || 'Failed to register. Please try again.');
        }
      } else {
        setError('Failed to register. Please try again.');
      }
    } finally {
      setLoading(false);
    }
  };

  const handleVerifyOtp = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!otp) {
      return setError('Please enter the verification code');
    }

    setError('');
    setMessage('');
    setLoading(true);

    try {
      const response = await apiClient.post('/auth/verify-otp', {
        email,
        otp,
      });

      navigate('/login', { state: { message: response.data?.message || 'Email verified successfully. Please log in.' } });
    } catch (err: unknown) {
      if (axios.isAxiosError<{ detail?: string }>(err)) {
        setError(err.response?.data?.detail || 'Failed to verify OTP. Please try again.');
      } else {
        setError('Failed to verify OTP. Please try again.');
      }
    } finally {
      setLoading(false);
    }
  };

  const handleResendOtp = async () => {
    if (password !== confirmPassword) {
      return setError('Passwords do not match');
    }

    if (!email || !password) {
      return setError('Please fill in all fields');
    }

    setError('');
    setMessage('');
    setLoading(true);

    try {
      const response = await apiClient.post('/auth/register', {
        email,
        password,
      });

      setStep('verify');
      setMessage(response.data?.message || 'OTP sent to your email.');
    } catch (err: unknown) {
      if (axios.isAxiosError<{ detail?: string }>(err)) {
        const status = err.response?.status;
        const detail = err.response?.data?.detail || '';
        if (status === 429) {
          const m = /(?:(\d+)\s*seconds?)?/i.exec(detail);
          if (m && m[1]) setCooldownRemaining(parseInt(m[1], 10));
          setError(detail || 'Please wait before requesting another code.');
        } else {
          setError(detail || 'Failed to resend OTP. Please try again.');
        }
      } else {
        setError('Failed to resend OTP. Please try again.');
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
          <form className="space-y-6" onSubmit={step === 'register' ? handleSendOtp : handleVerifyOtp}>
            {error && (
              <div className="bg-red-50 border border-red-200 text-red-700 p-3 rounded-lg text-sm">
                {error}
              </div>
            )}

            {message && (
              <div className="bg-green-50 border border-green-200 text-green-700 p-3 rounded-lg text-sm">
                {message}
              </div>
            )}
            {cooldownRemaining > 0 && (
              <div className="bg-yellow-50 border border-yellow-200 text-yellow-800 p-3 rounded-lg text-sm">
                Please wait {cooldownRemaining} second{cooldownRemaining !== 1 ? 's' : ''} before requesting another code.
              </div>
            )}

            {step === 'register' ? (
              <>
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
              </>
            ) : (
              <>
                <div className="rounded-xl border border-blue-200 bg-blue-50 p-4 text-sm text-blue-900">
                  <div className="flex items-center gap-2 font-medium">
                    <ShieldCheck className="w-4 h-4" />
                    Verify your email
                  </div>
                  <p className="mt-2">We sent a one-time code to {email}. Enter it below to finish registration.</p>
                </div>

                <div>
                  <label className="block text-sm font-medium text-[var(--text-strong)]">Verification code</label>
                  <div className="mt-1">
                    <input
                      type="text"
                      inputMode="numeric"
                      autoComplete="one-time-code"
                      required
                      value={otp}
                      onChange={(e) => setOtp(e.target.value)}
                      className="input-field tracking-[0.35em] text-center font-semibold"
                      placeholder="123456"
                      maxLength={6}
                    />
                  </div>
                </div>
              </>
            )}

            <div>
              <button
                type="submit"
                disabled={loading || (step === 'register' && cooldownRemaining > 0)}
                className="btn-primary w-full flex justify-center items-center gap-2 text-white font-medium hover:shadow-lg disabled:opacity-50 disabled:cursor-not-allowed"
              >
                {loading ? (
                  <Loader2 className="w-5 h-5 animate-spin" />
                ) : step === 'register' ? (
                  cooldownRemaining > 0 ? `Wait ${cooldownRemaining}s` : 'Send OTP'
                ) : (
                  'Verify & Continue'
                )}
              </button>
            </div>

            {step === 'verify' && (
              <button
                type="button"
                onClick={() => { void handleResendOtp(); }}
                disabled={loading || cooldownRemaining > 0}
                className="w-full text-sm font-medium text-[var(--accent)] hover:text-[var(--accent-hover)] disabled:opacity-50"
              >
                {cooldownRemaining > 0 ? `Resend (${cooldownRemaining}s)` : 'Resend code'}
              </button>
            )}
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

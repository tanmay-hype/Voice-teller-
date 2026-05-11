import React, { useState, useEffect } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import axios from 'axios';
import apiClient from '../services/apiClient';
import { Mic2, Loader2, } from 'lucide-react';

const Register: React.FC = () => {
  const [step, setStep] = useState<'form' | 'otp'>('form');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [otp, setOtp] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const [latitude, setLatitude] = useState<number | null>(null);
  const [longitude, setLongitude] = useState<number | null>(null);
  const [locationLoading, setLocationLoading] = useState(true);
  const [otpExpiry, setOtpExpiry] = useState(15);
  const navigate = useNavigate();

  // Get user location on component mount
  useEffect(() => {
    if (navigator.geolocation) {
      navigator.geolocation.getCurrentPosition(
        (position) => {
          setLatitude(position.coords.latitude);
          setLongitude(position.coords.longitude);
          setLocationLoading(false);
        },
        (error) => {
          console.warn('Geolocation error:', error);
          setLocationLoading(false);
        },
        {
          enableHighAccuracy: true,
          timeout: 10000,
          maximumAge: 0
        }
      );
    } else {
      setLocationLoading(false);
    }
  }, []);

  // OTP timer
  useEffect(() => {
    if (step === 'otp' && otpExpiry > 0) {
      const timer = setTimeout(() => setOtpExpiry(otpExpiry - 1), 1000);
      return () => clearTimeout(timer);
    }
  }, [otpExpiry, step]);

  const handleRequestOTP = async (e: React.FormEvent) => {
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
      await apiClient.post('/auth/register/request-otp', {
        email,
        password,
        latitude,
        longitude,
      });

      setStep('otp');
      setOtpExpiry(15 * 60); // 15 minutes in seconds
    } catch (err: unknown) {
      if (axios.isAxiosError<{ detail?: string }>(err)) {
        setError(err.response?.data?.detail || 'Failed to request OTP. Please try again.');
      } else {
        setError('Failed to request OTP. Please try again.');
      }
    } finally {
      setLoading(false);
    }
  };

  const handleVerifyOTP = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!otp || otp.length !== 6) {
      return setError('Please enter a valid 6-digit OTP');
    }

    setError('');
    setLoading(true);

    try {
      await apiClient.post('/auth/register/verify-otp', {
        email,
        otp,
        password,
        latitude,
        longitude,
      });

      // Redirect to login
      navigate('/login', { state: { message: 'Registration successful! Please login.' } });
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

  const handleResendOTP = async () => {
    setError('');
    setLoading(true);
    
    try {
      await apiClient.post('/auth/register/request-otp', {
        email,
        password,
        latitude,
        longitude,
      });
      
      setOtpExpiry(15 * 60);
      setError('');
    } catch (err: unknown) {
      if (axios.isAxiosError<{ detail?: string }>(err)) {
        setError(err.response?.data?.detail || 'Failed to resend OTP.');
      } else {
        setError('Failed to resend OTP.');
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
          
          {/* STEP 1: Registration Form */}
          {step === 'form' && (
            <form className="space-y-6" onSubmit={handleRequestOTP}>
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
                  disabled={loading || locationLoading}
                  className="btn-primary w-full flex justify-center items-center gap-2 text-white font-medium hover:shadow-lg disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  {loading ? <Loader2 className="w-5 h-5 animate-spin" /> : 'Continue'}
                </button>
              </div>
            </form>
          )}

          {/* STEP 2: OTP Verification */}
          {step === 'otp' && (
            <form className="space-y-6" onSubmit={handleVerifyOTP}>
              {error && (
                <div className="bg-red-50 border border-red-200 text-red-700 p-3 rounded-lg text-sm">
                  {error}
                </div>
              )}

              <div className="bg-blue-50 border border-blue-200 p-4 rounded-lg">
                <p className="text-sm text-blue-900">
                  <span className="font-semibold">Verification Code Sent!</span>
                  <br />
                  We've sent a 6-digit OTP to <strong>{email}</strong>
                </p>
              </div>

              <div>
                <label className="block text-sm font-medium text-[var(--text-strong)]">Enter OTP</label>
                <div className="mt-1">
                  <input
                    type="text"
                    maxLength={6}
                    placeholder="000000"
                    value={otp}
                    onChange={(e) => setOtp(e.target.value.replace(/\D/g, ''))}
                    className="input-field text-center text-2xl tracking-widest font-mono"
                  />
                </div>
                <p className="text-xs text-[var(--text-muted)] mt-2">
                  ⏱️ Code expires in {Math.floor(otpExpiry / 60)}:{String(otpExpiry % 60).padStart(2, '0')}
                </p>
              </div>

              <div>
                <button
                  type="submit"
                  disabled={loading || otp.length !== 6}
                  className="btn-primary w-full flex justify-center items-center gap-2 text-white font-medium hover:shadow-lg disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  {loading ? <Loader2 className="w-5 h-5 animate-spin" /> : 'Verify & Register'}
                </button>
              </div>

              <div className="flex gap-2">
                <button
                  type="button"
                  onClick={() => {
                    setStep('form');
                    setOtp('');
                  }}
                  className="btn-secondary flex-1 py-2 px-4 text-sm"
                >
                  Back
                </button>
                <button
                  type="button"
                  onClick={handleResendOTP}
                  disabled={loading || otpExpiry > 0}
                  className="btn-secondary flex-1 py-2 px-4 text-sm disabled:opacity-50"
                >
                  Resend OTP
                </button>
              </div>
            </form>
          )}

          {/* Sign in link */}
          <div className="mt-6 text-center text-sm">
            <span className="text-[var(--text-muted)]">Already have an account? </span>
            <Link to="/login" className="font-medium text-[var(--accent)] hover:text-[var(--accent-600)]">
              Sign in
            </Link>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Register;

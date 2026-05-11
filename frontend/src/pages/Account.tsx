import React, { useEffect, useMemo, useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { Camera, Loader2, Trash2, ArrowLeft } from 'lucide-react';
import apiClient from '../services/apiClient';
import { useAuthStore } from '../store/authStore';

interface UserProfile {
  id: string;
  email: string;
  first_name?: string | null;
  last_name?: string | null;
  contact_no?: string | null;
  profile_picture_url?: string | null;
  status?: string;
}

const Account: React.FC = () => {
  const navigate = useNavigate();
  const token = useAuthStore((s) => s.token);
  const login = useAuthStore((s) => s.login);
  const authUser = useAuthStore((s) => s.user);

  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const [user, setUser] = useState<UserProfile | null>(null);
  const [firstName, setFirstName] = useState('');
  const [lastName, setLastName] = useState('');
  const [contactNo, setContactNo] = useState('');
  const [email, setEmail] = useState('');
  const [profilePictureFile, setProfilePictureFile] = useState<File | null>(null);
  const [previewUrl, setPreviewUrl] = useState('');

  useEffect(() => {
    const fetchProfile = async () => {
      try {
        const response = await apiClient.get('/users/me');
        const profile = response.data as UserProfile;
        setUser(profile);
        setFirstName(profile.first_name || '');
        setLastName(profile.last_name || '');
        setContactNo(profile.contact_no || '');
        setEmail(profile.email || '');
        setPreviewUrl(profile.profile_picture_url ? `${import.meta.env.VITE_API_URL?.replace(/\/api\/?$/, '') || 'http://localhost:8000'}${profile.profile_picture_url}` : '');
      } catch (err) {
        setError('Failed to load profile. Please try again.');
      } finally {
        setLoading(false);
      }
    };

    fetchProfile();
  }, []);

  const avatarText = useMemo(() => {
    const source = firstName || authUser?.email || 'U';
    return source.charAt(0).toUpperCase();
  }, [firstName, authUser?.email]);

  const handlePictureChange = (file: File | null) => {
    setProfilePictureFile(file);
    if (file) {
      const objectUrl = URL.createObjectURL(file);
      setPreviewUrl(objectUrl);
    }
  };

  const handleSaveProfile = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setSuccess('');
    setSaving(true);

    try {
      const formData = new FormData();
      formData.append('first_name', firstName.trim());
      formData.append('last_name', lastName.trim());
      formData.append('contact_no', contactNo.trim());
      formData.append('email', email.trim());
      if (profilePictureFile) {
        formData.append('profile_picture', profilePictureFile);
      }

      const response = await apiClient.put('/users/me', formData, {
        headers: { 'Content-Type': 'multipart/form-data' },
      });

      const updatedUser = response.data as UserProfile;
      setUser(updatedUser);
      setSuccess('Profile saved successfully.');

      if (token) {
        login({ id: updatedUser.id, email: updatedUser.email }, token);
      }
    } catch (err: unknown) {
      setError('Failed to save profile. Please try again.');
    } finally {
      setSaving(false);
    }
  };

  const profileImage = previewUrl || '';

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-[60vh]">
        <Loader2 className="w-8 h-8 animate-spin text-[var(--accent)]" />
      </div>
    );
  }

  return (
    <div className="max-w-4xl mx-auto space-y-6">
      <div className="flex items-center justify-between gap-4">
        <div>
          <Link to="/dashboard" className="inline-flex items-center gap-2 text-sm text-[var(--text-muted)] hover:text-[var(--text-strong)] transition">
            <ArrowLeft className="w-4 h-4" /> Back to dashboard
          </Link>
          <h1 className="mt-3 text-3xl font-bold text-[var(--text-strong)]">My Account</h1>
          <p className="text-[var(--text-muted)] mt-2">Update your profile details and account information.</p>
        </div>
        <span className="rounded-full px-4 py-2 text-sm font-medium bg-emerald-50 text-emerald-700 border border-emerald-200">
          {user?.status || 'active'}
        </span>
      </div>

      <form onSubmit={handleSaveProfile} className="space-y-6">
        {error && <div className="rounded-xl border border-red-200 bg-red-50 p-4 text-sm text-red-700">{error}</div>}
        {success && <div className="rounded-xl border border-emerald-200 bg-emerald-50 p-4 text-sm text-emerald-700">{success}</div>}

        <div className="card bg-white border border-[var(--border)] shadow-xl rounded-3xl p-6 space-y-6">
          <div className="flex items-center gap-5">
            <div className="relative">
              <div className="w-24 h-24 rounded-full bg-[var(--accent-bg)] text-[var(--accent)] overflow-hidden flex items-center justify-center text-3xl font-bold border border-[var(--border)]">
                {profileImage ? (
                  <img src={profileImage} alt="Profile preview" className="w-full h-full object-cover" />
                ) : (
                  avatarText
                )}
              </div>
              <label className="absolute -bottom-2 -right-2 w-9 h-9 rounded-full bg-[var(--accent)] text-white flex items-center justify-center cursor-pointer shadow-lg hover:scale-105 transition">
                <Camera className="w-4 h-4" />
                <input
                  type="file"
                  accept="image/*"
                  className="hidden"
                  onChange={(e) => handlePictureChange(e.target.files?.[0] || null)}
                />
              </label>
            </div>
            <div>
              <h2 className="text-xl font-semibold text-[var(--text-strong)]">Profile picture</h2>
              <p className="text-sm text-[var(--text-muted)]">Upload a new picture to personalize your profile.</p>
            </div>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-5">
            <div>
              <label className="block text-sm font-medium text-[var(--text-strong)] mb-2">First name *</label>
              <input value={firstName} onChange={(e) => setFirstName(e.target.value)} required className="input-field" placeholder="First name" />
            </div>
            <div>
              <label className="block text-sm font-medium text-[var(--text-strong)] mb-2">Last name *</label>
              <input value={lastName} onChange={(e) => setLastName(e.target.value)} required className="input-field" placeholder="Last name" />
            </div>
            <div>
              <label className="block text-sm font-medium text-[var(--text-strong)] mb-2">Contact no *</label>
              <input value={contactNo} onChange={(e) => setContactNo(e.target.value)} required className="input-field" placeholder="Contact number" />
            </div>
            <div>
              <label className="block text-sm font-medium text-[var(--text-strong)] mb-2">Email address</label>
              <input type="email" value={email} onChange={(e) => setEmail(e.target.value)} required className="input-field" placeholder="you@example.com" />
            </div>
          </div>

          <div className="flex flex-col sm:flex-row gap-3 justify-between pt-2">
            <button
              type="button"
              onClick={() => navigate('/dashboard/account/delete')}
              className="inline-flex items-center justify-center gap-2 rounded-xl border border-red-200 bg-red-50 px-5 py-3 text-sm font-semibold text-red-700 hover:bg-red-100 transition"
            >
              <Trash2 className="w-4 h-4" /> Delete Account
            </button>

            <button
              type="submit"
              disabled={saving}
              className="inline-flex items-center justify-center gap-2 rounded-xl bg-[var(--accent)] px-6 py-3 text-sm font-semibold text-white hover:shadow-lg disabled:opacity-50"
            >
              {saving ? <Loader2 className="w-4 h-4 animate-spin" /> : 'Save Profile'}
            </button>
          </div>
        </div>
      </form>
    </div>
  );
};

export default Account;

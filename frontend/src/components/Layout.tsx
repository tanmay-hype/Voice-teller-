import React, { useEffect, useState } from 'react';
import { Link, useLocation, useNavigate } from 'react-router-dom';
import { motion } from 'framer-motion';
import { useAuthStore } from '../store/authStore';
import { Mic2, BookOpen, MessageSquare, LogOut, LayoutDashboard, ChevronDown, UserCircle2, CircleDollarSign } from 'lucide-react';
import clsx from 'clsx';
const Layout: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const logout = useAuthStore((s) => s.logout);
  const user = useAuthStore((s) => s.user);
  const location = useLocation();
  const navigate = useNavigate();
  const [accountMenuOpen, setAccountMenuOpen] = useState(false);

  const navigation = [
    { name: 'Dashboard', href: '/dashboard', icon: LayoutDashboard },
    { name: 'Voices', href: '/dashboard/voices', icon: Mic2 },
    { name: 'Stories', href: '/dashboard/stories', icon: BookOpen },
    { name: 'Chat', href: '/dashboard/chat', icon: MessageSquare },
  ];

  useEffect(() => {
    setAccountMenuOpen(false);
  }, [location.pathname]);

  return (
    <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} transition={{ duration: 0.6 }} className="flex h-screen bg-[var(--bg-primary)] font-sans text-[var(--text-primary)] transition-colors relative overflow-hidden">
      {/* Sidebar */}
      <div className="w-64 bg-[var(--sidebar-bg)] border-r border-[var(--border)] flex flex-col">
        <div className="h-16 flex items-center px-6 border-b border-[var(--border)] shrink-0">
          <div className="w-8 h-8 bg-[var(--accent)] rounded-xl flex items-center justify-center mr-3 shadow-md">
            <Mic2 className="w-5 h-5 text-white" />
          </div>
          <span className="text-[var(--text-strong)] font-bold tracking-wide">AIVoice</span>
        </div>
        
        <div className="flex-1 px-4 py-6 overflow-y-auto space-y-1">
          {navigation.map((item) => {
            const Icon = item.icon;
            const isActive = location.pathname === item.href || 
                            (item.href !== '/dashboard' && location.pathname.startsWith(item.href));
            return (
              <Link
                key={item.name}
                to={item.href}
                className={clsx(
                  "flex items-center px-3 py-2.5 rounded-lg text-sm font-medium transition-all duration-200 group",
                  isActive 
                    ? "bg-[var(--accent-bg)] text-[var(--accent)]" 
                    : "text-[var(--text-muted)] hover:bg-[var(--hover-bg)] hover:text-[var(--text-strong)]"
                )}
              >
                <Icon className={clsx("w-5 h-5 mr-3 flex-shrink-0 transition-colors", isActive ? "text-[var(--accent)]" : "text-[var(--text-muted)] group-hover:text-[var(--text-strong)]")} />
                {item.name}
              </Link>
            );
          })}
        </div>
        
        <div className="p-4 border-t border-slate-800 shrink-0">
          <div className="flex items-center px-3 py-2">
            <div className="w-8 h-8 rounded-full bg-[var(--sidebar-bg)] flex items-center justify-center text-xs font-bold text-[var(--text-strong)] border border-[var(--border)]">
              {user?.email?.charAt(0).toUpperCase() || 'U'}
            </div>
            <div className="ml-3 truncate">
              <p className="text-sm font-medium text-[var(--text-strong)] truncate">{user?.email}</p>
            </div>
          </div>
          <button
            onClick={logout}
            className="mt-4 w-full flex items-center px-3 py-2 text-sm font-medium text-[var(--text-muted)] rounded-lg hover:bg-[var(--hover-bg)] hover:text-[var(--accent)] transition-colors"
          >
            <LogOut className="w-5 h-5 mr-3 shrink-0" />
            Sign out
          </button>
        </div>
      </div>

      {/* Main Content Area */}
      <div className="flex-1 flex flex-col min-w-0 overflow-hidden relative">
        <div className="absolute inset-0 bg-[radial-gradient(ellipse_at_top_right,_var(--tw-gradient-stops))] from-[var(--accent)/8] via-transparent to-transparent pointer-events-none" />
        {/* Decorative blobs */}
        <div aria-hidden className="blob blob--pink" />
        <div aria-hidden className="blob blob--lav" />
        <div aria-hidden className="blob blob--mint" />
        <main className="flex-1 overflow-y-auto p-8 relative z-10">
          <div className="flex justify-end mb-6">
            <div className="relative">
              <button
                type="button"
                onClick={() => setAccountMenuOpen((open) => !open)}
                className="flex items-center gap-3 rounded-2xl border border-[var(--border)] bg-white/80 backdrop-blur px-4 py-2.5 shadow-sm hover:shadow-md transition"
              >
                <div className="w-10 h-10 rounded-full bg-[var(--accent-bg)] text-[var(--accent)] flex items-center justify-center font-semibold overflow-hidden">
                  {user?.email?.charAt(0).toUpperCase() || 'U'}
                </div>
                <div className="text-left hidden sm:block">
                  <p className="text-sm font-semibold text-[var(--text-strong)]">My Account</p>
                  <p className="text-xs text-[var(--text-muted)] truncate max-w-36">{user?.email}</p>
                </div>
                <ChevronDown className="w-4 h-4 text-[var(--text-muted)]" />
              </button>

              {accountMenuOpen && (
                <div className="absolute right-0 mt-3 w-64 rounded-2xl border border-[var(--border)] bg-white shadow-2xl overflow-hidden z-50">
                  <button
                    type="button"
                    onClick={() => navigate('/dashboard/account')}
                    className="w-full flex items-center gap-3 px-4 py-3 text-sm text-[var(--text-strong)] hover:bg-[var(--hover-bg)] transition text-left"
                  >
                    <UserCircle2 className="w-4 h-4 text-[var(--accent)]" />
                    Update Profile
                  </button>
                  <button
                    type="button"
                    disabled
                    className="w-full flex items-center gap-3 px-4 py-3 text-sm text-[var(--text-muted)] cursor-not-allowed bg-slate-50 text-left"
                  >
                    <CircleDollarSign className="w-4 h-4" />
                    Subscriptions <span className="ml-auto text-[10px] uppercase tracking-wider">Soon</span>
                  </button>
                  <button
                    type="button"
                    onClick={logout}
                    className="w-full flex items-center gap-3 px-4 py-3 text-sm text-red-600 hover:bg-red-50 transition text-left"
                  >
                    <LogOut className="w-4 h-4" />
                    Logout
                  </button>
                </div>
              )}
            </div>
          </div>
          <motion.div initial={{ y: 6, opacity: 0 }} animate={{ y: 0, opacity: 1 }} transition={{ duration: 0.45 }} className="max-w-full">
            {children}
          </motion.div>
        </main>
      </div>
    </motion.div>
  );
};

export default Layout;

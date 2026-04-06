import React from 'react';
import { Link, useLocation } from 'react-router-dom';
import { useAuthStore } from '../store/authStore';
import { Mic2, BookOpen, MessageSquare, LogOut, LayoutDashboard } from 'lucide-react';
import clsx from 'clsx';

const Layout: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const { logout, user } = useAuthStore();
  const location = useLocation();

  const navigation = [
    { name: 'Dashboard', href: '/dashboard', icon: LayoutDashboard },
    { name: 'Voices', href: '/dashboard/voices', icon: Mic2 },
    { name: 'Stories', href: '/dashboard/stories', icon: BookOpen },
    { name: 'Chat', href: '/dashboard/chat', icon: MessageSquare },
  ];

  return (
    <div className="flex h-screen bg-slate-950 font-sans text-slate-300">
      {/* Sidebar */}
      <div className="w-64 bg-slate-900 border-r border-slate-800 flex flex-col">
        <div className="h-16 flex items-center px-6 border-b border-slate-800 shrink-0">
          <div className="w-8 h-8 bg-blue-600 rounded-xl flex items-center justify-center mr-3 shadow-lg shadow-blue-600/20">
            <Mic2 className="w-5 h-5 text-white" />
          </div>
          <span className="text-white font-bold tracking-wide">AIVoice</span>
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
                    ? "bg-blue-600/10 text-blue-500" 
                    : "text-slate-400 hover:bg-slate-800 hover:text-white"
                )}
              >
                <Icon className={clsx("w-5 h-5 mr-3 flex-shrink-0 transition-colors", isActive ? "text-blue-500" : "text-slate-500 group-hover:text-slate-300")} />
                {item.name}
              </Link>
            );
          })}
        </div>
        
        <div className="p-4 border-t border-slate-800 shrink-0">
          <div className="flex items-center px-3 py-2">
            <div className="w-8 h-8 rounded-full bg-slate-800 flex items-center justify-center text-xs font-bold text-white border border-slate-700">
              {user?.email?.charAt(0).toUpperCase() || 'U'}
            </div>
            <div className="ml-3 truncate">
              <p className="text-sm font-medium text-white truncate">{user?.email}</p>
            </div>
          </div>
          <button
            onClick={logout}
            className="mt-4 w-full flex items-center px-3 py-2 text-sm font-medium text-slate-400 rounded-lg hover:bg-red-500/10 hover:text-red-400 transition-colors"
          >
            <LogOut className="w-5 h-5 mr-3 shrink-0" />
            Sign out
          </button>
        </div>
      </div>

      {/* Main Content Area */}
      <div className="flex-1 flex flex-col min-w-0 overflow-hidden relative">
        <div className="absolute inset-0 bg-[radial-gradient(ellipse_at_top_right,_var(--tw-gradient-stops))] from-blue-900/10 via-slate-950/0 to-slate-950/0 pointer-events-none" />
        <main className="flex-1 overflow-y-auto p-8 relative z-10">
          {children}
        </main>
      </div>
    </div>
  );
};

export default Layout;

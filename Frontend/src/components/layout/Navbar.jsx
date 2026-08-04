import React from 'react';
import { useAuth } from '../../hooks/useAuth';
import { Search, Bell, Shield, LogOut, User as UserIcon } from 'lucide-react';
import { Badge } from '../common/Badge';

export const Navbar = () => {
  const { user, logout } = useAuth();

  return (
    <header className="h-16 border-b border-terminal-border/80 bg-terminal-dark/95 backdrop-blur-md sticky top-0 z-30 flex items-center justify-between px-6">
      {/* Left side: Search bar / terminal breadcrumb */}
      <div className="flex items-center gap-4 w-96">
        <div className="relative w-full">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-slate-500" />
          <input
            type="text"
            placeholder="Search filings, metrics, tickers (e.g. INF, AAPL)..."
            className="w-full bg-terminal-card border border-terminal-border text-slate-200 text-xs rounded-lg pl-9 pr-4 py-2 focus:outline-none focus:border-emerald-500 transition-colors placeholder:text-slate-600 font-mono"
          />
        </div>
      </div>

      {/* Center: Live Multi-Agent Status */}
      <div className="hidden lg:flex items-center gap-2 px-3 py-1 bg-terminal-card/60 border border-emerald-500/20 rounded-full">
        <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse"></span>
        <span className="text-[11px] font-mono font-medium text-emerald-400 uppercase tracking-wider">
          Multi-Agent Pipeline: Grounded in Source Docs
        </span>
      </div>

      {/* Right side: User Profile & Actions */}
      <div className="flex items-center gap-4">
        <div className="flex items-center gap-1.5 px-2.5 py-1 rounded-lg bg-terminal-card border border-terminal-border text-slate-400 text-xs">
          <Shield className="w-3.5 h-3.5 text-cyan-400" />
          <span>Infosys Internship Project</span>
        </div>

        <button 
          type="button" 
          className="relative p-2 text-slate-400 hover:text-slate-200 hover:bg-terminal-card rounded-lg transition-colors"
          title="Notifications"
        >
          <Bell className="w-4 h-4" />
          <span className="absolute top-1.5 right-1.5 w-2 h-2 bg-emerald-500 rounded-full"></span>
        </button>

        <div className="h-6 w-px bg-terminal-border/80"></div>

        {user ? (
          <div className="flex items-center gap-3">
            <div className="flex items-center gap-2">
              <div className="w-8 h-8 rounded-full bg-gradient-to-br from-emerald-500 to-teal-700 flex items-center justify-center text-slate-950 font-bold text-xs">
                {user.full_name ? user.full_name.charAt(0).toUpperCase() : 'U'}
              </div>
              <div className="text-left hidden sm:block">
                <p className="text-xs font-semibold text-slate-200 leading-none">{user.full_name}</p>
                <p className="text-[10px] text-slate-500 mt-0.5">{user.role || 'Analyst'}</p>
              </div>
            </div>

            <button
              onClick={logout}
              className="p-2 text-slate-400 hover:text-rose-400 hover:bg-rose-500/10 rounded-lg transition-colors"
              title="Logout"
            >
              <LogOut className="w-4 h-4" />
            </button>
          </div>
        ) : (
          <Badge variant="default">Guest Session</Badge>
        )}
      </div>
    </header>
  );
};

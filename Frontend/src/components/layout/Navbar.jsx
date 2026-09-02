import React from 'react';
import { useAuth } from '../../hooks/useAuth';
import { Search, Bell, Shield, LogOut, Menu } from 'lucide-react';
import { Badge } from '../common/Badge';
import { ThemeToggle } from '../common/ThemeToggle';

export const Navbar = ({ onMenuClick = () => {} }) => {
  const { user, logout } = useAuth();

  return (
    <header className="sticky top-0 z-30 h-16 px-4 sm:px-6 flex items-center justify-between gap-4 border-b border-white/[0.07] bg-[#070B16]/70 backdrop-blur-2xl">
      {/* Left: mobile menu + search */}
      <div className="flex items-center gap-3 flex-1 min-w-0">
        <button
          onClick={onMenuClick}
          className="lg:hidden p-2 rounded-lg text-slate-300 hover:text-white hover:bg-white/[0.07] transition-colors"
          aria-label="Open navigation"
        >
          <Menu className="w-5 h-5" />
        </button>

        <div className="relative w-full max-w-sm hidden sm:block group">
          <Search className="absolute left-3.5 top-1/2 -translate-y-1/2 h-4 w-4 text-slate-500 transition-colors group-focus-within:text-brand-300" />

          <input
            type="text"
            placeholder="Search filings, metrics, tickers…"
            className="field h-10 pl-10 pr-4 text-xs"
          />
        </div>
      </div>

      {/* Center: pipeline status */}
      <div className="hidden xl:flex items-center gap-2 px-3 py-1.5 rounded-full bg-white/[0.05] border border-white/10 backdrop-blur-md">
        <span className="w-1.5 h-1.5 rounded-full bg-brand-400 animate-pulse" />

        <span className="text-[11px] font-medium text-slate-300 tracking-wide">
          Multi-Agent Pipeline · Grounded in source docs
        </span>
      </div>

      {/* Right: actions & user */}
      <div className="flex items-center gap-2 sm:gap-3">
        {/* Project badge */}
        <div className="hidden md:flex items-center gap-1.5 px-2.5 py-1.5 rounded-lg bg-white/[0.04] border border-white/10 text-slate-400 text-[11px]">
          <Shield className="w-3.5 h-3.5 text-accent-300" />
          <span>Infosys Internship Project</span>
        </div>

        {/* Theme toggle */}
        <ThemeToggle />

        {/* Notifications */}
        <button
          type="button"
          className="relative p-2 rounded-lg text-slate-400 hover:text-white hover:bg-white/[0.07] transition-colors"
          title="Notifications"
          aria-label="Notifications"
        >
          <Bell className="w-[18px] h-[18px]" />

          <span className="absolute top-1.5 right-1.5 w-1.5 h-1.5 bg-brand-400 rounded-full shadow-[0_0_8px_2px_rgba(129,140,248,0.6)]" />
        </button>

        <div className="hidden sm:block h-6 w-px bg-white/10" />

        {/* User */}
        {user ? (
          <div className="flex items-center gap-2 sm:gap-3">
            <div className="flex items-center gap-2.5">
              <div className="w-9 h-9 rounded-full bg-gradient-to-br from-brand-500 to-accent-600 flex items-center justify-center text-white font-bold text-xs ring-1 ring-white/15">
                {user.full_name
                  ? user.full_name.charAt(0).toUpperCase()
                  : 'U'}
              </div>

              <div className="text-left hidden md:block">
                <p className="text-xs font-semibold text-slate-100 leading-none">
                  {user.full_name}
                </p>

                <p className="text-[10px] text-slate-500 mt-1">
                  {user.role || 'Analyst'}
                </p>
              </div>
            </div>

            {/* Logout */}
            <button
              onClick={logout}
              className="p-2 rounded-lg text-slate-400 hover:text-rose-300 hover:bg-rose-500/10 transition-colors"
              title="Logout"
              aria-label="Logout"
            >
              <LogOut className="w-[18px] h-[18px]" />
            </button>
          </div>
        ) : (
          <Badge variant="default">Guest Session</Badge>
        )}
      </div>
    </header>
  );
};
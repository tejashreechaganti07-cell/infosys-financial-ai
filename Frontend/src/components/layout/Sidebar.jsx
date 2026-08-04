import React from 'react';
import { NavLink, useLocation } from 'react-router-dom';
import { 
  LayoutDashboard, 
  Layers, 
  FileText, 
  User, 
  TrendingUp, 
  Cpu, 
  Database,
  ExternalLink 
} from 'lucide-react';

export const Sidebar = () => {
  const location = useLocation();

  const navItems = [
    { name: 'Dashboard', path: '/dashboard', icon: LayoutDashboard },
    { name: 'Research Workspace', path: '/workspace', icon: Layers, highlight: true },
    { name: 'Analyst Reports', path: '/reports', icon: FileText },
    { name: 'Profile & API', path: '/profile', icon: User },
  ];

  return (
    <aside className="w-64 border-r border-terminal-border bg-terminal-dark/95 flex flex-col justify-between h-screen sticky top-0">
      {/* Top Brand Logo */}
      <div>
        <div className="h-16 flex items-center gap-3 px-6 border-b border-terminal-border/80">
          <div className="w-8 h-8 rounded-lg bg-emerald-500/10 border border-emerald-500/30 flex items-center justify-center text-emerald-400 shadow-glow-emerald">
            <TrendingUp className="w-5 h-5" />
          </div>
          <div>
            <h1 className="font-bold text-sm text-slate-100 tracking-wider">INFOSYS AI</h1>
            <p className="text-[10px] font-mono text-emerald-400 uppercase tracking-widest">Financial AI</p>
          </div>
        </div>

        {/* Navigation links */}
        <nav className="p-4 space-y-1.5">
          <p className="text-[11px] font-semibold text-slate-500 uppercase tracking-wider px-3 mb-2">
            Multi-Agent System
          </p>
          {navItems.map((item) => {
            const Icon = item.icon;
            const isActive = location.pathname.startsWith(item.path);

            return (
              <NavLink
                key={item.path}
                to={item.path}
                className={`flex items-center justify-between px-3.5 py-2.5 rounded-lg text-sm font-medium transition-all duration-200 ${
                  isActive
                    ? 'bg-emerald-500/15 text-emerald-400 border border-emerald-500/30 shadow-glow-emerald'
                    : 'text-slate-400 hover:text-slate-200 hover:bg-terminal-card'
                }`}
              >
                <div className="flex items-center gap-3">
                  <Icon className={`w-4 h-4 ${isActive ? 'text-emerald-400' : 'text-slate-500'}`} />
                  <span>{item.name}</span>
                </div>
                {item.highlight && (
                  <span className="text-[10px] font-mono font-semibold bg-emerald-500/20 text-emerald-400 px-1.5 py-0.5 rounded">
                    ⭐ CORE
                  </span>
                )}
              </NavLink>
            );
          })}
        </nav>
      </div>

      {/* Bottom status widget */}
      <div className="p-4 border-t border-terminal-border/80">
        <div className="bg-terminal-card/80 border border-terminal-border rounded-xl p-3.5 space-y-2">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <Cpu className="w-4 h-4 text-cyan-400" />
              <span className="text-xs font-semibold text-slate-300">Agents Engine</span>
            </div>
            <span className="text-[10px] font-mono bg-cyan-500/20 text-cyan-400 px-1.5 py-0.5 rounded font-medium">
              ACTIVE
            </span>
          </div>
          <p className="text-[11px] text-slate-400 leading-relaxed">
            Document, Extraction, Red Flag & Comparison Agents coordinated.
          </p>
          <div className="flex items-center justify-between text-[10px] font-mono text-slate-500 pt-1 border-t border-terminal-border/50">
            <span>DB: MONGODB</span>
            <span className="text-emerald-400">0 HALLUCINATION</span>
          </div>
        </div>
      </div>
    </aside>
  );
};

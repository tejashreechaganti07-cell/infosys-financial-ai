import React from 'react';
import { useAuth } from '../hooks/useAuth';
import { Card } from '../components/common/Card';
import { Badge } from '../components/common/Badge';
import { Button } from '../components/common/Button';
import { User, Shield, Key, Cpu, ExternalLink, RefreshCw, Database } from 'lucide-react';

export const Profile = () => {
  const { user, logout } = useAuth();

  const handleResetDemo = () => {
    if (window.confirm("Reset active session and reload demo credentials?")) {
      localStorage.clear();
      window.location.href = '/login';
    }
  };

  return (
    <div className="space-y-6 max-w-4xl mx-auto animate-fadeIn">
      {/* Top Banner */}
      <div className="pb-4 border-b border-white/[0.07]">
        <h2 className="text-xl font-bold text-slate-100 tracking-tight flex items-center gap-2">
          <span>Analyst Profile & System Configuration</span>
          <Badge variant="emerald">ACTIVE USER SESSION</Badge>
        </h2>
        <p className="text-xs text-slate-400 mt-1">
          Infosys Internship • Multi-Agent Financial Research Platform (FastAPI + React + MongoDB)
        </p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* User Card */}
        <Card title="User Account Details" subtitle="Authentication & Role Permissions">
          <div className="space-y-4 text-xs">
            <div className="flex items-center gap-3 p-3 rounded-xl glass-inset">
              <div className="w-12 h-12 rounded-full bg-gradient-to-br from-emerald-500 to-teal-700 flex items-center justify-center text-white font-bold text-base">
                {user?.full_name ? user.full_name.charAt(0).toUpperCase() : 'A'}
              </div>
              <div>
                <h4 className="font-bold text-slate-100 text-sm">{user?.full_name || 'Tejashree Chaganti'}</h4>
                <p className="text-slate-400">{user?.email || 'demo@infosys.com'}</p>
                <div className="mt-1 flex items-center gap-1.5">
                  <Badge variant="emerald">{user?.role || 'Senior Financial Analyst'}</Badge>
                </div>
              </div>
            </div>

            <div className="space-y-2 pt-2">
              <div className="flex items-center justify-between text-slate-400">
                <span>Organization:</span>
                <span className="font-semibold text-slate-200">Infosys Limited</span>
              </div>
              <div className="flex items-center justify-between text-slate-400">
                <span>Access Scope:</span>
                <span className="font-mono text-emerald-400">FULL WORKSPACE + REPORTS</span>
              </div>
              <div className="flex items-center justify-between text-slate-400">
                <span>Session Expiration:</span>
                <span className="font-mono text-slate-300">24 HOURS (JWT)</span>
              </div>
            </div>

            <div className="pt-4 border-t border-white/10 flex justify-end">
              <Button variant="danger" size="sm" onClick={logout}>
                Sign Out of Terminal
              </Button>
            </div>
          </div>
        </Card>
      </div>
    </div>
  );
};

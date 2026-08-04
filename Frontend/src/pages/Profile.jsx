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
      <div className="pb-4 border-b border-terminal-border/80">
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
            <div className="flex items-center gap-3 p-3 rounded-xl bg-terminal-dark/80 border border-terminal-border">
              <div className="w-12 h-12 rounded-full bg-gradient-to-br from-emerald-500 to-teal-700 flex items-center justify-center text-slate-950 font-bold text-base">
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

            <div className="pt-4 border-t border-terminal-border flex justify-end">
              <Button variant="danger" size="sm" onClick={logout}>
                Sign Out of Terminal
              </Button>
            </div>
          </div>
        </Card>

        {/* Project & API Card */}
        <Card title="Project & API Reference" subtitle="FastAPI REST API & Motor Driver">
          <div className="space-y-4 text-xs">
            <div className="p-3.5 rounded-xl bg-emerald-500/5 border border-emerald-500/20 space-y-2">
              <div className="flex items-center justify-between">
                <span className="font-bold text-emerald-400">FastAPI Swagger UI</span>
                <Badge variant="emerald">READY</Badge>
              </div>
              <p className="text-slate-300 leading-relaxed">
                Live interactive Swagger API documentation is running on port 8000.
              </p>
              <a
                href="http://localhost:8000/docs"
                target="_blank"
                rel="noopener noreferrer"
                className="inline-flex items-center gap-1.5 text-emerald-400 hover:text-emerald-300 font-semibold pt-1"
              >
                <span>Open http://localhost:8000/docs</span>
                <ExternalLink className="w-3.5 h-3.5" />
              </a>
            </div>

            <div className="space-y-2 text-slate-400">
              <div className="flex items-center justify-between">
                <span>Backend Framework:</span>
                <span className="font-mono text-slate-200">FastAPI (Python 3.12)</span>
              </div>
              <div className="flex items-center justify-between">
                <span>Database Engine:</span>
                <span className="font-mono text-emerald-400">MongoDB / Motor Async</span>
              </div>
              <div className="flex items-center justify-between">
                <span>Frontend Build:</span>
                <span className="font-mono text-slate-200">React + Vite + Tailwind CSS</span>
              </div>
              <div className="flex items-center justify-between">
                <span>Hallucination Prevention:</span>
                <span className="font-mono text-cyan-400">STRICT SOURCE CITATIONS</span>
              </div>
            </div>

            <div className="pt-4 border-t border-terminal-border flex justify-end">
              <Button variant="secondary" size="sm" onClick={handleResetDemo}>
                <RefreshCw className="w-4 h-4 mr-1.5" />
                Reset Demo Session
              </Button>
            </div>
          </div>
        </Card>
      </div>
    </div>
  );
};

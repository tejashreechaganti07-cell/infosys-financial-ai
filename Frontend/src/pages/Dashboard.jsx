import React, { useEffect, useState } from 'react';
import { dashboardService } from '../services/dashboardService';
import { StatsCards } from '../components/dashboard/StatsCards';
import { RecentDocuments } from '../components/dashboard/RecentDocuments';
import { RecentWorkspaces } from '../components/dashboard/RecentWorkspaces';
import { RecentReports } from '../components/dashboard/RecentReports';
import { Loader } from '../components/common/Loader';
import { Sparkles, RefreshCw, Layers } from 'lucide-react';
import { Link } from 'react-router-dom';

export const Dashboard = () => {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const fetchDashboard = async () => {
    setLoading(true);
    setError(null);
    try {
      const summary = await dashboardService.getSummary();
      setData(summary);
    } catch (err) {
      setError('Failed to load terminal dashboard summary.');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchDashboard();
  }, []);

  if (loading && !data) {
    return <Loader text="Loading Analyst Terminal Dashboard..." />;
  }

  return (
    <div className="space-y-6 animate-fadeIn">
      {/* Top Banner */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 pb-4 border-b border-terminal-border/80">
        <div>
          <div className="flex items-center gap-2">
            <h2 className="text-xl font-bold text-slate-100 tracking-tight">
              Executive Research Overview
            </h2>
            <span className="px-2 py-0.5 rounded text-[10px] font-mono bg-emerald-500/15 text-emerald-400 border border-emerald-500/30">
              0 HALLUCINATION ENGINE
            </span>
          </div>
          <p className="text-xs text-slate-400 mt-1">
            Infosys Internship Multi-Agent Financial Research System • Real Company Filings & Ratios
          </p>
        </div>

        <div className="flex items-center gap-3">
          <button
            onClick={fetchDashboard}
            className="p-2 bg-terminal-card hover:bg-terminal-hover text-slate-300 hover:text-white rounded-lg border border-terminal-border transition-colors flex items-center gap-1.5 text-xs"
            title="Refresh Data"
          >
            <RefreshCw className={`w-3.5 h-3.5 ${loading ? 'animate-spin' : ''}`} />
            <span>Refresh</span>
          </button>
          <Link
            to="/workspace"
            className="inline-flex items-center gap-2 px-4 py-2 bg-emerald-500 hover:bg-emerald-400 text-slate-950 font-semibold text-xs rounded-lg shadow-glow-emerald transition-all"
          >
            <Layers className="w-4 h-4" />
            <span>Launch Research Workspace ⭐</span>
          </Link>
        </div>
      </div>

      {error && (
        <div className="bg-rose-500/15 border border-rose-500/40 text-rose-300 px-4 py-3 rounded-xl text-xs">
          {error}
        </div>
      )}

      {/* KPI Stats Cards */}
      {data?.stats && <StatsCards cards={data.stats} />}

      {/* Main Grid: Workspaces & Reports */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <RecentWorkspaces workspaces={data?.recent_workspaces || []} />
        <RecentReports reports={data?.recent_reports || []} />
      </div>

      {/* Bottom Table: Recent Indexed Documents */}
      <RecentDocuments documents={data?.recent_documents || []} />
    </div>
  );
};

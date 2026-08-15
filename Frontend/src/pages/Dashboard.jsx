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
    <div className="space-y-6">
      {/* Top Banner */}
      <div className="flex flex-col md:flex-row md:items-end justify-between gap-5">
        <div>
          <div className="flex flex-wrap items-center gap-2.5">
            <h1 className="text-2xl font-bold text-slate-50 tracking-tight">
              Executive research overview
            </h1>
            <span className="px-2.5 py-1 rounded-full text-[10px] font-semibold uppercase tracking-[0.08em] bg-brand-500/12 text-brand-200 border border-brand-400/25">
              0 hallucination engine
            </span>
          </div>
          <p className="text-sm text-slate-400 mt-2 max-w-2xl">
            Multi-agent financial research across real company filings, ratios and risk signals.
          </p>
        </div>

        <div className="flex items-center gap-2.5 shrink-0">
          <button
            onClick={fetchDashboard}
            className="inline-flex items-center gap-2 h-10 px-3.5 rounded-xl text-xs font-semibold text-slate-300 bg-white/[0.05] border border-white/10 backdrop-blur-md hover:text-white hover:bg-white/[0.09] transition-all duration-200 ease-premium"
            title="Refresh Data"
          >
            <RefreshCw className={`w-4 h-4 ${loading ? 'animate-spin' : ''}`} />
            <span>Refresh</span>
          </button>
          <Link
            to="/workspace"
            className="inline-flex items-center gap-2 h-10 px-4 rounded-xl text-xs font-semibold text-white bg-gradient-to-b from-brand-500 to-brand-600 border border-brand-400/40 shadow-[0_10px_30px_-12px_rgba(99,102,241,0.9),inset_0_1px_0_0_rgba(255,255,255,0.18)] hover:from-brand-400 hover:to-brand-500 transition-all duration-200 ease-premium active:translate-y-px"
          >
            <Layers className="w-4 h-4" />
            <span>Launch research workspace</span>
          </Link>
        </div>
      </div>

      {error && (
        <div className="glass rounded-2xl border-rose-500/30 bg-rose-500/[0.08] text-rose-200 px-4 py-3 text-xs">
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

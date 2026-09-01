import React, { useEffect, useState } from 'react';
import { dashboardService } from '../services/dashboardService';
import { StatsCards } from '../components/dashboard/StatsCards';
import { RecentDocuments } from '../components/dashboard/RecentDocuments';
import { RecentWorkspaces } from '../components/dashboard/RecentWorkspaces';
import { RecentReports } from '../components/dashboard/RecentReports';
import { SystemStatus } from '../components/dashboard/SystemStatus';
import { RiskSignals } from '../components/dashboard/RiskSignals';
import { Loader } from '../components/common/Loader';
import { RefreshCw, Layers, AlertTriangle, ShieldCheck } from 'lucide-react';
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

  const riskCard = (data?.stats || []).find((c) => c.icon === 'AlertTriangle');

  return (
    <div className="space-y-7">
      {/* Dashboard header */}
      <header className="relative overflow-hidden rounded-2xl glass px-5 py-5 sm:px-7 sm:py-6">
        <span className="pointer-events-none absolute inset-x-0 top-0 h-px bg-gradient-to-r from-transparent via-brand-400/45 to-transparent" />
        <div className="flex flex-col xl:flex-row xl:items-end justify-between gap-5">
          <div className="min-w-0">
            <p className="eyebrow mb-2.5">Infosys AI · Financial Intelligence</p>
            <h1 className="text-[26px] sm:text-[30px] leading-none font-bold text-slate-50 tracking-tight">
              Executive Research Overview
            </h1>
            <p className="text-sm text-slate-400 mt-3 max-w-2xl leading-relaxed">
              Multi-agent financial research across real company filings, ratios and risk signals.
            </p>
          </div>

          <div className="flex flex-wrap items-center gap-2.5 shrink-0">
            <span className="inline-flex items-center gap-1.5 h-10 px-3 rounded-xl text-[11px] font-semibold text-slate-300 bg-white/[0.04] border border-white/10">
              <ShieldCheck className="w-3.5 h-3.5 text-emerald-400" />
              <span className="uppercase tracking-[0.08em]">0 Hallucination Engine</span>
            </span>
            <button
              onClick={fetchDashboard}
              className="inline-flex items-center gap-2 h-10 px-3.5 rounded-xl text-xs font-semibold text-slate-300 bg-white/[0.04] border border-white/10 hover:text-white hover:bg-white/[0.08] transition-all duration-200 ease-premium"
              title="Refresh Data"
            >
              <RefreshCw className={`w-4 h-4 ${loading ? 'animate-spin' : ''}`} />
              <span>Refresh</span>
            </button>
            <Link
              to="/workspace"
              className="inline-flex items-center gap-2 h-10 px-4 rounded-xl text-xs font-semibold text-white bg-gradient-to-b from-brand-500 to-brand-600 border border-brand-400/40 shadow-[0_10px_30px_-14px_rgba(99,102,241,0.9),inset_0_1px_0_0_rgba(255,255,255,0.18)] hover:from-brand-400 hover:to-brand-500 transition-all duration-200 ease-premium active:translate-y-px"
            >
              <Layers className="w-4 h-4" />
              <span>Launch Research Workspace</span>
            </Link>
          </div>
        </div>
      </header>

      {error && (
        <div className="flex items-start gap-2.5 rounded-xl border border-rose-500/25 bg-rose-500/[0.06] text-rose-300 px-3.5 py-2.5 text-[11px] leading-relaxed">
          <AlertTriangle className="w-3.5 h-3.5 mt-px shrink-0" />
          <span>{error}</span>
        </div>
      )}

      {/* Section 1 — Financial intelligence overview */}
      {data?.stats?.length > 0 && (
        <section className="space-y-3.5">
          <div className="flex items-baseline justify-between gap-3">
            <h2 className="eyebrow">Financial Intelligence Overview</h2>
          </div>
          <StatsCards cards={data.stats} />
        </section>
      )}

      {/* Section 2 — Research activity */}
      <section className="grid grid-cols-1 lg:grid-cols-2 gap-5">
        <RecentWorkspaces workspaces={data?.recent_workspaces || []} />
        <RecentReports reports={data?.recent_reports || []} />
      </section>

      {/* Section 3 — Financial document intelligence */}
      <RecentDocuments documents={data?.recent_documents || []} />

      {/* Section 4 — AI system status & risk signals */}
      <section className="grid grid-cols-1 lg:grid-cols-3 gap-5">
        <div className="lg:col-span-2">
          <SystemStatus />
        </div>
        <RiskSignals card={riskCard} />
      </section>
    </div>
  );
};


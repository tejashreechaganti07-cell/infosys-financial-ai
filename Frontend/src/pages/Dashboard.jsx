import React, { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { RefreshCw, Layers } from "lucide-react";

import { dashboardService } from "../services/dashboardService";
import { StatsCards } from "../components/dashboard/StatsCards";
import { RecentDocuments } from "../components/dashboard/RecentDocuments";
import { RecentWorkspaces } from "../components/dashboard/RecentWorkspaces";
import { RecentReports } from "../components/dashboard/RecentReports";
import { Loader } from "../components/common/Loader";

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
      setError("Failed to load terminal dashboard summary.");
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
              Executive Research Overview
            </h1>

            <span className="px-2.5 py-1 rounded-full text-[10px] font-semibold uppercase tracking-wide bg-brand-500/10 text-brand-200 border border-brand-400/30">
              0 Hallucination Engine
            </span>
          </div>

          <p className="text-sm text-slate-400 mt-2">
            Multi-agent financial research across real company filings, ratios
            and risk signals.
          </p>
        </div>

        <div className="flex items-center gap-2.5">
          <button
            onClick={fetchDashboard}
            title="Refresh Data"
            className="inline-flex items-center gap-2 h-10 px-3.5 rounded-xl text-xs font-semibold text-slate-300 bg-white/5 border border-white/10 hover:bg-white/10 transition"
          >
            <RefreshCw
              className={`w-4 h-4 ${loading ? "animate-spin" : ""}`}
            />
            Refresh
          </button>

          <Link
            to="/workspace"
            className="inline-flex items-center gap-2 h-10 px-4 rounded-xl text-xs font-semibold text-white bg-gradient-to-b from-brand-500 to-brand-600 hover:from-brand-400 hover:to-brand-500 transition"
          >
            <Layers className="w-4 h-4" />
            Launch Research Workspace
          </Link>
        </div>
      </div>

      {/* Error */}
      {error && (
        <div className="rounded-xl border border-rose-500/30 bg-rose-500/10 text-rose-200 px-4 py-3 text-sm">
          {error}
        </div>
      )}

      {/* Stats */}
      {data?.stats && <StatsCards cards={data.stats} />}

      {/* Workspaces + Reports */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <RecentWorkspaces workspaces={data?.recent_workspaces || []} />
        <RecentReports reports={data?.recent_reports || []} />
      </div>

      {/* Documents */}
      <RecentDocuments documents={data?.recent_documents || []} />
    </div>
  );
};

export default Dashboard;
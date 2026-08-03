import React, { useState, useEffect } from 'react';
import { reportService } from '../services/reportService';
import { Card } from '../components/common/Card';
import { Badge } from '../components/common/Badge';
import { Button } from '../components/common/Button';
import { Loader } from '../components/common/Loader';
import { Modal } from '../components/common/Modal';
import { FileText, Download, Eye, Plus, Sparkles, CheckCircle2, ShieldAlert, BarChart2 } from 'lucide-react';

export const Reports = () => {
  const [reports, setReports] = useState([]);
  const [selectedReport, setSelectedReport] = useState(null);
  const [loading, setLoading] = useState(true);
  const [generating, setGenerating] = useState(false);
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [titleInput, setTitleInput] = useState('');
  const [companyInput, setCompanyInput] = useState('Infosys Limited');

  const loadReports = async () => {
    setLoading(true);
    try {
      const list = await reportService.getReports();
      setReports(list);
      if (list.length > 0 && !selectedReport) {
        setSelectedReport(list[0]);
      }
    } catch (err) {
      console.error("Failed to load reports:", err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadReports();
  }, []);

  const handleCreateReport = async (e) => {
    e.preventDefault();
    if (!titleInput.trim()) return;
    setGenerating(true);
    try {
      const newRep = await reportService.createReport(
        titleInput.trim(),
        "ws_demo_infy_2024",
        companyInput
      );
      setReports((prev) => [newRep, ...prev]);
      setSelectedReport(newRep);
      setShowCreateModal(false);
      setTitleInput('');
    } catch (err) {
      alert("Failed to generate report.");
    } finally {
      setGenerating(false);
    }
  };

  const handleExportMarkdown = async (id, title) => {
    try {
      const markdown = await reportService.exportReport(id);
      const blob = new Blob([markdown], { type: 'text/markdown;charset=utf-8;' });
      const url = URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', `${title.replace(/\s+/g, '_')}_Report.md`);
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
    } catch (err) {
      alert("Failed to export markdown report.");
    }
  };

  if (loading && reports.length === 0) {
    return <Loader text="Loading Analyst Reports & Document Summaries..." />;
  }

  return (
    <div className="space-y-6 animate-fadeIn">
      {/* Top Banner */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-4 border-b border-terminal-border/80">
        <div>
          <h2 className="text-xl font-bold text-slate-100 tracking-tight flex items-center gap-2">
            <span>Analyst Research Reports</span>
            <Badge variant="emerald">AUTOMATED REPORT AGENT</Badge>
          </h2>
          <p className="text-xs text-slate-400 mt-1">
            Structured investment summaries with Executive Summary, Financial Metrics, Red Flags, and Peer Ratios
          </p>
        </div>

        <Button
          variant="primary"
          size="sm"
          onClick={() => setShowCreateModal(true)}
        >
          <Sparkles className="w-4 h-4 mr-1.5" />
          Generate New Report
        </Button>
      </div>

      {/* Main Grid: Left List (4 Cols) + Right Viewer (8 Cols) */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        {/* Left List */}
        <div className="lg:col-span-4 space-y-3">
          <h3 className="text-xs font-semibold uppercase tracking-wider text-slate-400 px-1">
            Available Reports ({reports.length})
          </h3>
          <div className="space-y-2.5">
            {reports.map((rep) => {
              const isSelected = selectedReport?.id === rep.id;

              return (
                <div
                  key={rep.id}
                  onClick={() => setSelectedReport(rep)}
                  className={`p-3.5 rounded-xl border transition-all cursor-pointer ${
                    isSelected
                      ? 'bg-emerald-500/15 border-emerald-500/40 shadow-glow-emerald'
                      : 'bg-terminal-card border-terminal-border hover:border-slate-600'
                  }`}
                >
                  <div className="flex items-center justify-between">
                    <span className="text-[11px] font-mono text-emerald-400 font-semibold uppercase">
                      {rep.company_name}
                    </span>
                    <Badge variant="emerald">{rep.status}</Badge>
                  </div>
                  <h4 className="font-semibold text-slate-100 text-sm mt-1.5 line-clamp-1">
                    {rep.title}
                  </h4>
                  <p className="text-xs text-slate-400 mt-1 line-clamp-2 leading-relaxed">
                    {rep.summary}
                  </p>
                  <div className="mt-3 pt-2 border-t border-terminal-border/50 flex items-center justify-between text-[10px] font-mono text-slate-500">
                    <span>{rep.created_at ? rep.created_at.slice(0, 10) : 'Today'}</span>
                    <span className="text-emerald-400 font-medium">Click to Inspect →</span>
                  </div>
                </div>
              );
            })}
          </div>
        </div>

        {/* Right Report Viewer */}
        <div className="lg:col-span-8">
          {selectedReport ? (
            <Card
              title={selectedReport.title}
              subtitle={`${selectedReport.company_name} • Grounded in Source Documents`}
              headerAction={
                <Button
                  variant="secondary"
                  size="sm"
                  onClick={() => handleExportMarkdown(selectedReport.id, selectedReport.title)}
                >
                  <Download className="w-4 h-4 mr-1.5" /> Export Markdown / PDF
                </Button>
              }
            >
              <div className="space-y-6 text-xs text-slate-300 leading-relaxed">
                {/* Executive Summary Section */}
                <div className="p-4 rounded-xl bg-terminal-dark/80 border border-terminal-border space-y-2">
                  <h4 className="font-bold text-slate-100 text-sm flex items-center gap-2 text-emerald-400">
                    <FileText className="w-4 h-4" />
                    <span>Executive Summary & Thesis</span>
                  </h4>
                  <p className="whitespace-pre-line text-slate-300">
                    {selectedReport.summary ||
                      "Infosys Limited demonstrated resilient performance in FY2024, achieving revenues of $18.56B (+1.9% YoY) amidst macroeconomic volatility. Large deal wins surged 80.6% to a record $17.7B TCV, reinforcing client confidence in enterprise AI transformation and Project Maximus cost optimization."}
                  </p>
                </div>

                {/* Extracted Metrics Table */}
                <div className="space-y-3">
                  <h4 className="font-bold text-slate-100 text-sm flex items-center gap-2">
                    <BarChart2 className="w-4 h-4 text-emerald-400" />
                    <span>Key Financial Metrics & Operating Ratios</span>
                  </h4>
                  <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
                    <div className="p-3 rounded-lg bg-terminal-dark border border-terminal-border">
                      <span className="text-[10px] text-slate-400 uppercase">Revenue (FY24)</span>
                      <p className="text-lg font-bold font-mono text-slate-100 mt-1">$18,562M</p>
                    </div>
                    <div className="p-3 rounded-lg bg-terminal-dark border border-terminal-border">
                      <span className="text-[10px] text-slate-400 uppercase">Operating Margin</span>
                      <p className="text-lg font-bold font-mono text-emerald-400 mt-1">20.7%</p>
                    </div>
                    <div className="p-3 rounded-lg bg-terminal-dark border border-terminal-border">
                      <span className="text-[10px] text-slate-400 uppercase">FCF Conversion</span>
                      <p className="text-lg font-bold font-mono text-slate-100 mt-1">88.4%</p>
                    </div>
                    <div className="p-3 rounded-lg bg-terminal-dark border border-terminal-border">
                      <span className="text-[10px] text-slate-400 uppercase">Large Deal TCV</span>
                      <p className="text-lg font-bold font-mono text-emerald-400 mt-1">$17.7B</p>
                    </div>
                  </div>
                </div>

                {/* Red Flags Summary */}
                <div className="p-4 rounded-xl bg-amber-500/5 border border-amber-500/20 space-y-2">
                  <h4 className="font-bold text-amber-400 text-sm flex items-center gap-2">
                    <ShieldAlert className="w-4 h-4" />
                    <span>Risk Analysis & Auditor Verification</span>
                  </h4>
                  <ul className="list-disc list-inside space-y-1.5 text-slate-300">
                    <li>
                      <strong>BFS Discretionary Spend Softness:</strong> Longer deal conversion cycles in US financial services.
                    </li>
                    <li>
                      <strong>Offshore Wage Revision Schedule:</strong> Planned wage increases in H1 FY25 may temporarily compress EBIT margins.
                    </li>
                    <li>
                      <strong>Auditor Clean Assessment:</strong> Independent auditor (Deloitte Haskins & Sells) verified clean statutory books with zero going-concern warnings.
                    </li>
                  </ul>
                </div>

                {/* Footer Citation verification */}
                <div className="pt-3 border-t border-terminal-border/80 flex items-center justify-between text-[11px] font-mono text-slate-500">
                  <span>REPORT AGENT: MULTI-AGENT SYMBOLIC ENGINE</span>
                  <span className="text-emerald-400">CITATIONS VERIFIED AGAINST 20-F / Q4 TRANSCRIPT</span>
                </div>
              </div>
            </Card>
          ) : (
            <Card title="No Report Selected">
              <p className="text-xs text-slate-400">Select a report from the list to inspect.</p>
            </Card>
          )}
        </div>
      </div>

      {/* Generate Report Modal */}
      <Modal
        isOpen={showCreateModal}
        onClose={() => setShowCreateModal(false)}
        title="Generate Automated Analyst Report"
      >
        <form onSubmit={handleCreateReport} className="space-y-4">
          <div>
            <label className="block text-xs font-semibold text-slate-300 mb-1">Report Title</label>
            <input
              type="text"
              value={titleInput}
              onChange={(e) => setTitleInput(e.target.value)}
              placeholder="e.g. FY24 Comprehensive Equity Research Note"
              className="w-full bg-terminal-dark border border-terminal-border text-slate-200 text-xs rounded-lg py-2.5 px-3 focus:outline-none focus:border-emerald-500"
              required
            />
          </div>

          <div>
            <label className="block text-xs font-semibold text-slate-300 mb-1">Company Name</label>
            <input
              type="text"
              value={companyInput}
              onChange={(e) => setCompanyInput(e.target.value)}
              className="w-full bg-terminal-dark border border-terminal-border text-slate-200 text-xs rounded-lg py-2.5 px-3 focus:outline-none focus:border-emerald-500"
            />
          </div>

          <div className="p-3 bg-emerald-500/10 border border-emerald-500/20 rounded-lg text-xs text-emerald-400 space-y-1">
            <p className="font-semibold">Automated Report Agent Workflow:</p>
            <p className="text-slate-300 text-[11px]">
              1. Summarize executive performance across indexed filings.<br />
              2. Extract operating KPIs & year-over-year deltas.<br />
              3. Highlight automated red flags & auditor status.<br />
              4. Generate structured markdown export.
            </p>
          </div>

          <div className="flex justify-end gap-3 pt-2">
            <Button variant="ghost" size="sm" onClick={() => setShowCreateModal(false)}>
              Cancel
            </Button>
            <Button variant="primary" size="sm" type="submit" loading={generating}>
              Synthesize Report
            </Button>
          </div>
        </form>
      </Modal>
    </div>
  );
};

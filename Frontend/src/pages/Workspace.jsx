import React, { useState, useEffect } from 'react';

import { workspaceService } from '../services/workspaceService';
import { documentService } from '../services/documentService';

import { UploadPanel } from '../components/workspace/UploadPanel';
import { DocumentList } from '../components/workspace/DocumentList';
import { ChatWindow } from '../components/workspace/ChatWindow';
import { MetricsPanel } from '../components/workspace/MetricsPanel';
import { RedFlagsPanel } from '../components/workspace/RedFlagsPanel';
import { ComparisonPanel } from '../components/workspace/ComparisonPanel';

import { Loader } from '../components/common/Loader';
import { Button } from '../components/common/Button';

import {
  Layers,
  Plus,
  BarChart2,
  ShieldAlert,
  Scale,
  Sparkles
} from 'lucide-react';

export const Workspace = () => {
  const [workspaces, setWorkspaces] = useState([]);
  const [activeWorkspace, setActiveWorkspace] = useState(null);
  const [documents, setDocuments] = useState([]);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState('chat');
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [newWsName, setNewWsName] = useState('');

  const loadWorkspaces = async () => {
    setLoading(true);

    try {
      const list = await workspaceService.getWorkspaces();

      setWorkspaces(list);

      if (list.length > 0 && !activeWorkspace) {
        setActiveWorkspace(list[0]);
      }
    } catch (err) {
      console.error('Failed to load workspaces:', err);
    } finally {
      setLoading(false);
    }
  };

  const loadDocuments = async () => {
    if (!activeWorkspace) return;

    try {
      const docs = await documentService.getDocuments(activeWorkspace.id);
      setDocuments(docs);
    } catch (err) {
      console.error('Failed to load documents:', err);
    }
  };

  useEffect(() => {
    loadWorkspaces();
  }, []);

  useEffect(() => {
    if (activeWorkspace) {
      loadDocuments();
    }
  }, [activeWorkspace]);

  const handleCreateWorkspace = async (e) => {
    e.preventDefault();

    if (!newWsName.trim()) return;

    try {
      const ws = await workspaceService.createWorkspace(
        newWsName.trim(),
        'Created in Analyst Workspace'
      );

      setWorkspaces((prev) => [ws, ...prev]);
      setActiveWorkspace(ws);
      setNewWsName('');
      setShowCreateModal(false);
    } catch (err) {
      alert('Failed to create workspace.');
    }
  };

  if (loading && workspaces.length === 0) {
    return <Loader text="Loading Research Workspace & Seeded Filings..." />;
  }

  const tabs = [
    {
      id: 'chat',
      label: 'Conversational Research & Q&A',
      icon: Sparkles
    },
    {
      id: 'metrics',
      label: 'Extracted Metrics & Ratios',
      icon: BarChart2
    },
    {
      id: 'redflags',
      label: 'Automated Red Flag Scanner',
      icon: ShieldAlert
    },
    {
      id: 'comparison',
      label: 'Peer Comparison Matrix',
      icon: Scale
    }
  ];

  return (
    <div className="space-y-6 animate-fadeIn">

      {/* Workspace Selector Bar */}
      <div className="bg-terminal-card border border-terminal-border rounded-xl p-4 shadow-lg flex flex-col sm:flex-row sm:items-center justify-between gap-4">

        <div className="flex items-center gap-3">

          <div className="w-10 h-10 rounded-xl bg-emerald-500/10 border border-emerald-500/30 flex items-center justify-center text-emerald-400">
            <Layers className="w-5 h-5" />
          </div>

          <div>

            <div className="flex items-center gap-2">

              <span className="text-xs font-mono font-semibold text-slate-400 uppercase">
                ACTIVE WORKSPACE:
              </span>

              <select
                value={activeWorkspace?.id || ''}
                onChange={(e) => {
                  const ws = workspaces.find(
                    (w) => w.id === e.target.value
                  );

                  if (ws) {
                    setActiveWorkspace(ws);
                  }
                }}
                className="bg-terminal-dark border border-terminal-border text-slate-100 text-sm font-semibold rounded-lg px-3 py-1 focus:outline-none focus:border-emerald-500"
              >
                {workspaces.map((ws) => (
                  <option key={ws.id} value={ws.id}>
                    {ws.name} ({ws.documents_count} docs)
                  </option>
                ))}
              </select>

            </div>

            <p className="text-xs text-slate-400 mt-0.5">
              {activeWorkspace?.description ||
                'Multi-agent deep dive analysis on company filings.'}
            </p>

          </div>

        </div>

        <div className="flex items-center gap-3">

          <Button
            variant="secondary"
            size="sm"
            onClick={() => setShowCreateModal(true)}
          >
            <Plus className="w-4 h-4 mr-1" />
            New Workspace
          </Button>

        </div>

      </div>

      {/* Tabs Bar */}
      <div className="flex items-center gap-2 border-b border-terminal-border/80 pb-2 overflow-x-auto">

        {tabs.map((tab) => {
          const Icon = tab.icon;
          const isActive = activeTab === tab.id;

          return (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              className={`flex items-center gap-2 px-4 py-2.5 rounded-lg text-xs font-semibold transition-all shrink-0 ${
                isActive
                  ? 'bg-emerald-500/20 text-emerald-400 border border-emerald-500/30 shadow-glow-emerald'
                  : 'text-slate-400 hover:text-slate-200 hover:bg-terminal-card'
              }`}
            >
              <Icon className="w-4 h-4" />
              <span>{tab.label}</span>
            </button>
          );
        })}

      </div>

      {/* Main Workspace Layout */}

      {activeTab === 'chat' && (
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">

          {/* Left Column: Chat Q&A */}
          <div className="lg:col-span-8">
            <ChatWindow workspaceId={activeWorkspace?.id} />
          </div>

          {/* Right Column: Document Ingestion & List */}
          <div className="lg:col-span-4 space-y-6">

            <UploadPanel
              workspaceId={activeWorkspace?.id}
              onUploadSuccess={loadDocuments}
            />

            <DocumentList
              documents={documents}
              onDeleteSuccess={loadDocuments}
            />

          </div>

        </div>
      )}

      {activeTab === 'metrics' && (
        <div className="space-y-6">

          <MetricsPanel />

          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <RedFlagsPanel />
            <ComparisonPanel />
          </div>

        </div>
      )}

      {activeTab === 'redflags' && (
        <div className="space-y-6">
          <RedFlagsPanel />
          <MetricsPanel />
        </div>
      )}

      {activeTab === 'comparison' && (
        <div className="space-y-6">
          <ComparisonPanel />
          <MetricsPanel />
        </div>
      )}

      {/* Create Workspace Modal */}
      {showCreateModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/75 backdrop-blur-sm">

          <div className="bg-terminal-card border border-terminal-border rounded-xl p-6 w-full max-w-md shadow-2xl space-y-4">

            <h3 className="text-base font-bold text-slate-100">
              Create Research Workspace
            </h3>

            <div>

              <label className="block text-xs font-semibold text-slate-400 mb-1">
                Workspace Name
              </label>

              <input
                type="text"
                value={newWsName}
                onChange={(e) => setNewWsName(e.target.value)}
                placeholder="e.g. FY24 Q4 Competitor Analysis"
                className="w-full bg-terminal-dark border border-terminal-border text-slate-200 text-xs rounded-lg py-2.5 px-3 focus:outline-none focus:border-emerald-500"
              />

            </div>

            <div className="flex items-center justify-end gap-3 pt-2">

              <Button
                variant="ghost"
                size="sm"
                onClick={() => setShowCreateModal(false)}
              >
                Cancel
              </Button>

              <Button
                variant="primary"
                size="sm"
                onClick={handleCreateWorkspace}
              >
                Create Workspace
              </Button>

            </div>

          </div>

        </div>
      )}

    </div>
  );
};
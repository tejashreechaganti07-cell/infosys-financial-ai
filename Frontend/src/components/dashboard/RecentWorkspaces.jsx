import React from 'react';
import { Card } from '../common/Card';
import { Badge } from '../common/Badge';
import { Layers, FileText, ArrowRight } from 'lucide-react';
import { Link } from 'react-router-dom';

export const RecentWorkspaces = ({ workspaces = [] }) => {
  return (
    <Card
      title="Recent Research Sessions"
      subtitle="Active multi-agent workspaces"
      headerAction={
        <Link to="/workspace" className="text-xs font-semibold text-emerald-400 hover:text-emerald-300">
          All Workspaces →
        </Link>
      }
    >
      {workspaces.length === 0 ? (
        <div className="py-8 text-center text-slate-500 text-xs">
          No active workspaces.
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
          {workspaces.map((ws) => (
            <Link
              key={ws.id}
              to="/workspace"
              className="p-4 rounded-xl bg-terminal-dark/60 border border-terminal-border/80 hover:border-emerald-500/40 hover:bg-terminal-hover/60 transition-all group flex flex-col justify-between"
            >
              <div>
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    <Layers className="w-4 h-4 text-emerald-400" />
                    <h4 className="font-semibold text-slate-200 text-sm group-hover:text-emerald-400 transition-colors">
                      {ws.name}
                    </h4>
                  </div>
                  <Badge variant="cyan">{ws.documents_count} Docs</Badge>
                </div>
                <p className="text-xs text-slate-400 mt-2 line-clamp-2 leading-relaxed">
                  {ws.description || "Multi-agent deep dive financial assessment."}
                </p>
              </div>
              <div className="mt-3 pt-3 border-t border-terminal-border/50 flex items-center justify-between text-[11px] font-mono text-slate-500">
                <span>Updated: {ws.updated_at ? ws.updated_at.slice(0, 10) : 'Recent'}</span>
                <span className="text-emerald-400 group-hover:translate-x-1 transition-transform flex items-center gap-1">
                  Launch <ArrowRight className="w-3 h-3" />
                </span>
              </div>
            </Link>
          ))}
        </div>
      )}
    </Card>
  );
};

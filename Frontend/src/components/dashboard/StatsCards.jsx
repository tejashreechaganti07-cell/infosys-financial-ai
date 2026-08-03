import React from 'react';
import { Card } from '../common/Card';
import { FolderTree, FileText, AlertTriangle, FileCheck, ArrowUpRight, ArrowDownRight } from 'lucide-react';

export const StatsCards = ({ cards = [] }) => {
  const iconMap = {
    FolderTree,
    FileText,
    AlertTriangle,
    FileCheck,
  };

  return (
    <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
      {cards.map((card, idx) => {
        const IconComponent = iconMap[card.icon] || FileText;
        const isUp = card.trend === 'up';

        return (
          <Card key={idx} className="relative overflow-hidden group hover:border-emerald-500/40 transition-all">
            <div className="flex items-center justify-between">
              <span className="text-xs font-semibold uppercase tracking-wider text-slate-400">
                {card.title}
              </span>
              <div className="w-9 h-9 rounded-lg bg-emerald-500/10 border border-emerald-500/20 flex items-center justify-center text-emerald-400 group-hover:scale-110 transition-transform">
                <IconComponent className="w-5 h-5" />
              </div>
            </div>
            <div className="mt-4 flex items-baseline justify-between">
              <span className="text-3xl font-bold font-mono text-slate-100 tracking-tight">
                {card.value}
              </span>
              <div className={`flex items-center gap-0.5 text-xs font-semibold ${isUp ? 'text-emerald-400' : 'text-rose-400'}`}>
                {isUp ? <ArrowUpRight className="w-3.5 h-3.5" /> : <ArrowDownRight className="w-3.5 h-3.5" />}
                <span>{card.change}</span>
              </div>
            </div>
          </Card>
        );
      })}
    </div>
  );
};

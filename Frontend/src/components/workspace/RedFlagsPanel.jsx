import React from 'react';
import {
  FolderTree,
  FileText,
  AlertTriangle,
  FileCheck,
  ArrowUpRight,
  ArrowDownRight,
} from 'lucide-react';

export const StatsCards = ({ cards = [] }) => {
  const iconMap = {
    FolderTree,
    FileText,
    AlertTriangle,
    FileCheck,
  };

  return (
    <div className="grid grid-cols-1 sm:grid-cols-2 xl:grid-cols-4 gap-4 stagger">
      {cards.map((card, idx) => {
        const IconComponent = iconMap[card.icon] || FileText;
        const isUp = card.trend === 'up';

        return (
          <div
            key={idx}
            className="group relative overflow-hidden glass rounded-2xl p-5 transition-all duration-300 ease-premium hover:-translate-y-1 hover:border-brand-300/30 hover:shadow-lift"
          >
            {/* Accent wash on hover */}
            <div className="pointer-events-none absolute -top-16 -right-10 h-36 w-36 rounded-full bg-brand-500/0 blur-3xl transition-all duration-500 group-hover:bg-brand-500/25" />

            <div className="relative flex items-start justify-between gap-3">
              <span className="eyebrow leading-4">{card.title}</span>

              <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-brand-500/20 to-accent-500/10 border border-white/10 flex items-center justify-center text-brand-200 transition-transform duration-300 group-hover:scale-105">
                <IconComponent className="w-[18px] h-[18px]" />
              </div>
            </div>

            <div className="relative mt-5 flex items-end justify-between gap-3">
              <span className="text-[2rem] leading-none font-bold text-slate-50 tracking-tight tabular-nums">
                {card.value}
              </span>

              <div
                className={`flex items-center gap-1 rounded-full border px-2 py-1 text-[11px] font-semibold ${
                  isUp
                    ? 'text-brand-200 bg-brand-500/10 border-brand-400/25'
                    : 'text-rose-200 bg-rose-500/10 border-rose-400/25'
                }`}
              >
                {isUp ? (
                  <ArrowUpRight className="w-3.5 h-3.5" />
                ) : (
                  <ArrowDownRight className="w-3.5 h-3.5" />
                )}

                <span>{card.change}</span>
              </div>
            </div>
          </div>
        );
      })}
    </div>
  );
};
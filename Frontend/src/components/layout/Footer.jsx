import React from 'react';

export const Footer = () => {
  return (
    <footer className="h-10 border-t border-terminal-border bg-terminal-dark/95 flex items-center justify-between px-6 text-xs text-slate-500 font-mono">
      <div>
        <span>INFOSYS // MULTI-AGENT FINANCIAL RESEARCH SYSTEM (PHASE 1)</span>
      </div>
      <div className="flex items-center gap-4">
        <span>STRICT SOURCE GROUNDING: ENABLED</span>
        <span>LATENCY: 18ms</span>
      </div>
    </footer>
  );
};

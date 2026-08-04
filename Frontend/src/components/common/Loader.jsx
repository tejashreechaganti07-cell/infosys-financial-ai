import React from 'react';

export const Loader = ({ size = 'md', text = 'Processing Multi-Agent Pipeline...' }) => {
  const sizes = {
    sm: 'w-6 h-6 border-2',
    md: 'w-10 h-10 border-2',
    lg: 'w-16 h-16 border-4',
  };

  return (
    <div className="flex flex-col items-center justify-center py-12 gap-3">
      <div className="relative">
        <div className={`${sizes[size]} rounded-full border-emerald-500/20 border-t-emerald-400 animate-spin`}></div>
        <div className="absolute inset-0 flex items-center justify-center">
          <div className="w-2 h-2 bg-emerald-400 rounded-full animate-ping"></div>
        </div>
      </div>
      {text && <p className="text-xs text-slate-400 font-medium tracking-wide animate-pulse">{text}</p>}
    </div>
  );
};

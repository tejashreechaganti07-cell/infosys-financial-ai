import React from 'react';
import { clsx } from 'clsx';
import { twMerge } from 'tailwind-merge';

export const Card = ({
  children,
  title,
  subtitle,
  headerAction,
  className = '',
  hover = false,
  ...props
}) => {
  const baseClasses = 'bg-[#111827]/90 backdrop-blur-md border border-[#1F2937] rounded-xl shadow-lg p-5 transition-all duration-200';
  const hoverClasses = hover ? 'hover:border-emerald-500/40 hover:shadow-glow-emerald cursor-pointer' : '';
  
  return (
    <div className={twMerge(clsx(baseClasses, hoverClasses, className))} {...props}>
      {(title || headerAction) && (
        <div className="flex items-center justify-between pb-4 mb-4 border-b border-terminal-border/80">
          <div>
            {title && <h3 className="font-semibold text-slate-100 text-base tracking-tight">{title}</h3>}
            {subtitle && <p className="text-xs text-slate-400 mt-0.5">{subtitle}</p>}
          </div>
          {headerAction && <div>{headerAction}</div>}
        </div>
      )}
      <div>{children}</div>
    </div>
  );
};

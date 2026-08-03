import React from 'react';
import { clsx } from 'clsx';
import { twMerge } from 'tailwind-merge';

export const Button = ({
  children,
  variant = 'primary',
  size = 'md',
  className = '',
  disabled = false,
  loading = false,
  type = 'button',
  onClick,
  ...props
}) => {
  const baseStyles = 'inline-flex items-center justify-center font-medium transition-all duration-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-offset-terminal-dark disabled:opacity-50 disabled:cursor-not-allowed';

  const variants = {
    primary: 'bg-emerald-500 hover:bg-emerald-400 text-slate-950 font-semibold shadow-glow-emerald hover:shadow-emerald-500/40 focus:ring-emerald-400',
    secondary: 'bg-terminal-card hover:bg-terminal-hover text-slate-200 border border-terminal-border hover:border-slate-600 focus:ring-slate-500',
    ghost: 'bg-transparent hover:bg-terminal-hover text-slate-300 hover:text-white focus:ring-slate-500',
    danger: 'bg-rose-500/20 hover:bg-rose-500 text-rose-300 hover:text-white border border-rose-500/40 focus:ring-rose-400',
    cyan: 'bg-cyan-500 hover:bg-cyan-400 text-slate-950 font-semibold shadow-glow-cyan focus:ring-cyan-400',
  };

  const sizes = {
    sm: 'px-3 py-1.5 text-xs gap-1.5',
    md: 'px-4 py-2 text-sm gap-2',
    lg: 'px-6 py-3 text-base gap-2.5',
  };

  const mergedClasses = twMerge(clsx(baseStyles, variants[variant], sizes[size], className));

  return (
    <button
      type={type}
      className={mergedClasses}
      disabled={disabled || loading}
      onClick={onClick}
      {...props}
    >
      {loading && (
        <svg className="animate-spin -ml-1 mr-2 h-4 w-4 text-current" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
          <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
          <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v8H4z"></path>
        </svg>
      )}
      {children}
    </button>
  );
};

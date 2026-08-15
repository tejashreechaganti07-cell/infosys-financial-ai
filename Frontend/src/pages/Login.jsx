import { ThemeToggle } from '../components/common/ThemeToggle';
import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../hooks/useAuth';
import { Button } from '../components/common/Button';
import { Input } from '../components/common/Input';
import { Mail, Lock, TrendingUp, Sparkles, ShieldCheck, Layers, FileCheck } from 'lucide-react';

export const Login = () => {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const { login, previewLogin } = useAuth();
  const navigate = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setLoading(true);
    try {
      await login(email, password);
      navigate('/dashboard');
    } catch (err) {
      setError(err.response?.data?.detail || 'Invalid email or password. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const handleDemoLogin = async () => {
    setEmail('demo@infosys.com');
    setPassword('password123');
    setError('');
    setLoading(true);
    try {
      await login('demo@infosys.com', 'password123');
      navigate('/dashboard');
    } catch (err) {
      // Backend unavailable -> browse the UI in preview mode
      previewLogin();
      navigate('/dashboard');
    } finally {
      setLoading(false);
    }
  };

  const highlights = [
    { icon: Layers, title: 'Multi-agent research workspaces', desc: 'Ingest filings and interrogate them conversationally.' },
    { icon: ShieldCheck, title: 'Strict source grounding', desc: 'Every answer carries an exact filing citation.' },
    { icon: FileCheck, title: 'Automated analyst reports', desc: 'Executive summaries, metrics and red flags in one export.' },
  ];

  return (
    <div className="relative min-h-screen grid lg:grid-cols-[1.05fr_1fr] overflow-hidden">
      <div className="absolute top-5 right-5 z-50">
        <ThemeToggle />
      </div>
      {/* Ambient background */}
      <div className="pointer-events-none absolute inset-0 -z-10">
        <div className="absolute inset-0 bg-grid opacity-30" />
        <div className="orb -top-32 left-[8%] h-[460px] w-[460px] bg-brand-600/25 animate-float" />
        <div className="orb bottom-[-10%] right-[6%] h-[420px] w-[420px] bg-accent-600/20" />
      </div>

      {/* Brand / value panel */}
      <div className="hidden lg:flex flex-col justify-between p-12 xl:p-16 border-r border-white/[0.06]">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-brand-500 to-accent-600 flex items-center justify-center text-white shadow-[0_12px_30px_-14px_rgba(99,102,241,0.9)]">
            <TrendingUp className="w-5 h-5" />
          </div>
          <div>
            <p className="text-sm font-bold text-slate-50 leading-none">Infosys AI</p>
            <p className="text-[10px] uppercase tracking-[0.18em] text-slate-500 mt-1">
              Financial Intelligence
            </p>
          </div>
        </div>

        <div className="max-w-lg animate-fadeUp">
          <h1 className="text-4xl xl:text-[2.75rem] font-extrabold leading-[1.1] text-slate-50">
            The research terminal for{' '}
            <span className="text-gradient-emerald">grounded financial analysis</span>
          </h1>
          <p className="mt-4 text-sm text-slate-400 leading-relaxed">
            A multi-agent system that reads company filings, extracts the numbers that matter, flags
            risk, and cites every claim back to the source document.
          </p>

          <div className="mt-10 space-y-3 stagger">
            {highlights.map(({ icon: Icon, title, desc }) => (
              <div key={title} className="glass rounded-2xl p-4 flex items-start gap-3.5">
                <div className="w-9 h-9 rounded-xl bg-brand-500/12 border border-brand-400/25 flex items-center justify-center text-brand-300 shrink-0">
                  <Icon className="w-[18px] h-[18px]" />
                </div>
                <div>
                  <p className="text-sm font-semibold text-slate-100">{title}</p>
                  <p className="text-xs text-slate-400 mt-0.5 leading-relaxed">{desc}</p>
                </div>
              </div>
            ))}
          </div>
        </div>

        <p className="text-[11px] text-slate-600">
          Infosys Internship · Multi-Agent Financial Research System
        </p>
      </div>

      {/* Auth form */}
      <div className="flex items-center justify-center px-5 py-12 sm:px-8">
        <div className="w-full max-w-md animate-fadeUp">
          <div className="lg:hidden flex flex-col items-center mb-8">
            <div className="w-12 h-12 rounded-2xl bg-gradient-to-br from-brand-500 to-accent-600 flex items-center justify-center text-white">
              <TrendingUp className="w-6 h-6" />
            </div>
          </div>

          <div className="glass-solid rounded-3xl p-7 sm:p-9">
            <div className="mb-7">
              <h2 className="text-2xl font-bold text-slate-50">Welcome back</h2>
              <p className="text-sm text-slate-400 mt-1.5">
                Sign in to your analyst research terminal.
              </p>
            </div>

            {error && (
              <div
                role="alert"
                className="mb-5 rounded-xl bg-rose-500/10 border border-rose-500/30 text-rose-200 px-4 py-3 text-xs leading-relaxed"
              >
                {error}
              </div>
            )}

            <form className="space-y-4" onSubmit={handleSubmit}>
              <Input
                id="email"
                label="Email address"
                type="email"
                required
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                placeholder="name@company.com"
                icon={Mail}
              />

              <Input
                id="password"
                label="Password"
                type="password"
                required
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                placeholder="••••••••"
                icon={Lock}
              />

              <div className="pt-2">
                <Button type="submit" variant="primary" size="lg" className="w-full" loading={loading}>
                  Sign in
                </Button>
              </div>
            </form>

            <div className="mt-7">
              <div className="relative">
                <div className="absolute inset-0 flex items-center" aria-hidden="true">
                  <div className="w-full border-t border-white/10" />
                </div>
                <div className="relative flex justify-center">
                  <span className="bg-[#0E1426] px-3 text-[10px] uppercase tracking-[0.14em] text-slate-500">
                    Or quick test
                  </span>
                </div>
              </div>

              <div className="mt-5">
                <Button
                  type="button"
                  variant="secondary"
                  size="lg"
                  className="w-full"
                  onClick={handleDemoLogin}
                  loading={loading}
                >
                  <Sparkles className="w-4 h-4 text-accent-300" />
                  Use demo analyst credentials
                </Button>
              </div>
            </div>

            <p className="mt-7 text-center text-xs text-slate-400">
              Don&apos;t have an account?{' '}
              <Link to="/register" className="font-semibold text-brand-300 hover:text-brand-200 transition-colors">
                Create analyst account
              </Link>
            </p>
          </div>
        </div>
      </div>
    </div>
  );
};

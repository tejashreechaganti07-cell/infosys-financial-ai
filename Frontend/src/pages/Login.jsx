import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../hooks/useAuth';
import { Button } from '../components/common/Button';
import { Input } from '../components/common/Input';
import { Mail, Lock, TrendingUp, Sparkles } from 'lucide-react';

export const Login = () => {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const { login } = useAuth();
  const navigate = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setLoading(true);
    try {
      await login(email, password);
      navigate('/dashboard');
    } catch (err) {
      const detail = err.response?.data?.detail;
      let errMsg = 'Invalid email or password. Please try again.';
      if (typeof detail === 'string') {
        errMsg = detail;
      } else if (Array.isArray(detail)) {
        errMsg = detail.map(d => d.msg).join(', ') || errMsg;
      }
      setError(errMsg);
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
      setError('Could not log in with demo account.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-terminal-dark flex flex-col justify-center py-12 sm:px-6 lg:px-8 relative overflow-hidden">
      {/* Background glow effects */}
      <div className="absolute top-1/4 left-1/3 w-96 h-96 bg-emerald-500/10 rounded-full blur-3xl pointer-events-none"></div>
      <div className="absolute bottom-1/4 right-1/3 w-96 h-96 bg-cyan-500/10 rounded-full blur-3xl pointer-events-none"></div>

      <div className="sm:mx-auto sm:w-full sm:max-w-md z-10">
        <div className="flex justify-center">
          <div className="w-12 h-12 rounded-xl bg-emerald-500/10 border border-emerald-500/30 flex items-center justify-center text-emerald-400 shadow-glow-emerald">
            <TrendingUp className="w-7 h-7" />
          </div>
        </div>
        <h2 className="mt-4 text-center text-2xl font-bold text-slate-100 tracking-tight">
          Infosys AI Research Terminal
        </h2>
        <p className="mt-1 text-center text-xs text-slate-400 font-mono">
          MULTI-AGENT FINANCIAL FILING ANALYSIS SYSTEM
        </p>
      </div>

      <div className="mt-8 sm:mx-auto sm:w-full sm:max-w-md z-10">
        <div className="bg-terminal-card border border-terminal-border py-8 px-6 shadow-2xl rounded-xl sm:px-10">
          {error && (
            <div className="mb-4 bg-rose-500/15 border border-rose-500/40 text-rose-300 px-4 py-3 rounded-lg text-xs font-medium">
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
              <Button
                type="submit"
                variant="primary"
                className="w-full"
                loading={loading}
              >
                Sign Into Terminal
              </Button>
            </div>
          </form>

          <div className="mt-6">
            <div className="relative">
              <div className="absolute inset-0 flex items-center">
                <div className="w-full border-t border-terminal-border" />
              </div>
              <div className="relative flex justify-center text-xs uppercase font-mono">
                <span className="bg-terminal-card px-2 text-slate-500">Or Quick Test</span>
              </div>
            </div>

            <div className="mt-6">
              <Button
                type="button"
                variant="secondary"
                className="w-full border-emerald-500/30 text-emerald-400 hover:border-emerald-500 hover:bg-emerald-500/10"
                onClick={handleDemoLogin}
                loading={loading}
              >
                <Sparkles className="w-4 h-4 mr-2" />
                Use Demo Analyst Credentials
              </Button>
            </div>
          </div>

          <p className="mt-6 text-center text-xs text-slate-400">
            Don't have an account?{' '}
            <Link to="/register" className="font-medium text-emerald-400 hover:text-emerald-300">
              Create Analyst Account
            </Link>
          </p>
        </div>
      </div>
    </div>
  );
};

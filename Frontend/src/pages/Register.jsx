import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../hooks/useAuth';
import { Button } from '../components/common/Button';
import { Input } from '../components/common/Input';
import { Mail, Lock, User, TrendingUp } from 'lucide-react';

export const Register = () => {
  const [fullName, setFullName] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [role, setRole] = useState('Senior Financial Analyst');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const { register } = useAuth();
  const navigate = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setLoading(true);
    try {
      await register(email, password, fullName, role);
      navigate('/dashboard');
    } catch (err) {
      setError(err.response?.data?.detail || 'Registration failed. Please check your details.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-terminal-dark flex flex-col justify-center py-12 sm:px-6 lg:px-8 relative overflow-hidden">
      <div className="absolute top-1/3 right-1/4 w-96 h-96 bg-emerald-500/10 rounded-full blur-3xl pointer-events-none"></div>

      <div className="sm:mx-auto sm:w-full sm:max-w-md z-10">
        <div className="flex justify-center">
          <div className="w-12 h-12 rounded-xl bg-emerald-500/10 border border-emerald-500/30 flex items-center justify-center text-emerald-400 shadow-glow-emerald">
            <TrendingUp className="w-7 h-7" />
          </div>
        </div>
        <h2 className="mt-4 text-center text-2xl font-bold text-slate-100 tracking-tight">
          Create Analyst Account
        </h2>
        <p className="mt-1 text-center text-xs text-slate-400 font-mono">
          JOIN THE MULTI-AGENT FINANCIAL RESEARCH PLATFORM
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
              id="fullName"
              label="Full Name"
              type="text"
              required
              value={fullName}
              onChange={(e) => setFullName(e.target.value)}
              placeholder="Tejashree Chaganti"
              icon={User}
            />

            <Input
              id="email"
              label="Email address"
              type="email"
              required
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              placeholder="analyst@infosys.com"
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

            <div>
              <label htmlFor="role" className="block text-xs font-semibold text-slate-300 mb-1.5 uppercase tracking-wider">
                Professional Role
              </label>
              <select
                id="role"
                value={role}
                onChange={(e) => setRole(e.target.value)}
                className="w-full bg-terminal-dark/80 border border-terminal-border text-slate-200 text-sm rounded-lg py-2.5 px-3 focus:outline-none focus:ring-1 focus:ring-emerald-500 focus:border-emerald-500"
              >
                <option value="Senior Financial Analyst">Senior Financial Analyst</option>
                <option value="Investment Banking Analyst">Investment Banking Analyst</option>
                <option value="Equity Research Associate">Equity Research Associate</option>
                <option value="Portfolio Manager">Portfolio Manager</option>
                <option value="Finance Student / Intern">Finance Student / Intern</option>
              </select>
            </div>

            <div className="pt-2">
              <Button
                type="submit"
                variant="primary"
                className="w-full"
                loading={loading}
              >
                Register & Enter Workspace
              </Button>
            </div>
          </form>

          <p className="mt-6 text-center text-xs text-slate-400">
            Already have an account?{' '}
            <Link to="/login" className="font-medium text-emerald-400 hover:text-emerald-300">
              Sign In
            </Link>
          </p>
        </div>
      </div>
    </div>
  );
};

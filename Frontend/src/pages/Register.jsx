import { ThemeToggle } from '../components/common/ThemeToggle';

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

      const detail = err.response?.data?.detail;

      let errMsg = 'Registration failed. Please check your details.';

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

  return (

    <div className="relative min-h-screen flex items-center justify-center px-5 py-12 overflow-hidden">

      <div className="absolute top-5 right-5 z-50">

        <ThemeToggle />

      </div>

      <div className="pointer-events-none absolute inset-0 -z-10">

        <div className="absolute inset-0 bg-grid opacity-30" />

        <div className="orb top-[-12%] right-[18%] h-[440px] w-[440px] bg-accent-600/22 animate-float" />

        <div className="orb bottom-[-14%] left-[12%] h-[400px] w-[400px] bg-brand-600/22" />

      </div>

      <div className="w-full max-w-md animate-fadeUp">

        <div className="flex flex-col items-center text-center mb-8">

          <div className="w-12 h-12 rounded-2xl bg-gradient-to-br from-brand-500 to-accent-600 flex items-center justify-center text-white shadow-[0_14px_34px_-16px_rgba(99,102,241,0.95)]">

            <TrendingUp className="w-6 h-6" />

          </div>

          <h1 className="mt-5 text-2xl font-bold text-slate-50">
            Create analyst account
          </h1>

          <p className="mt-1.5 text-sm text-slate-400">
            Join the multi-agent financial research platform.
          </p>

        </div>

        <div className="glass-solid rounded-3xl p-7 sm:p-9">

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
              id="fullName"
              label="Full Name"
              type="text"
              required
              value={fullName}
              onChange={(e) => setFullName(e.target.value)}
              placeholder="Your full name"
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

              <label htmlFor="role" className="label">
                Professional Role
              </label>

              <select
                id="role"
                value={role}
                onChange={(e) => setRole(e.target.value)}
                className="field h-11 px-3.5"
              >

                <option value="Senior Financial Analyst">
                  Senior Financial Analyst
                </option>

                <option value="Investment Banking Analyst">
                  Investment Banking Analyst
                </option>

                <option value="Equity Research Associate">
                  Equity Research Associate
                </option>

                <option value="Portfolio Manager">
                  Portfolio Manager
                </option>

                <option value="Finance Student / Intern">
                  Finance Student / Intern
                </option>

              </select>

            </div>

            <div className="pt-2">

              <Button
                type="submit"
                variant="primary"
                size="lg"
                className="w-full"
                loading={loading}
              >
                Register &amp; enter workspace
              </Button>

            </div>

          </form>

          <p className="mt-7 text-center text-xs text-slate-400">

            Already have an account?{' '}

            <Link
              to="/login"
              className="font-semibold text-brand-300 hover:text-brand-200 transition-colors"
            >
              Sign in
            </Link>

          </p>

        </div>

      </div>

    </div>

  );

};
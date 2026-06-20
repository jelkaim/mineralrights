"use client";

import { useState } from 'react';
import { useAuth } from '@/context/AuthContext';
import Link from 'next/link';
import { ShieldCheck } from 'lucide-react';

export default function Login() {
  const { login } = useAuth();
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    login();
  };

  return (
    <div className="min-h-screen bg-slate-50 flex flex-col justify-center py-12 sm:px-6 lg:px-8">
      <div className="sm:mx-auto sm:w-full sm:max-w-md flex flex-col items-center">
        <div className="bg-green-500 rounded-full p-4 mb-6 text-white shadow-lg shadow-green-500/30">
          <ShieldCheck size={32} />
        </div>
        <h2 className="text-center text-3xl font-extrabold text-slate-900 mb-2">Welcome to HempGuard</h2>
        <p className="text-center text-sm text-slate-500">Sign in to continue</p>
      </div>

      <div className="mt-8 sm:mx-auto sm:w-full sm:max-w-md">
        <div className="bg-white py-8 px-4 shadow sm:rounded-lg sm:px-10 border border-slate-100">
          <form className="space-y-6" onSubmit={handleSubmit}>
            <div>
              <label className="block text-sm font-medium text-slate-700 text-center mb-1">Email</label>
              <div className="mt-1 relative">
                <input
                  type="email"
                  required
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  className="appearance-none block w-full px-3 py-2 border border-slate-200 rounded-md shadow-sm placeholder-slate-400 focus:outline-none focus:ring-slate-500 focus:border-slate-500 sm:text-sm"
                  placeholder="you@example.com"
                />
              </div>
            </div>

            <div>
              <label className="block text-sm font-medium text-slate-700 text-center mb-1">Password</label>
              <div className="mt-1">
                <input
                  type="password"
                  required
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  className="appearance-none block w-full px-3 py-2 border border-slate-200 rounded-md shadow-sm placeholder-slate-400 focus:outline-none focus:ring-slate-500 focus:border-slate-500 sm:text-sm"
                  placeholder="••••••••"
                />
              </div>
            </div>

            <div>
              <button
                type="submit"
                className="w-full flex justify-center py-2 px-4 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-slate-900 hover:bg-slate-800 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-slate-900"
              >
                Sign in
              </button>
            </div>
          </form>

          <div className="mt-6 flex items-center justify-between">
            <div className="text-sm">
              <a href="#" className="font-medium text-slate-500 hover:text-slate-700">
                Forgot password?
              </a>
            </div>
            <div className="text-sm">
              <span className="text-slate-500">Need an account? </span>
              <Link href="/signup" className="font-medium text-slate-900 hover:text-slate-700">
                Sign up
              </Link>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

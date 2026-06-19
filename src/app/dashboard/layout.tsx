"use client";

import { useAuth } from '@/context/AuthContext';
import { useRouter } from 'next/navigation';
import { useEffect } from 'react';
import Link from 'next/link';
import { Upload, History, Shield, ShieldAlert, ShieldCheck, Beaker } from 'lucide-react';

export default function DashboardLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  const { isAuthenticated } = useAuth();
  const router = useRouter();

  useEffect(() => {
    if (!isAuthenticated) {
      router.push('/login');
    }
  }, [isAuthenticated, router]);

  if (!isAuthenticated) return null;

  return (
    <div className="flex min-h-screen bg-slate-50">
      {/* Sidebar */}
      <aside className="w-64 bg-slate-50 border-r border-slate-200 flex-shrink-0 flex flex-col">
        {/* Brand */}
        <div className="h-20 flex items-center px-6 border-b border-slate-200">
          <div className="flex items-center gap-3">
            <div className="bg-blue-600 p-2 rounded-lg text-white">
              <Beaker size={24} />
            </div>
            <div>
              <h1 className="font-bold text-slate-900 leading-tight">LabCheck</h1>
              <p className="text-xs text-slate-500">Hemp Test Analysis</p>
            </div>
          </div>
        </div>

        {/* Navigation */}
        <div className="px-4 py-6">
          <h2 className="text-xs font-semibold text-slate-500 tracking-wider mb-4 px-2">NAVIGATION</h2>
          <nav className="space-y-1">
            <Link href="/dashboard" className="flex items-center gap-3 px-2 py-2 text-slate-700 hover:bg-slate-100 rounded-md font-medium text-sm">
              <Upload size={18} className="text-slate-500" />
              Upload Test
            </Link>
            <Link href="/dashboard/history" className="flex items-center gap-3 px-2 py-2 text-slate-700 hover:bg-slate-100 rounded-md font-medium text-sm">
              <History size={18} className="text-slate-500" />
              Test History
            </Link>
          </nav>
        </div>

        {/* Compliance Guide */}
        <div className="px-4 py-6 mt-auto border-t border-slate-200">
          <h2 className="text-xs font-semibold text-slate-500 tracking-wider mb-4 px-2">COMPLIANCE GUIDE</h2>
          <div className="space-y-4 px-2">
            <div className="flex items-start gap-3">
              <ShieldCheck size={18} className="text-emerald-500 mt-0.5 flex-shrink-0" />
              <div>
                <p className="text-sm font-medium text-slate-900">9-10/10</p>
                <p className="text-xs text-slate-500">Strictest state compliance</p>
              </div>
            </div>
            <div className="flex items-start gap-3">
              <Shield size={18} className="text-amber-500 mt-0.5 flex-shrink-0" />
              <div>
                <p className="text-sm font-medium text-slate-900">6-8/10</p>
                <p className="text-xs text-slate-500">Federal guidelines</p>
              </div>
            </div>
            <div className="flex items-start gap-3">
              <ShieldAlert size={18} className="text-rose-500 mt-0.5 flex-shrink-0" />
              <div>
                <p className="text-sm font-medium text-slate-900">1-5/10</p>
                <p className="text-xs text-slate-500">Below standards</p>
              </div>
            </div>
          </div>
        </div>
      </aside>

      {/* Main Content Area */}
      <main className="flex-1 overflow-auto bg-slate-50">
        {/* We can put a header here if needed or just let the page handle it */}
        <div className="p-8">
          {children}
        </div>
      </main>
    </div>
  );
}

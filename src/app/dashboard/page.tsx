"use client";

import { useAuth } from '@/context/AuthContext';
import { useRouter } from 'next/navigation';
import { useEffect } from 'react';
import AnalysisCard from '@/components/AnalysisCard';
import { LogOut, Upload, ShieldCheck } from 'lucide-react';

export default function Dashboard() {
  const { isAuthenticated, user, logout } = useAuth();
  const router = useRouter();

  useEffect(() => {
    if (!isAuthenticated) {
      router.push('/login');
    }
  }, [isAuthenticated, router]);

  if (!isAuthenticated) return null;

  // Mock data
  const mockResults = [
    { id: '1', productName: 'Premium CBD Tincture', date: 'Oct 24, 2023', score: 98, status: 'Pass' as const },
    { id: '2', productName: 'Hemp Flower - Sour Diesel', date: 'Oct 22, 2023', score: 85, status: 'Pass' as const },
    { id: '3', productName: 'Delta-8 Gummies', date: 'Oct 15, 2023', score: 62, status: 'Fail' as const },
  ];

  return (
    <div className="min-h-screen bg-slate-50">
      <nav className="bg-white shadow-sm border-b border-slate-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between h-16">
            <div className="flex items-center">
              <ShieldCheck className="text-green-500 mr-2" size={28} />
              <span className="text-xl font-bold text-slate-900">HempGuard</span>
            </div>
            <div className="flex items-center gap-4">
              <span className="text-sm text-slate-500 hidden md:block">{user?.email}</span>
              <button
                onClick={logout}
                className="p-2 text-slate-500 hover:text-slate-700 rounded-full hover:bg-slate-100"
                title="Logout"
              >
                <LogOut size={20} />
              </button>
            </div>
          </div>
        </div>
      </nav>

      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="flex justify-between items-center mb-8">
          <div>
            <h1 className="text-2xl font-bold text-slate-900">Dashboard</h1>
            <p className="text-sm text-slate-500">Manage and analyze your hemp lab test results</p>
          </div>
          <button className="flex items-center bg-slate-900 hover:bg-slate-800 text-white px-4 py-2 rounded-md text-sm font-medium transition-colors">
            <Upload size={16} className="mr-2" />
            Upload Lab Result
          </button>
        </div>

        <div className="mb-6">
          <h2 className="text-lg font-medium text-slate-900 mb-4">Recent Analyses</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {mockResults.map((result) => (
              <AnalysisCard key={result.id} {...result} />
            ))}
          </div>
        </div>
      </main>
    </div>
  );
}

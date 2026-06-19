"use client";

import { useAuth } from '@/context/AuthContext';
import { useRouter } from 'next/navigation';
import { useEffect, use, useState } from 'react';
import Link from 'next/link';
import { ArrowLeft, CheckCircle2, AlertCircle, Info } from 'lucide-react';
import ScoreGauge from '@/components/ScoreGauge';

type Metric = { name: string; status: 'Pass' | 'Fail' | 'Warning'; value: string };

type AnalysisData = {
  productName: string;
  labName: string;
  date: string;
  score: number;
  status: 'Pass' | 'Fail';
  summary: string;
  metrics: Metric[];
};

// Dummy data map
const analysesData: Record<string, AnalysisData> = {
  '1': {
    productName: 'Premium CBD Tincture',
    labName: 'GreenLeaf Labs',
    date: 'Oct 24, 2023',
    score: 98,
    status: 'Pass',
    summary: 'This product is of high quality and perfectly safe for consumption. It strictly adheres to federal guidelines with THC levels well below the 0.3% limit. No harmful contaminants were detected.',
    metrics: [
      { name: 'Potency (THC < 0.3%)', status: 'Pass', value: '0.05%' },
      { name: 'Pesticides', status: 'Pass', value: 'Not Detected' },
      { name: 'Heavy Metals', status: 'Pass', value: 'Below limits' },
      { name: 'Microbials', status: 'Pass', value: 'Clean' },
      { name: 'Residual Solvents', status: 'Pass', value: 'Clean' },
    ]
  },
  '2': {
    productName: 'Hemp Flower - Sour Diesel',
    labName: 'CannaTest',
    date: 'Oct 22, 2023',
    score: 85,
    status: 'Pass',
    summary: 'This product passes safety regulations but requires caution. While THC is compliant, there are trace amounts of heavy metals detected, though they remain within allowable limits.',
    metrics: [
      { name: 'Potency (THC < 0.3%)', status: 'Pass', value: '0.28%' },
      { name: 'Pesticides', status: 'Pass', value: 'Not Detected' },
      { name: 'Heavy Metals', status: 'Warning', value: 'Trace amounts' },
      { name: 'Microbials', status: 'Pass', value: 'Clean' },
      { name: 'Residual Solvents', status: 'Pass', value: 'Not Tested' },
    ]
  },
  '3': {
    productName: 'Delta-8 Gummies',
    labName: 'Peak Analytics',
    date: 'Oct 15, 2023',
    score: 62,
    status: 'Fail',
    summary: 'This product failed compliance testing. The Delta-9 THC concentration exceeds the federal legal limit of 0.3%. Additionally, residual solvents from the extraction process were detected above safe limits.',
    metrics: [
      { name: 'Potency (THC < 0.3%)', status: 'Fail', value: '0.45%' },
      { name: 'Pesticides', status: 'Pass', value: 'Not Detected' },
      { name: 'Heavy Metals', status: 'Pass', value: 'Clean' },
      { name: 'Microbials', status: 'Pass', value: 'Clean' },
      { name: 'Residual Solvents', status: 'Fail', value: 'Above limit (Ethanol)' },
    ]
  }
};

export default function AnalysisDetail({ params }: { params: Promise<{ id: string }> }) {
  const { isAuthenticated } = useAuth();
  const router = useRouter();
  const resolvedParams = use(params);
  const id = resolvedParams.id;

  const [data, setData] = useState<AnalysisData | null>(null);

  useEffect(() => {
    if (!isAuthenticated) {
      router.push('/login');
    }
  }, [isAuthenticated, router]);

  useEffect(() => {
    let active = true;
    const loadData = () => {
      const localData = localStorage.getItem(`analysis_${id}`);
      if (!active) return;

      if (localData) {
        try {
          setData(JSON.parse(localData));
        } catch (e) {
          console.error("Failed to parse local analysis data", e);
          setData(analysesData[id] || analysesData['1']);
        }
      } else {
        setData(analysesData[id] || analysesData['1']);
      }
    };

    // We are deliberately doing this inside useEffect to avoid Next.js hydration mismatch
    // (localStorage is not available on server).
    loadData();

    return () => { active = false; };
  }, [id]);

  if (!isAuthenticated || !data) return null;

  const isPass = data.status === 'Pass';

  return (
    <div className="min-h-screen bg-slate-50 pb-12">
      <div className="bg-white border-b border-slate-200">
        <div className="max-w-4xl mx-auto px-4 py-4 sm:px-6 lg:px-8">
          <Link href="/dashboard" className="inline-flex items-center text-sm font-medium text-slate-500 hover:text-slate-900 transition-colors">
            <ArrowLeft size={16} className="mr-1" /> Back to Dashboard
          </Link>
        </div>
      </div>

      <main className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 mt-8">
        <div className="bg-white rounded-xl shadow-sm border border-slate-200 overflow-hidden">
          {/* Header */}
          <div className="p-6 md:p-8 border-b border-slate-100 flex flex-col md:flex-row md:items-center justify-between gap-6">
            <div>
              <h1 className="text-2xl md:text-3xl font-bold text-slate-900 mb-2">{data.productName}</h1>
              <div className="flex flex-wrap items-center gap-4 text-sm text-slate-500">
                <span>Lab: <span className="font-medium text-slate-700">{data.labName}</span></span>
                <span>•</span>
                <span>Date: <span className="font-medium text-slate-700">{data.date}</span></span>
              </div>
            </div>
            <div className={`flex items-center px-4 py-2 rounded-full text-sm font-medium whitespace-nowrap self-start ${isPass ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'}`}>
              {isPass ? <CheckCircle2 size={18} className="mr-2" /> : <AlertCircle size={18} className="mr-2" />}
              {isPass ? 'Compliant & Safe' : 'Action Required'}
            </div>
          </div>

          <div className="p-6 md:p-8 grid grid-cols-1 md:grid-cols-3 gap-8">
            {/* Score Section */}
            <div className="md:col-span-1 flex flex-col items-center justify-center p-6 bg-slate-50 rounded-lg border border-slate-100">
              <ScoreGauge score={data.score} />
              <p className="text-center text-sm text-slate-500 mt-4">
                Smart Compliance Score based on federal and state standards.
              </p>
            </div>

            {/* Summary & Metrics */}
            <div className="md:col-span-2 space-y-8">
              <div>
                <h2 className="text-lg font-semibold text-slate-900 mb-3 flex items-center">
                  <Info size={18} className="mr-2 text-slate-400" /> Plain English Summary
                </h2>
                <p className="text-slate-600 leading-relaxed bg-blue-50/50 p-4 rounded-lg border border-blue-100 text-sm">
                  {data.summary}
                </p>
              </div>

              <div>
                <h2 className="text-lg font-semibold text-slate-900 mb-4">Safety & Quality Metrics</h2>
                <div className="space-y-3">
                  {data.metrics.map((metric, index: number) => (
                    <div key={index} className="flex items-center justify-between p-3 bg-white border border-slate-200 rounded-lg">
                      <span className="font-medium text-slate-700">{metric.name}</span>
                      <div className="flex items-center gap-3">
                        <span className="text-sm text-slate-500">{metric.value}</span>
                        {metric.status === 'Pass' ? (
                          <CheckCircle2 size={18} className="text-green-500" />
                        ) : metric.status === 'Warning' ? (
                          <AlertCircle size={18} className="text-yellow-500" />
                        ) : (
                          <AlertCircle size={18} className="text-red-500" />
                        )}
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          </div>
        </div>
      </main>
    </div>
  );
}

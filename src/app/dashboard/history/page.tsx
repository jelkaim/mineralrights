"use client";

import AnalysisCard from "@/components/AnalysisCard";

export default function HistoryPage() {
  const mockAnalyses = [
    {
      id: "1",
      productName: "Premium CBD Oil 1000mg",
      date: "Oct 24, 2023",
      score: 95,
      status: "Pass" as const,
    },
    {
      id: "2",
      productName: "Delta-8 Gummies",
      date: "Oct 20, 2023",
      score: 62,
      status: "Fail" as const,
    },
    {
      id: "3",
      productName: "Full Spectrum Salve",
      date: "Sep 15, 2023",
      score: 40,
      status: "Fail" as const,
    },
  ];

  return (
    <div className="max-w-4xl mx-auto pt-8">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-slate-900 mb-2">Test History</h1>
        <p className="text-slate-600">Review your past lab test analyses and compliance reports.</p>
      </div>

      <div className="space-y-4">
        {mockAnalyses.map((analysis) => (
          <AnalysisCard key={analysis.id} {...analysis} />
        ))}
      </div>
    </div>
  );
}

import Link from 'next/link';
import { FileText, CheckCircle2, AlertCircle } from 'lucide-react';

interface AnalysisCardProps {
  id: string;
  productName: string;
  date: string;
  score: number;
  status: 'Pass' | 'Fail';
}

export default function AnalysisCard({ id, productName, date, score, status }: AnalysisCardProps) {
  const isPass = status === 'Pass';

  return (
    <Link href={`/dashboard/analysis/${id}`}>
      <div className="bg-white rounded-lg shadow-sm border border-slate-200 p-5 hover:shadow-md transition-shadow cursor-pointer">
        <div className="flex justify-between items-start mb-4">
          <div className="flex items-center">
            <div className="bg-slate-100 p-2 rounded-md mr-3">
              <FileText className="text-slate-600" size={20} />
            </div>
            <div>
              <h3 className="font-medium text-slate-900">{productName}</h3>
              <p className="text-xs text-slate-500">Analyzed on {date}</p>
            </div>
          </div>
          <div className={`flex items-center px-2.5 py-1 rounded-full text-xs font-medium ${isPass ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'}`}>
            {isPass ? <CheckCircle2 size={14} className="mr-1" /> : <AlertCircle size={14} className="mr-1" />}
            {status}
          </div>
        </div>

        <div className="border-t border-slate-100 pt-4 mt-2">
          <div className="flex justify-between items-center">
            <span className="text-sm text-slate-600">Compliance Score</span>
            <span className="font-semibold text-slate-900">{score}/100</span>
          </div>
          <div className="w-full bg-slate-200 rounded-full h-2 mt-2">
            <div
              className={`h-2 rounded-full ${score >= 90 ? 'bg-green-500' : score >= 70 ? 'bg-yellow-500' : 'bg-red-500'}`}
              style={{ width: `${score}%` }}
            ></div>
          </div>
        </div>
      </div>
    </Link>
  );
}

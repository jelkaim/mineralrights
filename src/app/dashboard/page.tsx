"use client";

import { Upload, FileText } from 'lucide-react';

export default function Dashboard() {
  return (
    <div className="flex flex-col items-center max-w-4xl mx-auto pt-8">
      <div className="text-center mb-12">
        <h1 className="text-4xl font-bold text-slate-900 mb-4">Hemp Lab Test Analyzer</h1>
        <p className="text-lg text-slate-600 max-w-2xl mx-auto">
          Upload your hemp or CBD product lab results and get an instant compliance analysis with plain English explanations and safety ratings.
        </p>
      </div>

      <div className="w-full bg-white rounded-2xl shadow-sm border border-slate-200 p-12">
        <div className="flex flex-col items-center text-center">
          <div className="flex items-center gap-3 mb-2">
            <FileText className="text-blue-600" size={32} />
            <h2 className="text-2xl font-bold text-slate-900">Upload Lab Results</h2>
          </div>
          <p className="text-slate-500 mb-8">Supported formats: PDF, JPEG, PNG</p>

          <div className="w-full max-w-2xl border-2 border-dashed border-slate-300 rounded-xl p-16 hover:bg-slate-50 transition-colors cursor-pointer flex flex-col items-center">
            <div className="bg-blue-100 p-4 rounded-xl mb-6 text-blue-600">
              <Upload size={32} />
            </div>

            <h3 className="text-xl font-bold text-slate-900 mb-2">Drop your lab report here</h3>
            <p className="text-slate-500 mb-6">Or click to browse and select your PDF or image file</p>

            <button className="bg-blue-600 hover:bg-blue-700 text-white px-6 py-3 rounded-lg font-medium flex items-center gap-2 transition-colors">
              <FileText size={20} />
              Browse Files
            </button>

            <p className="text-xs text-slate-400 mt-6">
              Supports PDF, JPEG, PNG files up to 10MB
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}

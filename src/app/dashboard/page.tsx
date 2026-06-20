"use client";

import { Upload, FileText, Loader2 } from 'lucide-react';
import { useState, useRef } from 'react';
import { useRouter } from 'next/navigation';

export default function Dashboard() {
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);
  const router = useRouter();

  const uploadAndAnalyzeFile = async (file: File) => {
    setIsAnalyzing(true);

    const formData = new FormData();
    formData.append('file', file);

    try {
      const response = await fetch('/api/analyze', {
        method: 'POST',
        body: formData,
      });

      if (!response.ok) {
        throw new Error('Failed to analyze file');
      }

      const result = await response.json();

      if (result.data) {
        // Store the result temporarily in localStorage for MVP
        const id = Date.now().toString();
        localStorage.setItem(`analysis_${id}`, JSON.stringify(result.data));
        router.push(`/dashboard/analysis/${id}`);
      } else if (result.id) {
        // Fallback to mock routing if no API key is provided
        router.push(`/dashboard/analysis/${result.id}`);
      }
    } catch (error) {
      console.error(error);
      alert('Error analyzing lab report. Please ensure it is a valid PDF and try again.');
    } finally {
      setIsAnalyzing(false);
    }
  };

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files.length > 0) {
      uploadAndAnalyzeFile(e.target.files[0]);
    }
  };

  const handleDrop = (e: React.DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    if (e.dataTransfer.files && e.dataTransfer.files.length > 0) {
      uploadAndAnalyzeFile(e.dataTransfer.files[0]);
    }
  };

  const handleDragOver = (e: React.DragEvent<HTMLDivElement>) => {
    e.preventDefault();
  };

  const triggerFileInput = () => {
    fileInputRef.current?.click();
  };

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

          <input
            type="file"
            ref={fileInputRef}
            onChange={handleFileChange}
            className="hidden"
            accept=".pdf,.jpeg,.jpg,.png"
          />

          <div
            onClick={!isAnalyzing ? triggerFileInput : undefined}
            onDrop={!isAnalyzing ? handleDrop : undefined}
            onDragOver={!isAnalyzing ? handleDragOver : undefined}
            className={`w-full max-w-2xl border-2 border-dashed border-slate-300 rounded-xl p-16 transition-colors flex flex-col items-center ${isAnalyzing ? 'bg-slate-50 cursor-wait' : 'hover:bg-slate-50 cursor-pointer'}`}
          >
            {isAnalyzing ? (
              <div className="flex flex-col items-center">
                <Loader2 className="animate-spin text-blue-600 mb-4" size={48} />
                <h3 className="text-xl font-bold text-slate-900 mb-2">Analyzing Lab Report...</h3>
                <p className="text-slate-500">Extracting data and running compliance checks.</p>
              </div>
            ) : (
              <>
                <div className="bg-blue-100 p-4 rounded-xl mb-6 text-blue-600">
                  <Upload size={32} />
                </div>

                <h3 className="text-xl font-bold text-slate-900 mb-2">Drop your lab report here</h3>
                <p className="text-slate-500 mb-6">Or click to browse and select your PDF or image file</p>

                <button
                  onClick={(e) => { e.stopPropagation(); triggerFileInput(); }}
                  className="bg-blue-600 hover:bg-blue-700 text-white px-6 py-3 rounded-lg font-medium flex items-center gap-2 transition-colors"
                >
                  <FileText size={20} />
                  Browse Files
                </button>

                <p className="text-xs text-slate-400 mt-6">
                  Supports PDF, JPEG, PNG files up to 10MB
                </p>
              </>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}

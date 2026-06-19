"use client";

import { useAuth } from '@/context/AuthContext';
import Link from 'next/link';
import { ArrowLeft, ShieldCheck } from 'lucide-react';
import { useState, useRef, useEffect } from 'react';

export default function Verify() {
  const { verify } = useAuth();
  const [code, setCode] = useState(['', '', '', '', '', '']);
  const inputs = useRef<(HTMLInputElement | null)[]>([]);

  useEffect(() => {
    inputs.current = inputs.current.slice(0, 6);
  }, []);

  const handleChange = (index: number, value: string) => {
    if (value.length > 1) {
      value = value.slice(-1);
    }
    const newCode = [...code];
    newCode[index] = value;
    setCode(newCode);

    if (value !== '' && index < 5 && inputs.current[index + 1]) {
      inputs.current[index + 1]?.focus();
    }
  };

  const handleKeyDown = (index: number, e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === 'Backspace' && code[index] === '' && index > 0) {
      inputs.current[index - 1]?.focus();
    }
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    verify();
  };

  return (
    <div className="min-h-screen bg-slate-50 flex flex-col justify-center py-12 sm:px-6 lg:px-8">
      <div className="sm:mx-auto sm:w-full sm:max-w-md">
        <div className="bg-white py-8 px-4 shadow sm:rounded-lg sm:px-10 border border-slate-100">
          <div className="mb-6">
            <Link href="/login" className="flex items-center text-sm font-medium text-slate-500 hover:text-slate-700">
              <ArrowLeft size={16} className="mr-1" /> Back to sign in
            </Link>
          </div>

          <div className="flex justify-center mb-6">
            <div className="bg-slate-100 rounded-full p-4 text-slate-700">
              <ShieldCheck size={32} />
            </div>
          </div>

          <h2 className="text-center text-2xl font-bold text-slate-900 mb-2">Verify your email</h2>
          <p className="text-center text-sm text-slate-500 mb-8">
            We&apos;ve sent a 6-digit code to<br/>
            <span className="font-medium text-slate-700">user@example.com</span>
          </p>

          <form className="space-y-6" onSubmit={handleSubmit}>
            <div>
              <div className="flex justify-center gap-2 mb-2">
                {code.map((digit, index) => (
                  <input
                    key={index}
                    ref={(el) => {
                      inputs.current[index] = el;
                    }}
                    type="text"
                    inputMode="numeric"
                    maxLength={1}
                    value={digit}
                    onChange={(e) => handleChange(index, e.target.value)}
                    onKeyDown={(e) => handleKeyDown(index, e)}
                    className="w-12 h-12 text-center text-xl font-medium border border-slate-200 rounded-md shadow-sm focus:outline-none focus:ring-slate-500 focus:border-slate-500"
                  />
                ))}
              </div>
              <p className="text-center text-xs text-slate-500">Enter the verification code sent to your email</p>
            </div>

            <div>
              <button
                type="submit"
                className="w-full flex justify-center py-2 px-4 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-slate-900 hover:bg-slate-800 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-slate-900"
              >
                Verify email
              </button>
            </div>

            <div className="text-center text-sm text-slate-500">
              Didn&apos;t receive the code? <a href="#" className="font-medium text-slate-900 hover:text-slate-700">Resend</a>
            </div>
          </form>
        </div>
      </div>
    </div>
  );
}

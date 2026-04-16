"use client";
import Link from 'next/link';
import { ChevronLeft, Info } from 'lucide-react';

export default function CookiesPage() {
  return (
    <div className="min-h-screen bg-slate-50 pt-32 pb-20 px-6">
      <div className="max-w-3xl mx-auto bg-white p-12 md:p-20 rounded-[3rem] border border-slate-200 shadow-sm space-y-12">
        <div className="space-y-6">
          <Link href="/" className="inline-flex items-center gap-2 text-slate-400 hover:text-blue-600 transition-colors font-bold text-sm uppercase tracking-widest">
            <ChevronLeft className="w-4 h-4" />
            Back to Home
          </Link>
          <div className="space-y-4">
             <h1 className="text-5xl font-black tracking-tighter text-slate-900 leading-none">Cookie Policy</h1>
             <p className="text-sm font-black text-slate-400 uppercase tracking-[0.2em]">Updated April 2026</p>
          </div>
        </div>

        <div className="prose prose-slate max-w-none space-y-8">
           <p className="text-xl text-slate-600 font-medium leading-relaxed">
              We use strictly necessary cookies to ensure our identity verification pipeline remains secure and efficient.
           </p>
           <h3 className="text-xl font-black text-slate-900 tracking-tight">How we use cookies</h3>
           <p className="text-slate-500 leading-relaxed">
              Veridex AI uses cookies for session management and basic analytics. These allow us to maintain your login state throughout the verification process and monitor our system performance. We do not use advertising or tracking cookies from third parties.
           </p>
           <table className="w-full text-sm text-left border-collapse mt-8">
              <thead>
                 <tr className="border-b-2 border-slate-100">
                    <th className="py-4 font-black uppercase tracking-widest text-slate-400">Class</th>
                    <th className="py-4 font-black uppercase tracking-widest text-slate-400">Reason</th>
                 </tr>
              </thead>
              <tbody className="divide-y divide-slate-100">
                 <tr>
                    <td className="py-4 font-bold text-slate-900">Essential</td>
                    <td className="py-4 text-slate-500">Authentication and session integrity.</td>
                 </tr>
                 <tr>
                    <td className="py-4 font-bold text-slate-900">Performance</td>
                    <td className="py-4 text-slate-500">Load balancing and latency monitoring.</td>
                 </tr>
              </tbody>
           </table>
        </div>
      </div>
    </div>
  );
}

"use client";
import Link from 'next/link';
import { motion } from 'framer-motion';
import { Shield, ChevronLeft, Lock, Eye, Scale } from 'lucide-react';

export default function PrivacyPage() {
  return (
    <div className="min-h-screen bg-white pt-32 pb-20 px-6">
      <div className="max-w-4xl mx-auto space-y-16">
        <div className="space-y-6">
          <Link href="/" className="inline-flex items-center gap-2 text-slate-400 hover:text-blue-600 transition-colors font-bold text-sm uppercase tracking-widest">
            <ChevronLeft className="w-4 h-4" />
            Back to Home
          </Link>
          <div className="space-y-4">
             <div className="w-14 h-14 bg-slate-900 text-white rounded-2xl flex items-center justify-center">
                <Shield className="w-7 h-7 text-blue-500" />
             </div>
             <h1 className="text-5xl font-black tracking-tighter text-slate-900">Privacy Policy</h1>
             <p className="text-sm font-black text-slate-400 uppercase tracking-[0.3em]">Last Updated: April 16, 2026</p>
          </div>
        </div>

        <div className="prose prose-slate max-w-none space-y-12">
           <section className="space-y-6">
              <h2 className="text-2xl font-black tracking-tight text-slate-900 flex items-center gap-3">
                 <Eye className="w-6 h-6 text-blue-600" />
                 1. Data Collection
              </h2>
              <p className="text-slate-600 leading-relaxed font-medium">
                 Veridex AI collects minimal personal information required for identity verification. This includes document images, biometric vectors, and session metadata. We do not sell your personal data to third parties.
              </p>
           </section>

           <section className="space-y-6">
              <h2 className="text-2xl font-black tracking-tight text-slate-900 flex items-center gap-3">
                 <Lock className="w-6 h-6 text-blue-600" />
                 2. Encryption & Storage
              </h2>
              <p className="text-slate-600 leading-relaxed font-medium">
                 All data is encrypted in transit using TLS 1.3 and at rest using AES-256. Sensitive identity assets are stored in isolated hardware security modules (HSMs) and are purged according to your requested retention schedule.
              </p>
           </section>

           <section className="space-y-6">
              <h2 className="text-2xl font-black tracking-tight text-slate-900 flex items-center gap-3">
                 <Scale className="w-6 h-6 text-blue-600" />
                 3. Compliance
              </h2>
              <p className="text-slate-600 leading-relaxed font-medium">
                 We comply with global data protection standards, including GDPR, CCPA, and DPDP. You have the right to request deletion of any data verified through our systems at any time.
              </p>
           </section>
        </div>
        
        <div className="p-8 bg-slate-50 rounded-[2rem] border border-slate-100 flex flex-col md:flex-row items-center justify-between gap-6">
           <div>
              <h4 className="font-black text-slate-900 tracking-tight">Questions about Privacy?</h4>
              <p className="text-sm text-slate-500 font-medium">Contact our Data Protection Office.</p>
           </div>
           <button className="px-8 py-4 bg-slate-900 text-white rounded-2xl font-bold hover:bg-slate-800 transition-all">
              privacy@veridex.ai
           </button>
        </div>
      </div>
    </div>
  );
}

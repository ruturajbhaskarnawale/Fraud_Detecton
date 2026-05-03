"use client";
import Link from 'next/link';
import { motion } from 'framer-motion';
import { Shield, ArrowLeft, Lock, Eye, Scale } from 'lucide-react';

const sections = [
  {
    title: "Data Collection",
    content: ["Veridex AI collects minimal personal information required for identity verification. This includes document images, biometric vectors, and session metadata.", "We do not sell your personal data to third parties."]
  },
  {
    title: "Encryption & Storage",
    content: ["All data is encrypted in transit using TLS 1.3 and at rest using AES-256.", "Sensitive identity assets are stored in isolated hardware security modules (HSMs) and are purged according to your requested retention schedule."]
  },
  {
    title: "Compliance",
    content: ["We comply with global data protection standards, including GDPR, CCPA, and DPDP.", "You have the right to request deletion of any data verified through our systems at any time."]
  }
];

export default function PrivacyPage() {
  return (
    <div className="min-h-screen bg-background text-foreground pt-32 pb-20 px-6">
      <div className="max-w-4xl mx-auto space-y-16">
        <div className="space-y-6">
          <Link href="/" className="inline-flex items-center gap-2 text-muted-foreground hover:text-blue-500 transition-colors font-bold text-sm uppercase tracking-widest">
            <ArrowLeft className="w-4 h-4" />
            Back to Home
          </Link>
          <div className="flex flex-col md:flex-row md:items-end justify-between gap-8">
             <div className="space-y-4">
                <div className="w-14 h-14 bg-secondary text-foreground rounded-2xl flex items-center justify-center">
                   <Shield className="w-8 h-8" />
                </div>
                <h1 className="text-6xl font-black tracking-tighter">Privacy Policy</h1>
                <p className="text-sm font-black text-muted-foreground uppercase tracking-[0.3em]">Last Updated: April 16, 2026</p>
             </div>
          </div>
        </div>
        <div className="prose prose-invert max-w-none prose-slate">
          {sections.map((s) => (
            <div key={s.title} className="py-12 border-t border-border space-y-6">
              <h2 className="text-3xl font-black tracking-tight flex items-center gap-4 text-foreground">
                <span className="text-blue-500">/</span> {s.title}
              </h2>
              <div className="text-muted-foreground font-medium text-lg leading-relaxed space-y-4">
                {s.content.map((p, i) => (
                  <p key={i}>{p}</p>
                ))}
              </div>
            </div>
          ))}
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

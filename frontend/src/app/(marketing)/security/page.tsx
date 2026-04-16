"use client";
import Link from 'next/link';
import { motion } from 'framer-motion';
import { Lock, ChevronLeft, ShieldAlert, Cpu, Database, Network } from 'lucide-react';

export default function SecurityPage() {
  return (
    <div className="min-h-screen bg-[#020617] text-white pt-32 pb-20 px-6">
      <div className="max-w-5xl mx-auto space-y-20">
        <div className="space-y-8">
          <Link href="/" className="inline-flex items-center gap-2 text-slate-500 hover:text-blue-400 transition-colors font-bold text-sm uppercase tracking-widest">
            <ChevronLeft className="w-4 h-4" />
            Back to Home
          </Link>
          <div className="space-y-4">
             <div className="w-16 h-16 bg-blue-600/20 border border-blue-500/30 rounded-2xl flex items-center justify-center">
                <Lock className="w-8 h-8 text-blue-500" />
             </div>
             <h1 className="text-6xl font-black tracking-tighter italic">Security <span className="text-blue-500 not-italic">Protocol.</span></h1>
             <p className="text-xl text-slate-400 font-medium leading-relaxed max-w-2xl">
                Industrial-grade security is the core of everything we build. Our infrastructure is hardened to defend against deepfakes, injection attacks, and data tampering.
             </p>
          </div>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
           <SecurityCard 
             title="End-to-End Encryption" 
             desc="All data packets are hashed and signed. Veridex records are immutable at the architectural level."
             icon={<Database className="w-6 h-6" />}
           />
           <SecurityCard 
             title="Zero-Trust Access" 
             desc="Granular IAM controls ensure that only authorized verified endpoints can communicate with the engine."
             icon={<Cpu className="w-6 h-6" />}
           />
           <SecurityCard 
             title="Network Hardening" 
             desc="Global DDoS protection and Layer 7 firewalls monitor every request for suspicious activity patterns."
             icon={<Network className="w-6 h-6" />}
           />
        </div>

        <div className="p-12 bg-white/5 border border-white/10 rounded-[3rem] space-y-8">
           <h3 className="text-sm font-black text-blue-500 uppercase tracking-widest">Compliance & Audits</h3>
           <div className="grid grid-cols-2 md:grid-cols-4 gap-8 grayscale opacity-50 contrast-125">
              <div className="font-black text-2xl tracking-tighter">SOC2 TYPE II</div>
              <div className="font-black text-2xl tracking-tighter">GDPR CERT</div>
              <div className="font-black text-2xl tracking-tighter">PCI-DSS L1</div>
              <div className="font-black text-2xl tracking-tighter">ISO 27001</div>
           </div>
        </div>
      </div>
    </div>
  );
}

function SecurityCard({ title, desc, icon }: any) {
  return (
    <div className="p-10 bg-white/5 border border-white/10 rounded-[2.5rem] space-y-6 hover:border-blue-500/50 transition-all group">
       <div className="w-12 h-12 bg-blue-600/10 text-blue-500 rounded-2xl flex items-center justify-center group-hover:scale-110 transition-transform">
          {icon}
       </div>
       <div className="space-y-3">
          <h4 className="text-2xl font-black tracking-tighter">{title}</h4>
          <p className="text-sm text-slate-400 font-medium leading-relaxed">{desc}</p>
       </div>
    </div>
  );
}

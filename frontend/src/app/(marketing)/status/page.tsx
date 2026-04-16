"use client";
import Link from 'next/link';
import { motion } from 'framer-motion';
import { Activity, ChevronLeft, CheckCircle2, Clock, Globe, ShieldCheck } from 'lucide-react';
import { useState, useEffect } from 'react';

export default function StatusPage() {
  const [uptime, setUptime] = useState(99.98);

  return (
    <div className="min-h-screen bg-slate-50 pt-32 pb-20 px-6">
      <div className="max-w-4xl mx-auto space-y-12">
        <div className="flex flex-col md:flex-row md:items-end justify-between gap-6">
           <div className="space-y-4">
              <Link href="/" className="inline-flex items-center gap-2 text-slate-400 hover:text-blue-600 transition-colors font-bold text-sm uppercase tracking-widest">
                <ChevronLeft className="w-4 h-4" />
                Back to Home
              </Link>
              <h1 className="text-5xl font-black tracking-tighter text-slate-900">System Status</h1>
           </div>
           
           <div className="px-6 py-3 bg-emerald-100 text-emerald-700 rounded-2xl flex items-center gap-3 border border-emerald-200 shadow-sm shadow-emerald-100">
              <div className="w-2.5 h-2.5 bg-emerald-600 rounded-full animate-pulse" />
              <span className="font-black text-sm uppercase tracking-widest">All Systems Operational</span>
           </div>
        </div>

        {/* Real-time Metrics */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
           <MetricCard label="API Uptime" value={`${uptime}%`} detail="Past 90 days" icon={<Globe className="w-5 h-5" />} />
           <MetricCard label="Avg Response" value="1.2s" detail="Global Latency" icon={<Clock className="w-5 h-5" />} />
           <MetricCard label="Security" value="ACTIVE" detail="Firewall Layer 7" icon={<ShieldCheck className="w-5 h-5" />} />
        </div>

        {/* Components Board */}
        <div className="bg-white rounded-[2.5rem] border border-slate-200 shadow-sm overflow-hidden">
           <div className="p-8 border-b border-slate-100 bg-slate-50/50">
              <h3 className="text-sm font-black text-slate-900 uppercase tracking-widest">Global Node Performance</h3>
           </div>
           <div className="p-8 space-y-2">
              <StatusRow name="Forensic Engine" region="US-EAST-1" status="Online" />
              <StatusRow name="OCR Extraction Pipeline" region="EU-WEST-2" status="Online" />
              <StatusRow name="Face Match Vectorizer" region="AP-SOUTH-1" status="Online" />
              <StatusRow name="Authentication Service" region="Global" status="Online" />
              <StatusRow name="Database Cluster" region="Multi-Region" status="Degraded" warning />
           </div>
        </div>

        {/* Incident History Header */}
        <div className="space-y-6 pt-10">
           <h3 className="text-sm font-black text-slate-400 uppercase tracking-widest">Incident History</h3>
           <div className="space-y-4">
              {[
                { date: 'Apr 12', title: 'Scheduled Database Maintenance', type: 'MAINTENANCE' },
                { date: 'Mar 28', title: 'Increased Latency in AP-SOUTH-1', type: 'RESOLVED' },
                { date: 'Mar 15', title: 'API Service Interruption', type: 'RESOLVED' }
              ].map((inc, i) => (
                <div key={i} className="flex items-center gap-6 p-6 bg-white border border-slate-100 rounded-2xl hover:border-slate-200 transition-all">
                   <span className="text-sm font-black text-slate-400 w-16 uppercase tracking-tighter">{inc.date}</span>
                   <div className="flex-1">
                      <h4 className="font-bold text-slate-900 tracking-tight">{inc.title}</h4>
                      <p className="text-[10px] font-black text-blue-600 uppercase tracking-widest mt-1">{inc.type}</p>
                   </div>
                </div>
              ))}
           </div>
        </div>
      </div>
    </div>
  );
}

function MetricCard({ label, value, detail, icon }: any) {
  return (
    <div className="p-8 bg-white border border-slate-200 rounded-[2rem] shadow-sm space-y-4 hover:shadow-md transition-all">
       <div className="w-10 h-10 bg-slate-50 rounded-xl flex items-center justify-center text-slate-400">{icon}</div>
       <div>
          <h4 className="text-2xl font-black text-slate-900 tracking-tighter">{value}</h4>
          <p className="text-[10px] font-black text-slate-400 uppercase tracking-widest">{label}</p>
          <p className="text-[10px] font-bold text-slate-400/60 uppercase tracking-widest mt-1">{detail}</p>
       </div>
    </div>
  );
}

function StatusRow({ name, region, status, warning = false }: any) {
  return (
    <div className="flex items-center justify-between p-4 bg-white hover:bg-slate-50 rounded-xl transition-all border border-transparent hover:border-slate-100">
       <div className="flex items-center gap-4">
          <div className={cn("w-2 h-2 rounded-full", warning ? "bg-amber-400" : "bg-emerald-500")} />
          <div>
             <h4 className="font-bold text-slate-900 text-sm tracking-tight">{name}</h4>
             <p className="text-[9px] font-black text-slate-400 uppercase tracking-widest">{region}</p>
          </div>
       </div>
       <span className={cn("text-[10px] font-black uppercase tracking-widest", warning ? "text-amber-600" : "text-emerald-600")}>
          {status}
       </span>
    </div>
  );
}

function cn(...inputs: any[]) {
  return inputs.filter(Boolean).join(' ');
}

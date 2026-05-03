"use client";
import { useEffect, useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { ShieldCheck, ShieldAlert, ArrowLeft, Download, Clock, Eye, Fingerprint, FileText, Lock } from 'lucide-react';
import { useParams, useRouter } from 'next/navigation';
import Link from 'next/link';
import { verificationService, VerifyResponse } from '@/services/api';
import { cn } from '@/lib/utils';
import { useResultStore } from '@/stores/useResultStore';
import { ResultPanelSkeleton } from '@/components/Skeleton';
import { DeepAnalysisGrid } from '@/components/results/DeepAnalysisGrid';
import { SignalMatrix } from '@/components/results/SignalMatrix';
import { CriticalFlagsPanel } from '@/components/results/CriticalFlagsPanel';
import { AssetCard } from '@/components/results/AssetCard';
import { AuditTimeline } from '@/components/results/AuditTimeline';

export default function ResultsPage() {
  const { id } = useParams();
  const router = useRouter();
  
  const lastResult = useResultStore((state) => state.lastResult);
  
  const [data, setData] = useState<VerifyResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [selectedAsset, setSelectedAsset] = useState<string | null>(null);

  const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

  useEffect(() => {
    const fetchResult = async () => {
      if (lastResult && lastResult.tracking_id === id) {
        setData(lastResult);
        setLoading(false);
        return;
      }

      try {
        if (!id) return;
        const record = await verificationService.getRecord(id as string);
        setData(record);
      } catch (err: any) {
        console.error("Failed to fetch result:", err);
        setError("Forensic record not found or inaccessible.");
      } finally {
        setLoading(false);
      }
    };
    fetchResult();
  }, [id, lastResult]);

  if (loading) return (
    <div className="max-w-7xl mx-auto py-10 px-4">
      <ResultPanelSkeleton />
    </div>
  );

  if (error || !data) return (
    <div className="max-w-xl mx-auto py-20 px-6 text-center space-y-6">
      <div className="w-20 h-20 bg-rose-900/30 text-rose-500 rounded-3xl flex items-center justify-center mx-auto shadow-sm border border-rose-500/30">
        <ShieldAlert className="w-10 h-10" />
      </div>
      <div className="space-y-2">
         <h1 className="text-2xl font-black text-white uppercase tracking-tight">Audit Access Denied</h1>
         <p className="text-slate-400 font-medium">{error || "The requested verification token has expired or is invalid."}</p>
      </div>
      <Link href="/verify" className="inline-flex items-center gap-2 px-8 py-4 bg-white text-slate-900 rounded-2xl font-bold text-xs uppercase tracking-widest hover:bg-slate-200 transition-all">
         <ArrowLeft className="w-4 h-4" />
         Restart Pipeline
      </Link>
    </div>
  );

  const { decision, risk, ocr, document, biometrics, forensics, fraud, metadata: net_metadata, image_paths, timestamp } = data;
  const trust_index = Math.max(0, 100 - ((risk?.score || 0) * 100));

  const verdictStyles: Record<string, { bg: string; text: string; icon: any; label: string }> = {
    'ACCEPT': { bg: 'bg-emerald-900/20 border-emerald-500/30', text: 'text-emerald-400', icon: ShieldCheck, label: 'Verified Safe' },
    'REJECT': { bg: 'bg-rose-900/20 border-rose-500/30', text: 'text-rose-400', icon: ShieldAlert, label: 'High Risk Cluster' },
    'REVIEW': { bg: 'bg-amber-900/20 border-amber-500/30', text: 'text-amber-400', icon: Clock, label: 'Manual Review Required' },
    'ABSTAIN': { bg: 'bg-slate-800/50 border-slate-700', text: 'text-slate-400', icon: Eye, label: 'Insufficient Signal' }
  };

  const currentVerdict = verdictStyles[decision] || verdictStyles['ABSTAIN'];

  const display_factors = [
    ...(fraud?.rules_triggered || []),
    ...(forensics?.forgery_flags || []),
    ...(biometrics?.flags?.filter(f => f !== 'skipped') || [])
  ];

  return (
    <div className="space-y-10 max-w-7xl mx-auto py-10 px-4 print:p-0">
      <div className="flex flex-col md:flex-row md:items-end justify-between gap-6 pb-6 border-b border-slate-800">
        <div className="space-y-2">
          <div className="flex items-center gap-2">
            <span className="px-2 py-0.5 bg-blue-600 text-white text-[9px] font-black uppercase tracking-widest rounded">Certified Audit</span>
            <span className="text-[10px] font-bold text-slate-500 uppercase tracking-widest font-mono">ID: {id?.toString().slice(0, 12)}</span>
          </div>
          <h1 className="text-4xl font-black text-white tracking-tight">Forensic Intelligence Report</h1>
        </div>
        <div className="flex items-center gap-3 print:hidden">
           <button onClick={() => window.print()} className="px-6 py-3 bg-slate-800 text-white rounded-2xl font-bold text-xs uppercase tracking-widest flex items-center gap-2 hover:bg-slate-700 transition-all shadow-xl border border-slate-700">
              <Download className="w-4 h-4" /> Export PDF
           </button>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-12 gap-10">
        {/* LEFT COLUMN: Decision, Risk, & Red Flags */}
        <div className="lg:col-span-4 space-y-8">
          <div className={cn("p-10 rounded-[2.5rem] border flex flex-col items-center text-center space-y-8 shadow-2xl", currentVerdict.bg)}>
            <div className={cn("w-20 h-20 rounded-3xl bg-slate-900 flex items-center justify-center shadow-xl border border-white/10")}>
               <currentVerdict.icon className={cn("w-10 h-10", currentVerdict.text)} />
            </div>
            <div className="space-y-2">
               <p className="text-[10px] font-black uppercase tracking-[0.2em] opacity-50 text-white">System Decision</p>
               <h2 className={cn("text-5xl font-black tracking-tighter leading-none", currentVerdict.text)}>{decision}</h2>
               <p className={cn("text-xs font-bold opacity-80 italic", currentVerdict.text)}>{currentVerdict.label}</p>
            </div>
            
            <div className="w-full space-y-3 pt-6 border-t border-white/10">
              <div className="flex justify-between items-center text-[10px] font-black uppercase tracking-widest opacity-70 text-white">
                <span>Trust Index</span>
                <span>{trust_index.toFixed(1)}%</span>
              </div>
              <div className="w-full h-3 bg-slate-900 rounded-full overflow-hidden border border-slate-700">
                 <motion.div 
                   initial={{ width: 0 }}
                   animate={{ width: `${trust_index}%` }}
                   className={cn("h-full", trust_index > 80 ? "bg-emerald-500" : trust_index > 40 ? "bg-amber-500" : "bg-rose-500")} 
                 />
              </div>
            </div>
          </div>

          <CriticalFlagsPanel flags={display_factors as string[]} />
        </div>

        {/* RIGHT COLUMN: Signal Matrix & Raw Evidence */}
        <div className="lg:col-span-8 space-y-10">
          <SignalMatrix data={data} />

          <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
            <AssetCard label="Scanned Document" icon={<FileText/>} src={image_paths?.id_card ? `${API_URL}${image_paths.id_card}` : null} onExpand={setSelectedAsset} />
            <AssetCard label="Live Biometric" icon={<Fingerprint/>} src={image_paths?.selfie ? `${API_URL}${image_paths.selfie}` : null} onExpand={setSelectedAsset} />
          </div>

          <div className="flex items-center justify-between px-6 py-4 bg-slate-900 rounded-2xl border border-slate-800 shadow-xl">
             <div className="flex items-center gap-4">
               <Lock className="w-4 h-4 text-slate-500" />
               <p className="text-[10px] font-bold text-slate-400 uppercase tracking-widest">Signed & Encrypted: {new Date(timestamp || Date.now()).toLocaleString()}</p>
             </div>
             <p className="text-[10px] font-black text-blue-500 uppercase tracking-widest cursor-pointer hover:underline">View Decision Trace</p>
          </div>
        </div>
      </div>

      {/* DEEP VERIFICATION ANALYSIS */}
      <DeepAnalysisGrid data={data} />

      {/* AUDIT TRACE & SYSTEM LOGS */}
      <AuditTimeline data={data} />

      <AnimatePresence>
        {selectedAsset && (
          <motion.div 
            initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }}
            onClick={() => setSelectedAsset(null)}
            className="fixed inset-0 z-50 bg-slate-950/95 flex items-center justify-center p-12 backdrop-blur-md cursor-zoom-out print:hidden"
          >
            <motion.img 
              initial={{ scale: 0.9 }} animate={{ scale: 1 }}
              src={selectedAsset} alt="Audit Asset" className="max-w-full max-h-full rounded-2xl shadow-2xl border border-slate-800" 
            />
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}

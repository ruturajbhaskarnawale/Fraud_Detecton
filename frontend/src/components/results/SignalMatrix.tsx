import { Activity } from 'lucide-react';
import { motion } from 'framer-motion';
import { VerifyResponse } from '@/services/api';
import { cn } from '@/lib/utils';

export function SignalMatrix({ data }: { data: VerifyResponse }) {
  const { ocr, document, biometrics, forensics, fraud, metadata } = data;

  return (
    <div className="bg-slate-900 border border-slate-800 rounded-[2.5rem] p-10 shadow-2xl text-white">
      <div className="flex justify-between items-center mb-10 pb-6 border-b border-slate-800/50">
        <h3 className="text-xs font-black uppercase tracking-widest flex items-center gap-2 text-white">
          <Activity className="w-4 h-4 text-blue-500" /> Calibrated Signal Matrix
        </h3>
        <p className="text-[10px] font-mono text-slate-500">V2.5.0-STABLE</p>
      </div>
      
      <div className="grid grid-cols-1 md:grid-cols-2 gap-x-12 gap-y-8">
        <SignalMetric label="OCR Confidence" value={ocr?.confidence} />
        <SignalMetric label="Doc Integrity" value={document?.confidence} />
        <SignalMetric label="Face Similarity" value={biometrics?.face_similarity} />
        <SignalMetric label="Liveness Check" value={biometrics?.liveness_score} />
        <SignalMetric label="Forensic Score" value={forensics ? 1 - forensics.tamper_score : undefined} />
        <SignalMetric label="Fraud Risk" value={fraud ? 1 - fraud.fraud_score : undefined} />
        <SignalMetric label="Network Trust" value={metadata ? 1 - metadata.ip_risk : undefined} />
        <SignalMetric label="Device Integrity" value={metadata ? 1 - metadata.device_risk : undefined} />
      </div>
    </div>
  );
}

function SignalMetric({ label, value }: { label: string; value: number | undefined }) {
  const pct = (value || 0) * 100;
  const isUndefined = value === undefined;
  
  return (
    <div className="space-y-3">
      <div className="flex justify-between items-center text-[10px] font-black uppercase tracking-widest">
        <span className="text-slate-400">{label}</span>
        <span className={cn("font-mono", isUndefined ? "text-slate-600" : pct > 70 ? "text-emerald-400" : pct > 30 ? "text-amber-400" : "text-rose-400")}>
          {isUndefined ? "N/A" : `${pct.toFixed(1)}%`}
        </span>
      </div>
      <div className="w-full h-1.5 bg-slate-800 rounded-full overflow-hidden">
        {!isUndefined && (
          <motion.div 
            initial={{ width: 0 }}
            animate={{ width: `${pct}%` }}
            className={cn("h-full", pct > 70 ? "bg-emerald-500 shadow-[0_0_10px_rgba(16,185,129,0.5)]" : pct > 30 ? "bg-amber-500 shadow-[0_0_10px_rgba(245,158,11,0.5)]" : "bg-rose-500 shadow-[0_0_10px_rgba(225,29,72,0.5)]")} 
          />
        )}
      </div>
    </div>
  );
}

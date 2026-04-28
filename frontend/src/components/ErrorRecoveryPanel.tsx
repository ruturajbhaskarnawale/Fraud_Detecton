import React from 'react';
import { motion } from 'framer-motion';
import { AlertCircle, RotateCcw, Lightbulb, Camera, Layout } from 'lucide-react';

interface ErrorRecoveryPanelProps {
  error: string | null;
  onRetry: () => void;
}

export function ErrorRecoveryPanel({ error, onRetry }: ErrorRecoveryPanelProps) {
  const isAbstain = error?.toLowerCase().includes('quality') || error?.toLowerCase().includes('confidence');

  return (
    <motion.div 
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className="text-center space-y-10"
    >
      <div className="w-20 h-20 bg-rose-50 text-rose-500 rounded-[2rem] flex items-center justify-center mx-auto shadow-xl shadow-rose-100/50">
        <AlertCircle className="w-10 h-10" />
      </div>

      <div className="space-y-4">
        <h3 className="text-2xl font-black text-slate-900 uppercase tracking-tight">
          {isAbstain ? "Signal Quality Issue" : "Verification Failed"}
        </h3>
        <p className="text-slate-500 text-sm font-medium max-w-sm mx-auto">
          {error || "The AI encountered an anomaly while processing your request."}
        </p>

        {isAbstain && (
          <div className="bg-slate-50 p-8 rounded-[2.5rem] text-left space-y-6 max-w-sm mx-auto border border-slate-100 shadow-inner mt-8">
            <p className="text-[10px] font-black uppercase tracking-[0.2em] text-blue-600">Actionable Improvements:</p>
            <div className="space-y-5">
              <RecoveryTip 
                icon={<Lightbulb className="w-4 h-4" />}
                title="Lighting Control"
                desc="Avoid direct overhead glare or extreme shadows on the ID card surface."
              />
              <RecoveryTip 
                icon={<Camera className="w-4 h-4" />}
                title="Biometric Alignment"
                desc="Keep your face centered and look directly into the camera lens."
              />
              <RecoveryTip 
                icon={<Layout className="w-4 h-4" />}
                title="Frame Completeness"
                desc="Ensure all 4 corners of the document are visible within the frame."
              />
            </div>
          </div>
        )}
      </div>

      <button 
        onClick={onRetry} 
        className="px-10 py-5 bg-slate-900 text-white rounded-2xl font-black text-[10px] uppercase tracking-[0.3em] hover:bg-black transition-all shadow-2xl shadow-slate-200 flex items-center gap-3 mx-auto"
      >
        <RotateCcw className="w-4 h-4" />
        Retry Pipeline
      </button>
    </motion.div>
  );
}

function RecoveryTip({ icon, title, desc }: { icon: React.ReactNode; title: string; desc: string }) {
  return (
    <div className="flex gap-4">
      <div className="w-8 h-8 rounded-xl bg-white border border-slate-100 flex items-center justify-center text-slate-400 flex-shrink-0 shadow-sm">
        {icon}
      </div>
      <div>
        <p className="text-[11px] font-black text-slate-900 uppercase tracking-tight leading-none">{title}</p>
        <p className="text-[10px] font-bold text-slate-500 mt-1.5 leading-relaxed">{desc}</p>
      </div>
    </div>
  );
}

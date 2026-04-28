"use client";
import { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { 
  ShieldCheck, 
  ArrowRight, 
  SearchCode,
  Fingerprint,
  Activity,
  AlertCircle,
} from 'lucide-react';
import { useRouter } from 'next/navigation';
import Dropzone from '@/components/Dropzone';
import StepProgress from '@/components/StepProgress';
import { ErrorRecoveryPanel } from '@/components/ErrorRecoveryPanel';
import { verificationService } from '@/services/api';
import { cn } from '@/lib/utils';
import { useVerificationStore } from '@/stores/useVerificationStore';
import { useSessionStore } from '@/stores/useSessionStore';
import { useResultStore } from '@/stores/useResultStore';

export default function VerifyPage() {
  const router = useRouter();
  
  const { 
    stage, 
    idFile, 
    selfieFile, 
    error, 
    setStage, 
    setError, 
    setIdFile,
    setSelfieFile,
    reset: resetStore 
  } = useVerificationStore();
  
  const metadata = useSessionStore((state) => state.metadata);
  const setLastResult = useResultStore((state) => state.setLastResult);

  const [activeStep, setActiveStep] = useState(0);
  const [logs, setLogs] = useState<string[]>([]);
  
  const progressMessages = [
    "Establishing secure connection to AI nodes...",
    "Extracting OCR & Identity Metadata...",
    "Matching Biometrics & Liveness signals...",
    "Auditing pixel-level Forensic signatures...",
    "Consulting Fraud Graph Intelligence...",
    "Fusing signals into final Risk Score..."
  ];

  const startVerification = async () => {
    if (!idFile) return;
    
    setStage('uploading');
    setActiveStep(0);
    setError(null);
    setLogs([progressMessages[0]]);

    try {
      const statusUpdates = [
        { stage: 'ocr', step: 1, delay: 1000, msg: progressMessages[1] },
        { stage: 'face', step: 2, delay: 2500, msg: progressMessages[2] },
        { stage: 'forensics', step: 3, delay: 4500, msg: progressMessages[3] },
        { stage: 'fraud', step: 4, delay: 6500, msg: progressMessages[4] },
        { stage: 'fusing', step: 5, delay: 8500, msg: progressMessages[5] },
      ];

      statusUpdates.forEach(({ stage: s, step, delay, msg }) => {
        setTimeout(() => {
          if (useVerificationStore.getState().stage !== 'failed') {
            setStage(s as any);
            setActiveStep(step);
            setLogs(prev => [...prev, msg].slice(-3));
          }
        }, delay);
      });

      const response = await verificationService.verify(
        idFile, 
        selfieFile || undefined, 
        metadata || undefined
      );
      
      setLastResult(response);
      setActiveStep(6);
      
      if (response.decision === 'ABSTAIN') {
        setStage('failed');
        setError("Input quality insufficient for high-confidence verification. (ABSTAIN)");
      } else {
        setStage('completed');
        setTimeout(() => {
          router.push(`/results/${response.tracking_id}`);
        }, 1500);
      }

    } catch (err: any) {
      console.error("Verification failed:", err);
      const msg = err.response?.data?.error || err.message || "Unable to complete verification.";
      setError(msg);
      setStage('failed');
    }
  };

  const resetPipeline = () => {
    resetStore();
    setActiveStep(0);
    setLogs([]);
  };

  return (
    <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
      <div className="text-center space-y-4 mb-12">
        <h1 className="text-4xl font-black text-white tracking-tighter uppercase">Identity Verification</h1>
        <p className="text-slate-400 text-lg max-w-2xl mx-auto font-medium">Verify documents and biometrics with industrial-grade AI precision.</p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-12 gap-12 items-start">
        <div className="lg:col-span-4 bg-slate-900 border border-slate-800 p-10 rounded-[2.5rem] shadow-sm h-full">
           <h3 className="text-[10px] font-black uppercase tracking-[0.2em] text-slate-500 mb-10 pb-4 border-b border-slate-800/50">Pipeline Nodes</h3>
           <StepProgress activeStep={activeStep} status={stage === 'failed' ? 'failed' : stage === 'completed' ? 'completed' : stage === 'idle' ? 'idle' : 'processing'} />
        </div>

        <div className="lg:col-span-8 bg-slate-900 border border-slate-800 p-12 rounded-[2.5rem] shadow-xl shadow-slate-900/50 min-h-[640px] flex flex-col justify-center">
           <AnimatePresence mode="wait">
              {['uploading', 'ocr', 'face', 'liveness', 'forensics', 'fraud', 'fusing'].includes(stage) ? (
                <motion.div 
                  key="processing"
                  initial={{ opacity: 0 }}
                  animate={{ opacity: 1 }}
                  exit={{ opacity: 0 }}
                  className="space-y-12 text-center"
                >
                   <div className="relative w-40 h-40 mx-auto">
                      <div className="absolute inset-0 border-8 border-blue-900/30 rounded-full" />
                      <div className="absolute inset-0 border-8 border-blue-600 rounded-full border-t-transparent animate-spin" />
                      <div className="absolute inset-0 flex items-center justify-center bg-slate-800 rounded-full m-2 shadow-inner">
                         <Activity className="w-12 h-12 text-blue-500" />
                      </div>
                   </div>
                   
                   <div className="space-y-6">
                      <h3 className="text-3xl font-black text-white uppercase tracking-tight">Neural Processing</h3>
                      <div className="max-w-xs mx-auto space-y-3">
                        {logs.map((log, i) => (
                           <p key={i} className={cn(
                             "text-[11px] font-black uppercase tracking-widest transition-all",
                             i === logs.length - 1 ? "text-blue-400" : "text-slate-600"
                           )}>{log}</p>
                        ))}
                      </div>
                   </div>
                </motion.div>
              ) : stage === 'completed' ? (
                <motion.div 
                   key="completed"
                   initial={{ opacity: 0, scale: 0.9 }}
                   animate={{ opacity: 1, scale: 1 }}
                   className="text-center space-y-8"
                >
                   <div className="w-24 h-24 bg-emerald-900/20 text-emerald-400 border border-emerald-500/20 rounded-[2rem] flex items-center justify-center mx-auto mb-4 shadow-xl">
                      <ShieldCheck className="w-12 h-12" />
                   </div>
                   <div className="space-y-2">
                     <h3 className="text-3xl font-black text-white uppercase tracking-tight">Audit Certified</h3>
                     <p className="text-slate-500 font-bold uppercase text-[10px] tracking-[0.2em]">Redirecting to forensic report...</p>
                   </div>
                </motion.div>
              ) : stage === 'failed' ? (
                <ErrorRecoveryPanel key="failed" error={error} onRetry={resetPipeline} />
              ) : (
                <motion.div 
                  key="idle"
                  initial={{ opacity: 0 }}
                  animate={{ opacity: 1 }}
                  className="space-y-12"
                >
                   <div className="grid grid-cols-1 md:grid-cols-2 gap-10">
                      <div className="space-y-4">
                         <div className="flex justify-between items-center px-1">
                            <p className="text-[10px] font-black uppercase tracking-[0.2em] text-slate-500">Node 01: Document</p>
                            <span className="text-[9px] font-bold text-blue-400 border border-blue-800/50 bg-blue-900/20 px-2 py-0.5 rounded">Required</span>
                         </div>
                         <Dropzone 
                           label="ID Card (Front)" 
                           onFileSelect={setIdFile}
                           accept=".jpg,.jpeg,.png,.pdf"
                           icon={<SearchCode className="w-8 h-8 text-slate-300" />}
                           className="h-[300px] rounded-[2rem]"
                         />
                      </div>
                      <div className="space-y-4">
                         <div className="flex justify-between items-center px-1">
                            <p className="text-[10px] font-black uppercase tracking-[0.2em] text-slate-500">Node 02: Biometric</p>
                            <span className="text-[9px] font-bold text-blue-400 border border-blue-800/50 bg-blue-900/20 px-2 py-0.5 rounded">Required</span>
                         </div>
                         <Dropzone 
                           label="Live Selfie" 
                           onFileSelect={setSelfieFile}
                           accept=".jpg,.jpeg,.png"
                           icon={<Fingerprint className="w-8 h-8 text-slate-300" />}
                           className="h-[300px] rounded-[2rem]"
                         />
                      </div>
                   </div>

                   <button
                     disabled={!idFile || !selfieFile}
                     onClick={startVerification}
                     className="w-full bg-white hover:bg-slate-200 text-slate-900 disabled:bg-slate-800 disabled:text-slate-600 disabled:cursor-not-allowed font-black text-[10px] uppercase tracking-[0.3em] py-6 rounded-[2rem] transition-all shadow-xl shadow-slate-900/50 flex items-center justify-center gap-3"
                   >
                     <span>Initiate Pipeline</span>
                     <ArrowRight className="w-5 h-5" />
                   </button>
                </motion.div>
              )}
           </AnimatePresence>
        </div>
      </div>
    </div>
  );
}

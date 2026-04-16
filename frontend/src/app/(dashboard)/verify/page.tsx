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
  Loader2
} from 'lucide-react';
import { useRouter } from 'next/navigation';
import Dropzone from '@/components/Dropzone';
import StepProgress, { VerificationState } from '@/components/StepProgress';
import { verificationService } from '@/services/api';
import { cn } from '@/lib/utils';

export default function VerifyPage() {
  const router = useRouter();
  const [idFile, setIdFile] = useState<File | null>(null);
  const [selfieFile, setSelfieFile] = useState<File | null>(null);
  const [status, setStatus] = useState<VerificationState>('idle');
  const [activeStep, setActiveStep] = useState(0);
  const [error, setError] = useState<string | null>(null);
  const [logs, setLogs] = useState<string[]>([]);
  
  const progressMessages = [
    "Establishing secure connection to AI nodes...",
    "Validating document integrity...",
    "Extracting identity field metadata...",
    "Matching biometric facial landmarks...",
    "Generating final verification certificate..."
  ];

  const startVerification = async () => {
    if (!idFile) return;
    
    setStatus('processing');
    setActiveStep(1);
    setError(null);
    setLogs([progressMessages[0]]);

    try {
      // Simple status progression for UX
      const statusUpdates = [
        { step: 1, delay: 1500, msg: progressMessages[1] },
        { step: 2, delay: 3500, msg: progressMessages[2] },
        { step: 3, delay: 6000, msg: progressMessages[3] },
        { step: 3, delay: 8500, msg: progressMessages[4] },
      ];

      statusUpdates.forEach(({ step, delay, msg }) => {
        setTimeout(() => {
          setActiveStep(step);
          setLogs(prev => [...prev, msg].slice(-3));
        }, delay);
      });

      const response = await verificationService.verify(idFile, selfieFile || undefined);
      
      setActiveStep(4);
      setStatus('completed');
      
      setTimeout(() => {
        router.push(`/results/${response.tracking_id}`);
      }, 1500);

    } catch (err: any) {
      console.error("Verification failed:", err);
      const msg = err.response?.data?.error || err.message || "Unable to complete verification. Please try again.";
      setError(msg);
      setStatus('failed');
    }
  };

  return (
    <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
      <div className="text-center space-y-4 mb-12">
        <h1 className="text-4xl font-bold text-slate-900 tracking-tight">Identity Verification</h1>
        <p className="text-slate-700 text-lg max-w-2xl mx-auto font-medium">Verify documents and biometrics with industrial-grade AI precision.</p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-12 gap-12 items-start">
        {/* Left: Step Guidance */}
        <div className="lg:col-span-4 bg-white border border-slate-200 p-8 rounded-2xl shadow-sm h-full">
           <h3 className="text-xs font-bold uppercase tracking-widest text-slate-500 mb-8 pb-4 border-b border-slate-100">Verification Steps</h3>
           <StepProgress activeStep={activeStep} status={status} />
        </div>

        {/* Right: Upload Actions */}
        <div className="lg:col-span-8 bg-white border border-slate-200 p-10 rounded-2xl shadow-sm min-h-[560px] flex flex-col justify-center">
           <AnimatePresence mode="wait">
              {status === 'processing' ? (
                <motion.div 
                  key="processing"
                  initial={{ opacity: 0 }}
                  animate={{ opacity: 1 }}
                  exit={{ opacity: 0 }}
                  className="space-y-10 text-center"
                >
                   <div className="relative w-32 h-32 mx-auto">
                      <div className="absolute inset-0 border-4 border-blue-50/50 rounded-full" />
                      <div className="absolute inset-0 border-4 border-blue-600 rounded-full border-t-transparent animate-spin" />
                      <div className="absolute inset-0 flex items-center justify-center">
                         <Activity className="w-10 h-10 text-blue-600" />
                      </div>
                   </div>
                   
                   <div className="space-y-4">
                      <h3 className="text-2xl font-bold text-slate-900">Processing Document</h3>
                      <div className="max-w-sm mx-auto space-y-2">
                        {logs.map((log, i) => (
                           <p key={i} className="text-sm font-medium text-slate-400 animate-in fade-in slide-in-from-bottom-1">{log}</p>
                        ))}
                      </div>
                   </div>
                </motion.div>
              ) : status === 'completed' ? (
                <motion.div 
                   key="completed"
                   initial={{ opacity: 0, scale: 0.95 }}
                   animate={{ opacity: 1, scale: 1 }}
                   className="text-center space-y-6"
                >
                   <div className="w-20 h-20 bg-emerald-50 text-emerald-600 rounded-full flex items-center justify-center mx-auto mb-4">
                      <ShieldCheck className="w-10 h-10" />
                   </div>
                   <h3 className="text-2xl font-bold text-slate-900">Verification Secure</h3>
                   <p className="text-slate-600 font-medium">Redirecting to forensic report...</p>
                </motion.div>
              ) : (
                <motion.div 
                  key="idle"
                  initial={{ opacity: 0 }}
                  animate={{ opacity: 1 }}
                  className="space-y-10"
                >
                   {error && (
                     <div className="p-4 bg-rose-50 border border-rose-100 rounded-xl flex items-center gap-3 text-rose-700 text-sm font-bold">
                        <AlertCircle className="w-5 h-5" />
                        {error}
                     </div>
                   )}

                   <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
                      <div className="space-y-3">
                         <p className="text-[10px] font-bold uppercase tracking-widest text-slate-400">Step 1: Identity Card</p>
                         <Dropzone 
                           label="Aadhaar / PAN Card" 
                           onFileSelect={setIdFile}
                           accept=".jpg,.jpeg,.png,.pdf"
                           icon={<SearchCode className="w-6 h-6" />}
                           className="h-[280px]"
                         />
                      </div>
                      <div className="space-y-3">
                         <p className="text-[10px] font-bold uppercase tracking-widest text-slate-400">Step 2: Biometric Photo</p>
                         <Dropzone 
                           label="Live Selfie Access" 
                           onFileSelect={setSelfieFile}
                           accept=".jpg,.jpeg,.png"
                           icon={<Fingerprint className="w-6 h-6" />}
                           className="h-[280px]"
                         />
                      </div>
                   </div>

                   <button
                     disabled={!idFile}
                     onClick={startVerification}
                     className="w-full bg-blue-600 hover:bg-blue-700 disabled:bg-slate-100 disabled:text-slate-300 disabled:cursor-not-allowed text-white font-bold py-4 rounded-xl transition-all shadow-lg shadow-blue-100 flex items-center justify-center gap-2"
                   >
                     <span>Run Verification Pipeline</span>
                     <ArrowRight className="w-4 h-4" />
                   </button>
                </motion.div>
              )}
           </AnimatePresence>
        </div>
      </div>
    </div>
  );
}

"use client";
import { useState } from 'react';
import axios from 'axios';
import { motion, AnimatePresence } from 'framer-motion';
import { ShieldCheck, User, Camera, ArrowRight, RefreshCcw } from 'lucide-react';
import Navbar from '@/components/Navbar';
import Dropzone from '@/components/Dropzone';
import StepProgress, { VerificationState } from '@/components/StepProgress';
import ResultCard from '@/components/ResultCard';

export default function Home() {
  const [idFile, setIdFile] = useState<File | null>(null);
  const [selfieFile, setSelfieFile] = useState<File | null>(null);
  const [status, setStatus] = useState<VerificationState>('idle');
  const [activeStep, setActiveStep] = useState(0);
  const [result, setResult] = useState<any>(null);

  const startVerification = async () => {
    if (!idFile) return;
    
    setStatus('processing');
    setActiveStep(0);
    setResult(null);

    const formData = new FormData();
    formData.append('id_card', idFile);
    if (selfieFile) formData.append('selfie', selfieFile);

    try {
      // Step simulation for better UX (Backend is fast on small images, but OCR takes time)
      // Since we don't have websockets, we simulate the 'active' feeling
      const stepInterval = setInterval(() => {
        setActiveStep((prev) => (prev < 3 ? prev + 1 : prev));
      }, 3000);

      const response = await axios.post('http://localhost:8000/verify', formData);
      
      clearInterval(stepInterval);
      setActiveStep(4);
      setResult(response.data.results);
      setStatus('completed');
    } catch (error) {
      console.error(error);
      setStatus('failed');
    }
  };

  const reset = () => {
    setIdFile(null);
    setSelfieFile(null);
    setStatus('idle');
    setResult(null);
    setActiveStep(0);
  };

  return (
    <main className="min-h-screen pt-24 pb-12 px-4 bg-slate-50/50">
      <Navbar />
      
      <div className="max-w-3xl mx-auto space-y-8">
        
        {/* Centric Header */}
        <div className="text-center space-y-3">
          <motion.div 
            initial={{ scale: 0.8, opacity: 0 }}
            animate={{ scale: 1, opacity: 1 }}
            className="inline-flex items-center justify-center p-3 bg-blue-600 rounded-2xl shadow-lg shadow-blue-200"
          >
            <ShieldCheck className="w-8 h-8 text-white" />
          </motion.div>
          <h1 className="text-4xl font-extrabold text-slate-900 tracking-tight">Identity Verification</h1>
          <p className="text-slate-500 max-w-md mx-auto">Upload your document and a selfie for real-time security analysis.</p>
        </div>

        <section className="glass-card p-8 rounded-[2.5rem] border border-white">
          <AnimatePresence mode="wait">
            
            {status === 'idle' && (
              <motion.div 
                key="upload-form"
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: -20 }}
                className="space-y-6"
              >
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  <div className="space-y-4">
                    <label className="text-sm font-bold text-slate-700 ml-1">1. Government ID</label>
                    <Dropzone 
                      label="Aadhaar / PAN Card" 
                      onFileSelect={setIdFile} 
                      icon={<ShieldCheck className="w-6 h-6" />}
                    />
                  </div>
                  <div className="space-y-4">
                    <label className="text-sm font-bold text-slate-700 ml-1">2. Live Selfie (Optional)</label>
                    <Dropzone 
                      label="Your Face Image" 
                      onFileSelect={setSelfieFile} 
                      icon={<Camera className="w-6 h-6" />}
                    />
                  </div>
                </div>

                <div className="pt-4">
                  <button
                    disabled={!idFile}
                    onClick={startVerification}
                    className="w-full bg-blue-600 hover:bg-blue-700 disabled:bg-slate-300 disabled:cursor-not-allowed text-white font-bold py-4 px-6 rounded-2xl transition-all shadow-xl shadow-blue-200 flex items-center justify-center space-x-2 group"
                  >
                    <span>Analyze Document</span>
                    <ArrowRight className="w-5 h-5 group-hover:translate-x-1 transition-transform" />
                  </button>
                </div>
              </motion.div>
            )}

            {status === 'processing' && (
              <motion.div 
                key="loading"
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                exit={{ opacity: 0 }}
                className="py-12"
              >
                <StepProgress activeStep={activeStep} status={status} />
              </motion.div>
            )}

            {status === 'completed' && result && (
              <motion.div 
                key="result"
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                className="space-y-8"
              >
                <ResultCard data={result} />
                
                <button
                  onClick={reset}
                  className="w-full py-4 rounded-2xl border border-slate-200 text-slate-600 font-bold hover:bg-slate-50 transition-colors flex items-center justify-center space-x-2"
                >
                  <RefreshCcw className="w-4 h-4" />
                  <span>Start New Verification</span>
                </button>
              </motion.div>
            )}

          </AnimatePresence>
        </section>

        {/* Footer info */}
        <div className="text-center text-xs text-slate-400 font-medium tracking-wide">
          <p>© 2026 CampusHub AI Labs. All data is processed locally.</p>
        </div>
      </div>
    </main>
  );
}

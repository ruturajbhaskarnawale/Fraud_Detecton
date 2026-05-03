"use client";
import { useState } from 'react';
import { AnimatePresence, motion } from 'framer-motion';
import { ArrowRight } from 'lucide-react';
import StepProgress from '@/components/StepProgress';
import { ErrorRecoveryPanel } from '@/components/ErrorRecoveryPanel';
import { useVerificationStore } from '@/stores/useVerificationStore';
import { useVerificationPipeline } from '@/hooks/useVerificationPipeline';
import { DocumentNode } from '@/components/verify/DocumentNode';
import { BiometricNode } from '@/components/verify/BiometricNode';
import { ProcessingOverlay } from '@/components/verify/ProcessingOverlay';
import { PipelineCompleted } from '@/components/verify/PipelineCompleted';

export default function VerifyPage() {
  const { 
    stage, 
    idFile, 
    selfieFile, 
    error, 
    setIdFile,
    setSelfieFile,
  } = useVerificationStore();

  const { activeStep, logs, startVerification, resetPipeline } = useVerificationPipeline();

  return (
    <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
      <div className="text-center space-y-4 mb-12">
        <h1 className="text-4xl font-black tracking-tighter uppercase">Identity Verification</h1>
        <p className="text-muted-foreground text-lg max-w-2xl mx-auto font-medium">Verify documents and biometrics with industrial-grade AI precision.</p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-12 gap-12 items-start">
        <div className="lg:col-span-4 bg-card border border-border p-10 rounded-[2.5rem] shadow-sm h-full">
           <h3 className="text-[10px] font-black uppercase tracking-[0.2em] text-muted-foreground mb-10 pb-4 border-b border-border/50">Pipeline Nodes</h3>
           <StepProgress activeStep={activeStep} status={stage === 'failed' ? 'failed' : stage === 'completed' ? 'completed' : stage === 'idle' ? 'idle' : 'processing'} />
        </div>

        <div className="lg:col-span-8 bg-card border border-border p-12 rounded-[2.5rem] shadow-xl min-h-[640px] flex flex-col justify-center">
           <AnimatePresence mode="wait">
              {['uploading', 'ocr', 'face', 'liveness', 'forensics', 'fraud', 'fusing'].includes(stage) ? (
                <ProcessingOverlay key="processing" logs={logs} />
              ) : stage === 'completed' ? (
                <PipelineCompleted key="completed" />
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
                      <DocumentNode idFile={idFile} setIdFile={setIdFile} />
                      <BiometricNode selfieFile={selfieFile} setSelfieFile={setSelfieFile} />
                   </div>

                   <button
                     disabled={!idFile || !selfieFile}
                     onClick={startVerification}
                     className="w-full bg-foreground hover:opacity-90 text-background disabled:bg-secondary disabled:text-muted-foreground disabled:cursor-not-allowed font-black text-[10px] uppercase tracking-[0.3em] py-6 rounded-[2rem] transition-all shadow-xl flex items-center justify-center gap-3"
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

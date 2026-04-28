"use client";
import React from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { CheckCircle2, Circle, Clock, Loader2, Shield, Scan, Fingerprint, Search, Zap, Activity } from 'lucide-react';
import { cn } from '@/lib/utils';

export type VerificationState = 'idle' | 'processing' | 'completed' | 'failed' | 'abstain' | 'review';

interface StepProgressProps {
  activeStep: number;
  status: VerificationState;
}

const steps = [
  { id: 1, name: 'Secure Ingestion', desc: 'Receiving encrypted assets', icon: Zap },
  { id: 2, name: 'Identity Extraction', desc: 'OCR & Document Parsing', icon: Scan },
  { id: 3, name: 'Biometric Scaling', desc: 'Face & Liveness Matching', icon: Fingerprint },
  { id: 4, name: 'Forensic Audit', desc: 'U-Net Tamper Detection', icon: Search },
  { id: 5, name: 'Network Intelligence', desc: 'Graph-based Fraud Check', icon: Activity },
  { id: 6, name: 'Risk Model Fusion', desc: 'Final Probabilistic Decision', icon: Shield },
];

export default function StepProgress({ activeStep, status }: StepProgressProps) {
  return (
    <div className="relative space-y-8">
      {/* Connector Line */}
      <div className="absolute left-[23px] top-6 bottom-6 w-[2px] bg-slate-800 -z-10" />

      <div className="space-y-7">
        {steps.map((step, index) => {
          const isCompleted = activeStep > index;
          const isActive = activeStep === index && status !== 'completed';
          const isFullComplete = status === 'completed';
          const Icon = step.icon;

          return (
            <div 
              key={step.id} 
              className="flex items-start gap-5 relative group"
            >
              <div className="relative flex-shrink-0">
                <div className={cn(
                  "w-12 h-12 rounded-2xl flex items-center justify-center transition-all duration-300 border-2",
                  (isCompleted || (index === steps.length - 1 && isFullComplete)) ? "bg-emerald-900/20 text-emerald-400 border-emerald-500/20" : 
                  isActive ? "bg-blue-600 text-white border-blue-500 shadow-xl shadow-blue-900/50 scale-110" :
                  "bg-slate-900 text-slate-600 border-slate-800"
                )}>
                  {(isCompleted || (index === steps.length - 1 && isFullComplete)) ? <CheckCircle2 className="w-6 h-6" /> : 
                   isActive ? <Loader2 className="w-6 h-6 animate-spin" /> : 
                   <Icon className="w-5 h-5" />
                  }
                </div>
              </div>

              <div className="pt-1.5">
                <h4 className={cn(
                  "text-xs font-black tracking-widest uppercase transition-colors",
                  (isCompleted || (index === steps.length - 1 && isFullComplete)) ? "text-emerald-400" : 
                  isActive ? "text-blue-400" :
                  "text-slate-500"
                )}>
                  {step.name}
                </h4>
                <p className="text-[10px] font-bold text-slate-400 mt-1">{step.desc}</p>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}

"use client";
import React from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { CheckCircle2, Circle, Clock, Loader2 } from 'lucide-react';
import { cn } from '@/lib/utils';

export type VerificationState = 'idle' | 'processing' | 'completed' | 'failed';

interface StepProgressProps {
  activeStep: number;
  status: VerificationState;
}

const steps = [
  { id: 1, name: 'Upload Assets', desc: 'Securely receiving documents' },
  { id: 2, name: 'Content Extraction', desc: 'Processing identity data' },
  { id: 3, name: 'Face Correlation', desc: 'Matching biometric signals' },
  { id: 4, name: 'Final Report', desc: 'Compiling verification results' },
];

export default function StepProgress({ activeStep, status }: StepProgressProps) {
  return (
    <div className="relative space-y-8">
      {/* Simple Connector Line */}
      <div className="absolute left-[19px] top-6 bottom-6 w-[2px] bg-slate-100 -z-10" />

      <div className="space-y-6">
        {steps.map((step, index) => {
          const isCompleted = activeStep > index;
          const isActive = activeStep === index && status !== 'completed';
          const isPending = activeStep < index;
          const isFullComplete = status === 'completed';

          return (
            <div 
              key={step.id} 
              className="flex items-start gap-5 relative group"
            >
              <div className="relative flex-shrink-0">
                <div className={cn(
                  "w-10 h-10 rounded-xl flex items-center justify-center transition-all duration-300 border-2",
                  (isCompleted || (index === 3 && isFullComplete)) ? "bg-emerald-50 text-emerald-600 border-emerald-100" : 
                  isActive ? "bg-blue-600 text-white border-blue-600 shadow-lg shadow-blue-100" :
                  "bg-white text-slate-300 border-slate-100"
                )}>
                  {(isCompleted || (index === 3 && isFullComplete)) ? <CheckCircle2 className="w-5 h-5" /> : 
                   isActive ? <Loader2 className="w-5 h-5 animate-spin" /> : 
                   <span className="text-xs font-bold">{step.id}</span>
                  }
                </div>
              </div>

              <div className="pt-0.5">
                <h4 className={cn(
                  "text-sm font-bold tracking-tight transition-colors",
                  (isCompleted || (index === 3 && isFullComplete)) ? "text-emerald-700" : 
                  isActive ? "text-blue-600" :
                  "text-slate-400"
                )}>
                  {step.name}
                </h4>
                <p className="text-xs font-medium text-slate-700 mt-0.5">{step.desc}</p>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}

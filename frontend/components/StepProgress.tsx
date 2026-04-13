"use client";
import { motion } from 'framer-motion';
import { Check, Loader2, Circle } from 'lucide-react';
import { cn } from '@/lib/utils';

export type VerificationState = 'idle' | 'processing' | 'completed' | 'failed';

interface Step {
  id: string;
  name: string;
  description: string;
}

const STEPS: Step[] = [
  { id: 'ocr', name: 'Document Reading', description: 'Extracting data via OCR...' },
  { id: 'fraud', name: 'Fraud Analysis', description: 'Checking for tampering...' },
  { id: 'face', name: 'Identity Matching', description: 'Comparing face embeddings...' },
  { id: 'score', name: 'Risk Scoring', description: 'Generating final decision...' },
];

interface StepProgressProps {
  activeStep: number;
  status: VerificationState;
}

export default function StepProgress({ activeStep, status }: StepProgressProps) {
  if (status === 'idle') return null;

  return (
    <div className="w-full space-y-4">
      {STEPS.map((step, index) => {
        const isActive = index === activeStep;
        const isCompleted = index < activeStep || status === 'completed';
        const isPending = index > activeStep;

        return (
          <motion.div 
            key={step.id}
            initial={{ opacity: 0, x: -20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: index * 0.1 }}
            className={cn(
              "flex items-center space-x-4 p-4 rounded-xl border transition-all duration-300",
              isActive ? "bg-blue-50 border-blue-200 shadow-sm" : "bg-white border-slate-100",
              isCompleted ? "opacity-100" : "opacity-60"
            )}
          >
            <div className={cn(
              "w-8 h-8 rounded-full flex items-center justify-center transition-colors",
              isCompleted ? "bg-green-500 text-white" : isActive ? "bg-blue-500 text-white" : "bg-slate-100 text-slate-400"
            )}>
              {isCompleted ? <Check className="w-5 h-5" /> : isActive ? <Loader2 className="w-5 h-5 animate-spin" /> : <Circle className="w-4 h-4" />}
            </div>
            
            <div className="flex-1">
              <p className={cn(
                "font-semibold text-sm",
                isActive ? "text-blue-700" : "text-slate-900"
              )}>{step.name}</p>
              {isActive && (
                <p className="text-xs text-blue-500 animate-pulse mt-0.5">{step.description}</p>
              )}
            </div>
          </motion.div>
        );
      })}
    </div>
  );
}

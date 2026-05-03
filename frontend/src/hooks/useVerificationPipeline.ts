import { useState } from 'react';
import { useRouter } from 'next/navigation';
import { verificationService } from '@/services/api';
import { useVerificationStore } from '@/stores/useVerificationStore';
import { useSessionStore } from '@/stores/useSessionStore';
import { useResultStore } from '@/stores/useResultStore';

const progressMessages = [
  "Establishing secure connection to AI nodes...",
  "Extracting OCR & Identity Metadata...",
  "Matching Biometrics & Liveness signals...",
  "Auditing pixel-level Forensic signatures...",
  "Consulting Fraud Graph Intelligence...",
  "Fusing signals into final Risk Score..."
];

export function useVerificationPipeline() {
  const router = useRouter();
  
  const { 
    idFile, 
    selfieFile, 
    setStage, 
    setError, 
    reset: resetStore 
  } = useVerificationStore();
  
  const metadata = useSessionStore((state) => state.metadata);
  const setLastResult = useResultStore((state) => state.setLastResult);

  const [activeStep, setActiveStep] = useState(0);
  const [logs, setLogs] = useState<string[]>([]);

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

  return {
    activeStep,
    logs,
    startVerification,
    resetPipeline
  };
}

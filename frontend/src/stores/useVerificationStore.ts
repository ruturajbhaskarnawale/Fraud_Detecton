import { create } from 'zustand';
import { persist, createJSONStorage } from 'zustand/middleware';

export type PipelineStage = 
  | 'idle' 
  | 'uploading' 
  | 'ocr' 
  | 'face' 
  | 'liveness' 
  | 'forensics' 
  | 'fraud' 
  | 'fusing' 
  | 'completed' 
  | 'failed';

interface VerificationState {
  stage: PipelineStage;
  progress: number;
  error: string | null;
  idFile: File | null;
  selfieFile: File | null;
  
  setStage: (stage: PipelineStage) => void;
  setProgress: (progress: number) => void;
  setError: (error: string | null) => void;
  setIdFile: (file: File | null) => void;
  setSelfieFile: (file: File | null) => void;
  setFiles: (idFile: File | null, selfieFile: File | null) => void;
  reset: () => void;
}

export const useVerificationStore = create<VerificationState>()(
  persist(
    (set) => ({
      stage: 'idle',
      progress: 0,
      error: null,
      idFile: null,
      selfieFile: null,

      setStage: (stage) => set({ stage }),
      setProgress: (progress) => set({ progress }),
      setError: (error) => set({ error }),
      setIdFile: (idFile) => set({ idFile }),
      setSelfieFile: (selfieFile) => set({ selfieFile }),
      setFiles: (idFile, selfieFile) => set({ idFile, selfieFile }),
      reset: () => set({ stage: 'idle', progress: 0, error: null, idFile: null, selfieFile: null }),
    }),
    {
      name: 'veridex-verification-storage',
      storage: createJSONStorage(() => localStorage),
      // Only persist metadata, not the File objects which are large and non-serializable
      partialize: (state) => ({ 
        stage: state.stage, 
        error: state.error,
        progress: state.progress 
      }),
    }
  )
);

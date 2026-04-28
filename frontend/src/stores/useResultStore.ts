import { create } from 'zustand';
import { persist, createJSONStorage } from 'zustand/middleware';
import { VerifyResponse } from '@/services/api/types';

interface ResultState {
  lastResult: VerifyResponse | null;
  history: VerifyResponse[];
  
  setLastResult: (result: VerifyResponse) => void;
  setHistory: (history: VerifyResponse[]) => void;
  clearResults: () => void;
}

export const useResultStore = create<ResultState>()(
  persist(
    (set) => ({
      lastResult: null,
      history: [],

      setLastResult: (result) => set({ lastResult: result }),
      setHistory: (history) => set({ history }),
      clearResults: () => set({ lastResult: null }),
    }),
    {
      name: 'veridex-result-storage',
      storage: createJSONStorage(() => localStorage),
    }
  )
);

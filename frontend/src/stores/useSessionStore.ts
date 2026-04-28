import { create } from 'zustand';
import { persist, createJSONStorage } from 'zustand/middleware';
import { v4 as uuidv4 } from 'uuid';
import { VerificationMetadata } from '@/services/api/types';

interface SessionState {
  metadata: VerificationMetadata | null;
  initializeSession: () => void;
  getMetadata: () => VerificationMetadata | null;
  refreshSession: () => void;
}

export const useSessionStore = create<SessionState>()(
  persist(
    (set, get) => ({
      metadata: null,

      initializeSession: () => {
        if (typeof window === 'undefined') return;

        const currentMetadata = get().metadata;
        
        let deviceId = localStorage.getItem('veridex_device_id');
        if (!deviceId) {
          deviceId = uuidv4();
          localStorage.setItem('veridex_device_id', deviceId);
        }

        // If metadata already exists (from persistence), we keep the device_id but can update other fields
        const metadata: VerificationMetadata = {
          device_id: deviceId,
          session_id: currentMetadata?.session_id || uuidv4(),
          user_agent: navigator.userAgent,
          timezone: Intl.DateTimeFormat().resolvedOptions().timeZone,
          resolution: `${window.innerWidth}x${window.innerHeight}`,
          language: navigator.language,
        };

        set({ metadata });
      },

      refreshSession: () => {
        const current = get().metadata;
        if (current) {
          set({
            metadata: {
              ...current,
              session_id: uuidv4() // New session ID for a new attempt
            }
          });
        }
      },

      getMetadata: () => {
        return get().metadata;
      },
    }),
    {
      name: 'veridex-session-storage',
      storage: createJSONStorage(() => localStorage),
    }
  )
);

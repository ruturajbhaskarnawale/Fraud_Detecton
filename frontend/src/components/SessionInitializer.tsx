"use client";
import { useEffect } from 'react';
import { useSessionStore } from '@/stores/useSessionStore';

export function SessionInitializer({ children }: { children: React.ReactNode }) {
  const initializeSession = useSessionStore((state) => state.initializeSession);

  useEffect(() => {
    initializeSession();
  }, [initializeSession]);

  return <>{children}</>;
}

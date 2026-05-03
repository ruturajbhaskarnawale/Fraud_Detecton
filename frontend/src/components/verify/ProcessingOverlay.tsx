import { motion } from 'framer-motion';
import { Activity } from 'lucide-react';
import { cn } from '@/lib/utils';

interface ProcessingOverlayProps {
  logs: string[];
}

export function ProcessingOverlay({ logs }: ProcessingOverlayProps) {
  return (
    <motion.div 
      key="processing"
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      exit={{ opacity: 0 }}
      className="space-y-12 text-center"
    >
       <div className="relative w-40 h-40 mx-auto">
          <div className="absolute inset-0 border-8 border-blue-900/30 rounded-full" />
          <div className="absolute inset-0 border-8 border-blue-600 rounded-full border-t-transparent animate-spin" />
          <div className="absolute inset-0 flex items-center justify-center bg-slate-800 rounded-full m-2 shadow-inner">
             <Activity className="w-12 h-12 text-blue-500" />
          </div>
       </div>
       
       <div className="space-y-6">
          <h3 className="text-3xl font-black text-white uppercase tracking-tight">Neural Processing</h3>
          <div className="max-w-xs mx-auto space-y-3">
            {logs.map((log, i) => (
               <p key={i} className={cn(
                 "text-[11px] font-black uppercase tracking-widest transition-all",
                 i === logs.length - 1 ? "text-blue-400" : "text-slate-600"
               )}>{log}</p>
            ))}
          </div>
       </div>
    </motion.div>
  );
}

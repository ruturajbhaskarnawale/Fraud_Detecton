import { motion } from 'framer-motion';
import { ShieldCheck } from 'lucide-react';

export function PipelineCompleted() {
  return (
    <motion.div 
       key="completed"
       initial={{ opacity: 0, scale: 0.9 }}
       animate={{ opacity: 1, scale: 1 }}
       className="text-center space-y-8"
    >
       <div className="w-24 h-24 bg-emerald-900/20 text-emerald-400 border border-emerald-500/20 rounded-[2rem] flex items-center justify-center mx-auto mb-4 shadow-xl">
          <ShieldCheck className="w-12 h-12" />
       </div>
       <div className="space-y-2">
         <h3 className="text-3xl font-black text-white uppercase tracking-tight">Audit Certified</h3>
         <p className="text-slate-500 font-bold uppercase text-[10px] tracking-[0.2em]">Redirecting to forensic report...</p>
       </div>
    </motion.div>
  );
}

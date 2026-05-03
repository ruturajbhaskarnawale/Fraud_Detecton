import { AlertTriangle, ShieldCheck } from 'lucide-react';

export function CriticalFlagsPanel({ flags }: { flags: string[] }) {
  return (
    <div className="bg-slate-900 border border-slate-800 rounded-[2.5rem] p-8 shadow-xl space-y-6">
      <h3 className="text-xs font-black text-white uppercase tracking-widest flex items-center gap-2">
        <AlertTriangle className="w-4 h-4 text-rose-500" /> Critical Red Flags
      </h3>
      <div className="space-y-3">
        {flags && flags.length > 0 ? (
          flags.map((factor, i) => (
            <div key={i} className="flex gap-4 items-center p-4 bg-rose-900/20 rounded-2xl border border-rose-900/50">
              <div className="w-2 h-2 rounded-full bg-rose-500 animate-pulse" />
              <p className="text-[11px] font-black text-rose-400 uppercase tracking-tight">
                {factor.replace(/_/g, ' ')}
              </p>
            </div>
          ))
        ) : (
          <div className="text-center py-6 space-y-3">
            <ShieldCheck className="w-8 h-8 text-emerald-500 mx-auto opacity-50" />
            <p className="text-[10px] font-bold text-slate-500 uppercase tracking-widest italic">
              No adverse signals detected.
            </p>
          </div>
        )}
      </div>
    </div>
  );
}

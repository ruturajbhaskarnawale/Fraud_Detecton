import { Clock, History, AlertTriangle, CheckCircle2, ShieldAlert } from 'lucide-react';
import { VerifyResponse } from '@/services/api';
import { cn } from '@/lib/utils';

export function AuditTimeline({ data }: { data: VerifyResponse }) {
  const { history, errors } = data;

  if (!history?.length && !errors?.length) return null;

  return (
    <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 pt-10 border-t border-slate-800">
      {/* Decision History */}
      <div className="bg-slate-900 border border-slate-800 rounded-3xl p-8 space-y-6 shadow-xl">
        <div className="flex items-center gap-3 border-b border-slate-800 pb-4">
          <History className="w-5 h-5 text-blue-500" />
          <h3 className="text-sm font-black uppercase tracking-widest text-white">Decision Lifecycle</h3>
        </div>
        
        <div className="space-y-6 relative before:absolute before:left-[11px] before:top-2 before:bottom-2 before:w-[1px] before:bg-slate-800">
          {history?.map((item, idx) => (
            <div key={idx} className="relative pl-10 flex flex-col gap-1">
              <div className={cn(
                "absolute left-0 top-1.5 w-6 h-6 rounded-full flex items-center justify-center border-4 border-slate-900 shadow-sm z-10",
                item.decision === 'ACCEPT' ? "bg-emerald-500" : item.decision === 'REJECT' ? "bg-rose-500" : "bg-amber-500"
              )}>
                {item.decision === 'ACCEPT' ? <CheckCircle2 className="w-3 h-3 text-white" /> : <ShieldAlert className="w-3 h-3 text-white" />}
              </div>
              <div className="flex justify-between items-center">
                <span className="text-xs font-black text-white uppercase tracking-tight">{item.decision}</span>
                <span className="text-[10px] font-mono text-slate-500">{new Date(item.at).toLocaleTimeString()}</span>
              </div>
              <p className="text-[10px] font-bold text-slate-400 uppercase tracking-widest">Actor: {item.actor}</p>
            </div>
          ))}
          {!history?.length && <p className="text-xs text-slate-500 italic pl-10">Initial state record.</p>}
        </div>
      </div>

      {/* System Errors / Module Logs */}
      <div className="bg-slate-950 border border-slate-800 rounded-3xl p-8 space-y-6 shadow-xl">
        <div className="flex items-center gap-3 border-b border-slate-800 pb-4">
          <AlertTriangle className="w-5 h-5 text-amber-500" />
          <h3 className="text-sm font-black uppercase tracking-widest text-white">System Diagnostics</h3>
        </div>

        <div className="space-y-4 max-h-[300px] overflow-y-auto pr-2 custom-scrollbar">
          {errors && errors.length > 0 ? (
            errors.map((err, idx) => (
              <div key={idx} className="p-4 bg-slate-900 rounded-2xl border border-amber-500/20 space-y-2">
                <div className="flex justify-between items-center">
                  <span className="text-[10px] font-black text-amber-500 uppercase tracking-widest">{err.module}</span>
                  <span className="text-[9px] font-mono text-slate-600">{new Date(err.at).toLocaleTimeString()}</span>
                </div>
                <p className="text-xs font-medium text-slate-300 leading-relaxed">{err.message}</p>
              </div>
            ))
          ) : (
            <div className="flex flex-col items-center justify-center py-10 text-center space-y-3">
              <CheckCircle2 className="w-8 h-8 text-emerald-500/30" />
              <p className="text-xs font-bold text-slate-600 uppercase tracking-widest">All Modules Operational</p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

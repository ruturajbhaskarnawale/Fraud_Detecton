import { AnimatePresence, motion } from 'framer-motion';
import { AlertCircle, ChevronRight, Database, ShieldCheck } from 'lucide-react';
import Link from 'next/link';
import { cn } from '@/lib/utils';
import { VerifyResponse } from '@/services/api';

export interface RecentActivityListProps {
  loading: boolean;
  data: VerifyResponse[];
}

export function RecentActivityList({ loading, data }: RecentActivityListProps) {
  return (
    <div className="bg-card border border-border rounded-2xl p-6 shadow-xl overflow-hidden flex flex-col">
      <div className="flex justify-between items-center mb-6">
        <h3 className="font-bold text-foreground">Recent Activity</h3>
        <Link href="/history" className="text-xs font-bold text-blue-500 hover:text-blue-600">View All</Link>
      </div>
      <div className="space-y-4 overflow-y-auto max-h-[300px] flex-1">
        {loading ? (
          <div className="space-y-4">
            {[1, 2].map(i => (
              <div key={i} className="flex gap-4 items-center p-3">
                <div className="w-10 h-10 bg-secondary rounded-lg animate-pulse"/>
                <div className="space-y-2 flex-1">
                  <div className="h-4 bg-secondary rounded animate-pulse w-3/4"/>
                  <div className="h-3 bg-secondary/50 rounded animate-pulse w-1/2"/>
                </div>
              </div>
            ))}
          </div>
        ) : (
          <AnimatePresence mode="popLayout">
            {data.slice(0, 10).map((record) => (
              <motion.div 
                key={record.tracking_id} 
                layout 
                initial={{ opacity: 0, x: -10 }} 
                animate={{ opacity: 1, x: 0 }} 
                exit={{ opacity: 0, scale: 0.95 }}
              >
                <Link href={`/results/${record.tracking_id}`} className="flex items-center justify-between p-3 rounded-xl hover:bg-secondary transition-colors group">
                  <div className="flex items-center gap-3">
                    <div className={cn(
                      "w-10 h-10 rounded-lg flex items-center justify-center", 
                      record.decision === 'ACCEPT' ? "bg-emerald-500/10 text-emerald-500 border border-emerald-500/20" : "bg-rose-500/10 text-rose-500 border border-rose-500/20"
                    )}>
                      {record.decision === 'ACCEPT' ? <ShieldCheck className="w-5 h-5" /> : <AlertCircle className="w-5 h-5" />}
                    </div>
                    <div className="min-w-0">
                      <p className="text-sm font-bold text-foreground truncate">Forensic Audit</p>
                      <p className="text-[10px] font-medium text-muted-foreground uppercase tracking-tight">#{record.tracking_id.slice(0, 8)}</p>
                    </div>
                  </div>
                  <ChevronRight className="w-4 h-4 text-muted-foreground group-hover:text-foreground transition-colors" />
                </Link>
              </motion.div>
            ))}
            {data.length === 0 && (
              <div className="py-12 text-center text-muted-foreground opacity-50">
                <Database className="w-8 h-8 mx-auto mb-2" />
                <p className="text-xs font-bold">No records found.</p>
              </div>
            )}
          </AnimatePresence>
        )}
      </div>
    </div>
  );
}

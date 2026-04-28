"use client";
import { useEffect, useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { 
  BarChart3, 
  TrendingUp, 
  ShieldCheck, 
  AlertCircle, 
  Clock, 
  Activity,
  Download,
  ChevronRight,
  Database,
} from 'lucide-react';
import { verificationService } from '@/services/api';
import { cn } from '@/lib/utils';
import Link from 'next/link';
import { useResultStore } from '@/stores/useResultStore';
import { DashboardCardSkeleton } from '@/components/Skeleton';

export default function DashboardPage() {
  const { history: data, setHistory } = useResultStore();
  const [loading, setLoading] = useState(data.length === 0);
  const [filter, setFilter] = useState('ALL');

  useEffect(() => {
    const fetchData = async () => {
      try {
        const records = await verificationService.getHistory();
        setHistory(records);
      } catch (err) {
        console.error("Dashboard data load failed:", err);
      } finally {
        setLoading(false);
      }
    };
    fetchData();
  }, [setHistory]);

  const total = data.length;
  const verified = data.filter(r => r.decision === 'ACCEPT').length;
  const suspicious = data.filter(r => r.decision === 'REJECT' || r.decision === 'ABSTAIN').length;
  
  const successRate = total > 0 ? ((verified / total) * 100).toFixed(1) : "0.0";
  const fraudPrevention = total > 0 ? ((suspicious / total) * 100).toFixed(1) : "0.0";

  const filteredData = data.filter(r => {
    if (filter === 'ALL') return true;
    if (filter === 'RISK') return r.decision !== 'ACCEPT';
    return r.decision === filter;
  });

  const handleExportCSV = () => {
    if (data.length === 0) return;
    const headers = ['Tracking ID', 'Decision', 'Risk Score', 'Timestamp'];
    const csvContent = [
      headers.join(','),
      ...data.map(r => [r.tracking_id, r.decision, r.risk_score, r.timestamp].join(','))
    ].join('\n');
    const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
    const url = URL.createObjectURL(blob);
    const link = document.createElement("a");
    link.setAttribute("href", url);
    link.setAttribute("download", `Veridex_Audit_Log_${new Date().toISOString().split('T')[0]}.csv`);
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  return (
    <div className="space-y-8 max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <h1 className="text-3xl font-bold text-white tracking-tight">Analytics Dashboard</h1>
          <p className="text-slate-400 mt-1">Real-time identity verification metrics and logs.</p>
        </div>
        
        <div className="flex items-center gap-3">
           <div className="flex bg-slate-900 border border-slate-800 rounded-lg p-1 shadow-sm">
              {['ALL', 'ACCEPT', 'RISK'].map((f) => (
                <button
                  key={f}
                  onClick={() => setFilter(f)}
                  className={cn(
                    "px-3 py-1.5 text-xs font-bold rounded-md transition-all uppercase tracking-tight",
                    filter === f ? "bg-slate-800 text-white shadow-sm" : "text-slate-500 hover:text-white"
                  )}
                >
                  {f}
                </button>
              ))}
           </div>
           <button onClick={handleExportCSV} className="inline-flex items-center gap-2 px-4 py-2.5 bg-slate-800 border border-slate-700 rounded-lg text-sm font-bold text-white hover:bg-slate-700 transition-colors shadow-sm">
              <Download className="w-4 h-4" />
              <span>Export CSV</span>
           </button>
        </div>
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
         {loading ? (
           <>
             <DashboardCardSkeleton />
             <DashboardCardSkeleton />
             <DashboardCardSkeleton />
             <DashboardCardSkeleton />
           </>
         ) : (
           <>
             <MetricCard label="Total Scans" value={total.toLocaleString()} trend="+12.5%" trendUp={true} icon={<Activity className="w-5 h-5" />} isActive={filter === 'ALL'} onClick={() => setFilter('ALL')} />
             <MetricCard label="Verification Rate" value={`${successRate}%`} trend="+0.4%" trendUp={true} icon={<ShieldCheck className="w-5 h-5" />} color="blue" isActive={filter === 'ACCEPT'} onClick={() => setFilter('ACCEPT')} />
             <MetricCard label="Fraud Prevented" value={`${fraudPrevention}%`} trend="+5.2%" trendUp={false} icon={<AlertCircle className="w-5 h-5" />} color="rose" isActive={filter === 'RISK'} onClick={() => setFilter('RISK')} />
             <MetricCard label="Avg Latency" value="1.8s" trend="-0.4s" trendUp={true} icon={<Clock className="w-5 h-5" />} />
           </>
         )}
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
         <div className="lg:col-span-2 bg-slate-900 border border-slate-800 rounded-2xl p-6 shadow-xl">
            <div className="flex justify-between items-center mb-6">
               <h3 className="font-bold text-white">Scan Volume Trends</h3>
               <div className="flex gap-4 text-xs font-semibold text-slate-400">
                  <span className="flex items-center gap-1.5"><div className="w-2 h-2 bg-blue-500 rounded-full"/> Valid</span>
                  <span className="flex items-center gap-1.5"><div className="w-2 h-2 bg-rose-500 rounded-full"/> Risk</span>
               </div>
            </div>
            <div className="h-64 w-full flex items-end justify-between gap-3 pt-4">
               {[0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11].map((i) => (
                 <div key={i} className="flex-1 flex flex-col items-center gap-2 h-full">
                    <div className="w-full flex flex-col-reverse h-full bg-slate-800 rounded-md overflow-hidden">
                       <div className="bg-blue-500 w-full" style={{ height: `${[45, 52, 38, 65, 48, 55, 72, 60, 42, 58, 68, 50][i]}%` }} />
                       <div className="bg-rose-500 w-full" style={{ height: `${[8, 12, 5, 15, 10, 8, 12, 11, 7, 9, 14, 8][i]}%` }} />
                    </div>
                 </div>
               ))}
            </div>
         </div>

         <div className="bg-slate-900 border border-slate-800 rounded-2xl p-6 shadow-xl overflow-hidden flex flex-col">
            <div className="flex justify-between items-center mb-6">
               <h3 className="font-bold text-white">Recent Activity</h3>
               <Link href="/history" className="text-xs font-bold text-blue-600 hover:text-blue-700">View All</Link>
            </div>
            <div className="space-y-4 overflow-y-auto max-h-[300px] flex-1">
               {loading ? (
                 <div className="space-y-4">
                    <div className="flex gap-4 items-center p-3"><div className="w-10 h-10 bg-slate-100 rounded-lg animate-pulse"/><div className="space-y-2 flex-1"><div className="h-4 bg-slate-100 rounded animate-pulse w-3/4"/><div className="h-3 bg-slate-50 rounded animate-pulse w-1/2"/></div></div>
                    <div className="flex gap-4 items-center p-3"><div className="w-10 h-10 bg-slate-100 rounded-lg animate-pulse"/><div className="space-y-2 flex-1"><div className="h-4 bg-slate-100 rounded animate-pulse w-3/4"/><div className="h-3 bg-slate-50 rounded animate-pulse w-1/2"/></div></div>
                 </div>
               ) : (
                 <AnimatePresence mode="popLayout">
                   {filteredData.slice(0, 10).map((record) => (
                     <motion.div key={record.tracking_id} layout initial={{ opacity: 0, x: -10 }} animate={{ opacity: 1, x: 0 }} exit={{ opacity: 0, scale: 0.95 }}>
                       <Link href={`/results/${record.tracking_id}`} className="flex items-center justify-between p-3 rounded-xl hover:bg-slate-800 transition-colors group">
                          <div className="flex items-center gap-3">
                             <div className={cn("w-10 h-10 rounded-lg flex items-center justify-center", record.decision === 'ACCEPT' ? "bg-emerald-900/20 text-emerald-400 border border-emerald-500/20" : "bg-rose-900/20 text-rose-400 border border-rose-500/20")}>
                                {record.decision === 'ACCEPT' ? <ShieldCheck className="w-5 h-5" /> : <AlertCircle className="w-5 h-5" />}
                             </div>
                             <div className="min-w-0">
                                <p className="text-sm font-bold text-white truncate">Forensic Audit</p>
                                <p className="text-[10px] font-medium text-slate-500 uppercase tracking-tight">#{record.tracking_id.slice(0, 8)}</p>
                             </div>
                          </div>
                          <ChevronRight className="w-4 h-4 text-slate-300 group-hover:text-slate-400" />
                       </Link>
                     </motion.div>
                   ))}
                   {filteredData.length === 0 && (
                     <div className="py-12 text-center text-slate-400 opacity-50"><Database className="w-8 h-8 mx-auto mb-2" /><p className="text-xs font-bold">No records found.</p></div>
                   )}
                 </AnimatePresence>
               )}
            </div>
         </div>
      </div>
    </div>
  );
}

function MetricCard({ label, value, trend, trendUp, icon, isActive, onClick }: any) {
  return (
    <button onClick={onClick} className={cn("bg-slate-900 border p-6 rounded-2xl shadow-xl transition-all text-left group w-full", isActive ? "border-blue-500 ring-1 ring-blue-500" : "border-slate-800 hover:border-slate-700")}>
      <div className="flex justify-between items-start mb-4">
        <div className={cn("p-2 rounded-lg transition-colors", isActive ? "bg-slate-800 text-blue-400" : "bg-slate-800/50 text-slate-500 group-hover:text-slate-300")}>{icon}</div>
        <div className={cn("flex items-center gap-1 text-[10px] font-bold px-2 py-0.5 rounded-full border", trendUp ? "bg-emerald-900/20 text-emerald-400 border-emerald-500/20" : "bg-rose-900/20 text-rose-400 border-rose-500/20")}>
           {trendUp ? <TrendingUp className="w-3 h-3" /> : <AlertCircle className="w-3 h-3" />}
           {trend}
        </div>
      </div>
      <div><p className="text-sm font-medium text-slate-500 mb-1">{label}</p><div className="text-2xl font-bold text-white">{value}</div></div>
    </button>
  );
}

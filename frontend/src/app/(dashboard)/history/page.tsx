"use client";
import { useEffect, useState } from 'react';
import Link from 'next/link';
import { motion, AnimatePresence } from 'framer-motion';
import { 
  Search, 
  ChevronRight, 
  Clock, 
  Filter, 
  ShieldCheck, 
  Activity,
  SearchCode,
  ShieldAlert
} from 'lucide-react';
import { useRouter } from 'next/navigation';
import { verificationService, Verdict } from '@/services/api';
import { cn } from '@/lib/utils';
import { useResultStore } from '@/stores/useResultStore';
import { HistoryRowSkeleton } from '@/components/Skeleton';

export default function HistoryPage() {
  const router = useRouter();
  const { history: records, setHistory } = useResultStore();
  
  const [loading, setLoading] = useState(records.length === 0);
  const [error, setError] = useState<string | null>(null);
  const [searchTerm, setSearchTerm] = useState("");
  const [activeFilter, setActiveFilter] = useState<Verdict | 'ALL'>('ALL');

  useEffect(() => {
    const fetchRecords = async () => {
      try {
        const data = await verificationService.getHistory();
        setHistory(data);
      } catch (err: any) {
        console.error("Failed to fetch records:", err);
        setError("Network connection failed. Unable to retrieve encrypted audit logs.");
      } finally {
        setLoading(false);
      }
    };
    fetchRecords();
  }, [setHistory]);

  const stats = {
    total: records.length,
    accept: records.filter(r => r.decision === 'ACCEPT').length,
    reject: records.filter(r => r.decision === 'REJECT').length,
    review: records.filter(r => r.decision === 'REVIEW').length
  };

  const filteredRecords = records.filter(r => {
    const matchesSearch = 
      r.tracking_id?.toLowerCase().includes(searchTerm.toLowerCase()) ||
      r.top_factors?.some(f => f.toLowerCase().includes(searchTerm.toLowerCase()));
    
    if (activeFilter === 'ALL') return matchesSearch;
    return matchesSearch && r.decision === activeFilter;
  });

  return (
    <div className="space-y-10 max-w-7xl mx-auto py-10 px-4">
      {/* Header & Stats */}
      <div className="flex flex-col md:flex-row justify-between items-start md:items-end gap-6">
        <div className="space-y-2">
          <h1 className="text-4xl font-black text-white tracking-tight">Audit History</h1>
          <p className="text-slate-400 font-medium">Immutable forensic ledger of all verification attempts.</p>
        </div>
        
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-4 w-full md:w-auto">
          <StatBox label="Total Audits" value={stats.total} color="slate" />
          <StatBox label="Accepted" value={stats.accept} color="emerald" />
          <StatBox label="Rejected" value={stats.reject} color="rose" />
          <StatBox label="Review" value={stats.review} color="amber" />
        </div>
      </div>

      {/* Search & Filters */}
      <div className="flex flex-col md:flex-row gap-4 items-center justify-between bg-slate-900 p-2 rounded-[2rem] border border-slate-800 shadow-xl">
         <div className="relative w-full md:w-96">
            <Search className="absolute left-4 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-500" />
            <input 
              type="text" 
              placeholder="Filter by tracking ID or Red Flag..." 
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="w-full pl-12 pr-4 py-3 bg-slate-800 border-none rounded-2xl text-sm font-bold text-white focus:ring-2 focus:ring-blue-500/50 transition-all placeholder:text-slate-500"
            />
         </div>
         <div className="flex bg-slate-800/50 p-1 rounded-2xl w-full md:w-auto overflow-x-auto">
            {['ALL', 'ACCEPT', 'REJECT', 'REVIEW', 'ABSTAIN'].map((filter) => (
              <button 
                key={filter}
                onClick={() => setActiveFilter(filter as any)}
                className={cn(
                  "flex-1 md:flex-none px-5 py-2.5 text-[10px] font-black rounded-xl transition-all uppercase tracking-widest whitespace-nowrap",
                  activeFilter === filter ? "bg-slate-700 text-white shadow-sm" : "text-slate-500 hover:text-white"
                )}
              >
                {filter}
              </button>
            ))}
         </div>
      </div>

      {/* Audit Logs Table */}
      <div className="bg-slate-900 border border-slate-800 rounded-[2.5rem] shadow-2xl overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full text-left border-collapse">
            <thead>
              <tr className="bg-slate-950/50 border-b border-slate-800">
                <th className="px-8 py-6 text-[10px] font-black text-slate-500 uppercase tracking-widest">Temporal Signature</th>
                <th className="px-8 py-6 text-[10px] font-black text-slate-500 uppercase tracking-widest">Entity Tracking ID</th>
                <th className="px-8 py-6 text-[10px] font-black text-slate-500 uppercase tracking-widest">Neural Verdict</th>
                <th className="px-8 py-6 text-[10px] font-black text-slate-500 uppercase tracking-widest text-right">Action</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800">
              {loading ? (
                <>
                  {[1, 2, 3, 4, 5].map((i) => (
                    <tr key={i}><td colSpan={4} className="p-0"><HistoryRowSkeleton /></td></tr>
                  ))}
                </>
              ) : error ? (
                <tr>
                  <td colSpan={4} className="px-8 py-32 text-center text-rose-500 font-bold uppercase tracking-widest text-xs">{error}</td>
                </tr>
              ) : filteredRecords.length === 0 ? (
                <tr>
                  <td colSpan={4} className="px-8 py-32 text-center text-slate-500">
                    <div className="space-y-2">
                       <SearchCode className="w-12 h-12 mx-auto opacity-20" />
                       <p className="font-black text-[10px] uppercase tracking-widest text-slate-400">No matching audit logs found</p>
                    </div>
                  </td>
                </tr>
              ) : (
                filteredRecords.map((record) => (
                  <tr 
                    key={record.tracking_id}
                    onClick={() => router.push(`/results/${record.tracking_id}`)}
                    className="hover:bg-slate-800/50 transition-all group cursor-pointer"
                  >
                    <td className="px-8 py-6">
                      <div className="flex items-center gap-4">
                         <div className="w-10 h-10 rounded-2xl bg-slate-800 flex items-center justify-center text-slate-500 group-hover:bg-blue-900/30 group-hover:text-blue-400 transition-all">
                            <Clock className="w-5 h-5" />
                         </div>
                         <div>
                            <p className="text-sm font-black text-white leading-none">{new Date(record.timestamp).toLocaleDateString([], { month: 'short', day: 'numeric' })}</p>
                            <p className="text-[10px] font-bold text-slate-500 uppercase mt-1.5">{new Date(record.timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}</p>
                         </div>
                      </div>
                    </td>
                    <td className="px-8 py-6">
                       <div className="flex items-center gap-4">
                          <div className="w-12 h-12 rounded-2xl overflow-hidden bg-slate-800">
                             <img src={`${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'}${record.image_paths.id_card}`} alt="ID" className="w-full h-full object-cover grayscale group-hover:grayscale-0" />
                          </div>
                          <div className="min-w-0">
                             <p className="text-[11px] font-mono font-bold text-slate-300 tracking-tighter truncate w-32">{record.tracking_id}</p>
                             <div className="flex gap-1 mt-1.5">
                                {record.top_factors.slice(0, 2).map((f, i) => (
                                  <span key={i} className="px-1.5 py-0.5 bg-rose-900/20 text-[8px] font-black text-rose-400 border border-rose-500/20 uppercase rounded tracking-tighter">{f.split('_')[0]}</span>
                                ))}
                             </div>
                          </div>
                       </div>
                    </td>
                    <td className="px-8 py-6">
                       <StatusChip verdict={record.decision} />
                    </td>
                    <td className="px-8 py-6 text-right">
                       <div className="w-8 h-8 rounded-full bg-slate-800 flex items-center justify-center ml-auto group-hover:bg-blue-600 group-hover:text-white transition-all">
                          <ChevronRight className="w-4 h-4 text-slate-400 group-hover:text-white" />
                       </div>
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}

function StatBox({ label, value, color }: { label: string; value: number; color: 'slate' | 'emerald' | 'rose' | 'amber' }) {
  const colors = {
    slate: 'text-white bg-slate-800 border-slate-700',
    emerald: 'text-emerald-400 bg-emerald-900/20 border-emerald-500/20',
    rose: 'text-rose-400 bg-rose-900/20 border-rose-500/20',
    amber: 'text-amber-400 bg-amber-900/20 border-amber-500/20'
  };
  return (
    <div className={cn("p-5 rounded-3xl space-y-1 border shadow-lg", colors[color])}>
       <p className="text-[9px] font-black uppercase tracking-widest opacity-70">{label}</p>
       <p className="text-2xl font-black tracking-tighter">{value}</p>
    </div>
  );
}

function StatusChip({ verdict }: { verdict: Verdict }) {
  const styles: Record<Verdict, string> = {
    'ACCEPT': 'bg-emerald-900/20 text-emerald-400 border-emerald-500/20',
    'REJECT': 'bg-rose-900/20 text-rose-400 border-rose-500/20',
    'REVIEW': 'bg-amber-900/20 text-amber-400 border-amber-500/20',
    'ABSTAIN': 'bg-slate-800/50 text-slate-400 border-slate-700'
  };
  
  return (
    <span className={cn(
      "inline-flex items-center gap-1.5 px-3 py-1.5 rounded-xl text-[10px] font-black uppercase tracking-wider border",
      styles[verdict] || styles['ABSTAIN']
    )}>
      <div className={cn("w-1.5 h-1.5 rounded-full", verdict === 'ACCEPT' ? 'bg-emerald-500 shadow-[0_0_5px_rgba(16,185,129,0.5)]' : verdict === 'REJECT' ? 'bg-rose-500 shadow-[0_0_5px_rgba(225,29,72,0.5)]' : 'bg-amber-500 shadow-[0_0_5px_rgba(245,158,11,0.5)]')} />
      {verdict}
    </span>
  );
}

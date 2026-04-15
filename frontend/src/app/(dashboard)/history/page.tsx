"use client";
import { useEffect, useState } from 'react';
import Link from 'next/link';
import { motion, AnimatePresence } from 'framer-motion';
import { 
  Search, 
  ChevronRight, 
  Clock, 
  AlertCircle, 
  Filter, 
  ArrowRight,
  ShieldCheck,
  Activity,
  User as UserIcon,
  Database,
  Calendar
} from 'lucide-react';
import { useRouter } from 'next/navigation';
import { verificationService } from '@/services/api';
import { cn } from '@/lib/utils';

export default function HistoryPage() {
  const router = useRouter();
  const [records, setRecords] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [searchTerm, setSearchTerm] = useState("");
  const [activeFilter, setActiveFilter] = useState('ALL');

  useEffect(() => {
    const fetchRecords = async () => {
      try {
        const data = await verificationService.getHistory();
        setRecords(data);
      } catch (err: any) {
        console.error("Failed to fetch records:", err);
        setError("Network connection failed. Unable to retrieve audit logs.");
      } finally {
        setLoading(false);
      }
    };
    fetchRecords();
  }, []);

  const totalValid = records.filter(r => r.decision === 'VALID').length;
  const totalRisk = records.filter(r => r.decision === 'SUSPICIOUS' || r.decision === 'REJECTED').length;

  const filteredRecords = records.filter(r => {
    const matchesSearch = 
      r.name?.toLowerCase().includes(searchTerm.toLowerCase()) || 
      r.id_number?.toLowerCase().includes(searchTerm.toLowerCase()) ||
      r.tracking_id?.toLowerCase().includes(searchTerm.toLowerCase());
    
    if (activeFilter === 'ALL') return matchesSearch;
    if (activeFilter === 'VALID') return matchesSearch && r.decision === 'VALID';
    if (activeFilter === 'RISK') return matchesSearch && (r.decision === 'SUSPICIOUS' || r.decision === 'REJECTED');
    return matchesSearch;
  });

  return (
    <div className="space-y-8 max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      {/* Header */}
      <div className="flex flex-col lg:flex-row lg:items-center justify-between gap-6">
        <div>
           <h1 className="text-3xl font-bold text-slate-900 tracking-tight">Audit History</h1>
           <p className="text-slate-700 mt-1">Full cryptographic logs retrieved from verification nodes.</p>
        </div>

        <div className="flex flex-col sm:flex-row gap-3">
           <div className="relative group">
              <Search className="w-4 h-4 absolute left-3 top-1/2 -translate-y-1/2 text-slate-400" />
              <input 
                type="text" 
                placeholder="Search by ID or Subject..." 
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="pl-10 pr-4 py-2 bg-white border border-slate-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-500/10 focus:border-blue-500 transition-all w-full sm:w-64"
              />
           </div>
           <div className="flex bg-slate-100 p-1 rounded-lg">
              <button 
                onClick={() => setActiveFilter('ALL')}
                className={cn("px-3 py-1.5 text-xs font-bold rounded-md transition-all", activeFilter === 'ALL' ? "bg-white text-slate-900 shadow-sm" : "text-slate-600 hover:text-slate-700")}
              >
                All ({records.length})
              </button>
              <button 
                onClick={() => setActiveFilter('VALID')}
                className={cn("px-3 py-1.5 text-xs font-bold rounded-md transition-all", activeFilter === 'VALID' ? "bg-white text-emerald-600 shadow-sm" : "text-slate-500 hover:text-slate-700")}
              >
                Valid ({totalValid})
              </button>
              <button 
                onClick={() => setActiveFilter('RISK')}
                className={cn("px-3 py-1.5 text-xs font-bold rounded-md transition-all", activeFilter === 'RISK' ? "bg-white text-rose-600 shadow-sm" : "text-slate-500 hover:text-slate-700")}
              >
                Risk ({totalRisk})
              </button>
           </div>
        </div>
      </div>

      {/* History Table */}
      <div className="bg-white border border-slate-200 rounded-2xl shadow-sm overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full text-left border-collapse">
            <thead>
              <tr className="bg-slate-50/80 border-b border-slate-100">
                <th className="px-6 py-4 text-xs font-bold text-slate-600 uppercase tracking-widest">Date / Time</th>
                <th className="px-6 py-4 text-xs font-bold text-slate-600 uppercase tracking-widest">Subject</th>
                <th className="px-6 py-4 text-xs font-bold text-slate-600 uppercase tracking-widest">Status</th>
                <th className="px-6 py-4 text-xs font-bold text-slate-600 uppercase tracking-widest text-right">Action</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-50">
              {loading ? (
                <tr>
                  <td colSpan={4} className="px-6 py-20 text-center">
                    <div className="flex flex-col items-center gap-3 text-slate-400">
                       <Activity className="w-6 h-6 animate-pulse" />
                       <span className="font-bold text-sm">Retrieving Audit Logs...</span>
                    </div>
                  </td>
                </tr>
              ) : error ? (
                <tr>
                  <td colSpan={4} className="px-6 py-20 text-center text-rose-500 font-bold">{error}</td>
                </tr>
              ) : filteredRecords.length === 0 ? (
                <tr>
                  <td colSpan={4} className="px-6 py-20 text-center text-slate-400">
                    <div className="space-y-1">
                       <p className="font-bold text-slate-300 italic text-lg uppercase">Empty Result Set</p>
                       <p className="text-sm font-medium">Try broadening your search parameters.</p>
                    </div>
                  </td>
                </tr>
              ) : (
                filteredRecords.map((record) => (
                  <tr 
                    key={record.id}
                    onClick={() => router.push(`/results/${record.tracking_id}`)}
                    className="hover:bg-slate-50/50 transition-colors group cursor-pointer"
                  >
                    <td className="px-6 py-5">
                      <div className="flex items-center gap-3">
                         <Calendar className="w-4 h-4 text-slate-300" />
                         <div className="min-w-0">
                            <p className="text-sm font-bold text-slate-900">{new Date(record.created_at).toLocaleDateString([], { month: 'short', day: 'numeric', year: 'numeric' })}</p>
                            <p className="text-[10px] font-medium text-slate-400">{new Date(record.created_at).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}</p>
                         </div>
                      </div>
                    </td>
                    <td className="px-6 py-5">
                       <div className="flex items-center gap-3">
                          <div className={cn(
                             "w-10 h-10 rounded-lg flex items-center justify-center font-bold text-sm",
                             record.decision === 'VALID' ? "bg-emerald-50 text-emerald-600" : "bg-rose-50 text-rose-600"
                          )}>
                             {record.name?.[0] || 'A'}
                          </div>
                          <div className="min-w-0">
                             <p className="text-sm font-bold text-slate-900 truncate">{record.name || 'Anonymous'}</p>
                             <p className="text-[10px] font-mono text-slate-400 truncate">{record.tracking_id}</p>
                          </div>
                       </div>
                    </td>
                    <td className="px-6 py-5">
                       <StatusChip status={record.decision} />
                    </td>
                    <td className="px-6 py-5 text-right">
                       <button className="text-xs font-bold text-blue-600 hover:text-blue-700 flex items-center gap-1 ml-auto">
                          Results <ChevronRight className="w-3.5 h-3.5" />
                       </button>
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

function StatusChip({ status }: { status: string }) {
  const isOk = status === 'VALID';
  const isSuspicious = status === 'SUSPICIOUS';
  
  return (
    <span className={cn(
      "inline-flex items-center gap-1.5 px-2.5 py-1 rounded-md text-[10px] font-bold uppercase tracking-wider border",
      isOk ? "bg-emerald-50 text-emerald-700 border-emerald-100" : 
      isSuspicious ? "bg-amber-50 text-amber-700 border-amber-100" : 
      "bg-rose-50 text-rose-700 border-rose-100"
    )}>
      {status}
    </span>
  );
}

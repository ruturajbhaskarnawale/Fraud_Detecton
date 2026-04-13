"use client";
import { useEffect, useState } from 'react';
import axios from 'axios';
import { motion } from 'framer-motion';
import { History, Search, Filter, ShieldCheck, ChevronRight, Clock } from 'lucide-react';
import Navbar from '@/components/Navbar';
import { cn } from '@/lib/utils';

export default function HistoryPage() {
  const [records, setRecords] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchRecords = async () => {
      try {
        const response = await axios.get('http://localhost:8000/records');
        setRecords(response.data);
      } catch (err) {
        console.error(err);
      } finally {
        setLoading(false);
      }
    };
    fetchRecords();
  }, []);

  return (
    <main className="min-h-screen pt-24 pb-12 px-4 bg-slate-50/50">
      <Navbar />
      
      <div className="max-w-5xl mx-auto space-y-8">
        <div className="flex justify-between items-end">
          <div className="space-y-1">
            <h1 className="text-3xl font-extrabold text-slate-900 tracking-tight">Verification History</h1>
            <p className="text-slate-500 font-medium">Browse and search past security scans.</p>
          </div>
          <div className="flex gap-2">
            <div className="relative">
              <Search className="w-4 h-4 absolute left-3 top-1/2 -translate-y-1/2 text-slate-400" />
              <input 
                type="text" 
                placeholder="Search by ID or Name..." 
                className="pl-10 pr-4 py-2 bg-white border border-slate-200 rounded-xl text-sm focus:outline-none focus:ring-2 focus:ring-blue-500/20"
              />
            </div>
          </div>
        </div>

        <div className="bg-white rounded-[2rem] border border-slate-200 shadow-sm overflow-hidden">
          <table className="w-full text-left">
            <thead>
              <tr className="bg-slate-50 border-b border-slate-200">
                <th className="px-6 py-4 text-xs font-bold text-slate-400 uppercase tracking-widest">Date</th>
                <th className="px-6 py-4 text-xs font-bold text-slate-400 uppercase tracking-widest">Document</th>
                <th className="px-6 py-4 text-xs font-bold text-slate-400 uppercase tracking-widest">Subject</th>
                <th className="px-6 py-4 text-xs font-bold text-slate-400 uppercase tracking-widest">Decision</th>
                <th className="px-6 py-4 text-xs font-bold text-slate-400 uppercase tracking-widest">Score</th>
                <th className="px-6 py-4"></th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100">
              {loading ? (
                <tr>
                  <td colSpan={6} className="px-6 py-12 text-center text-slate-400">Loading records...</td>
                </tr>
              ) : records.length === 0 ? (
                <tr>
                  <td colSpan={6} className="px-6 py-12 text-center text-slate-400">No records found.</td>
                </tr>
              ) : (
                records.map((record, i) => (
                  <motion.tr 
                    key={record.id}
                    initial={{ opacity: 0, y: 10 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ delay: i * 0.05 }}
                    className="hover:bg-slate-50/50 transition-colors group cursor-pointer"
                  >
                    <td className="px-6 py-4">
                      <div className="flex items-center gap-2 text-sm text-slate-600 font-medium">
                        <Clock className="w-3.5 h-3.5 text-slate-400" />
                        {new Date(record.timestamp).toLocaleDateString()}
                      </div>
                    </td>
                    <td className="px-6 py-4">
                      <span className="text-sm font-bold text-slate-700">{record.doc_type}</span>
                    </td>
                    <td className="px-6 py-4">
                      <div className="flex flex-col">
                        <span className="text-sm font-bold text-slate-900">{record.name || 'Anonymous'}</span>
                        <span className="text-[10px] text-slate-400 font-mono">{record.id_number || 'N/A'}</span>
                      </div>
                    </td>
                    <td className="px-6 py-4">
                      <StatusBadge status={record.decision} />
                    </td>
                    <td className="px-6 py-4">
                      <span className="text-sm font-black text-slate-900">{record.risk_score}</span>
                    </td>
                    <td className="px-6 py-4 text-right">
                      <ChevronRight className="w-4 h-4 text-slate-300 group-hover:text-blue-500 transition-colors inline" />
                    </td>
                  </motion.tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </div>
    </main>
  );
}

function StatusBadge({ status }: { status: string }) {
  const styles = {
    VALID: "bg-green-50 text-green-700 border-green-200",
    SUSPICIOUS: "bg-amber-50 text-amber-700 border-amber-200",
    REJECTED: "bg-red-50 text-red-700 border-red-200",
  }[status] || "bg-slate-50 text-slate-700 border-slate-200";

  return (
    <span className={cn("px-2.5 py-1 rounded-full text-[10px] font-black tracking-widest border", styles)}>
      {status}
    </span>
  );
}

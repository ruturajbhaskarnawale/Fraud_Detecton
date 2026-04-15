"use client";
import { useEffect, useState } from 'react';
import { motion } from 'framer-motion';
import { 
  BarChart3, 
  TrendingUp, 
  ShieldCheck, 
  AlertCircle, 
  Clock, 
  Zap,
  Activity,
  Filter,
  Download,
  ChevronRight,
  Database
} from 'lucide-react';
import { verificationService } from '@/services/api';
import { cn } from '@/lib/utils';
import Link from 'next/link';

export default function DashboardPage() {
  const [data, setData] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const records = await verificationService.getHistory();
        setData(records);
      } catch (err) {
        console.error("Dashboard data load failed:", err);
      } finally {
        setLoading(false);
      }
    };
    fetchData();
  }, []);

  // Compute analytics
  const total = data.length;
  const verified = data.filter(r => r.decision === 'VALID').length;
  const suspicious = data.filter(r => r.decision === 'SUSPICIOUS').length;
  const rejected = data.filter(r => r.decision === 'REJECTED').length;
  
  const successRate = total > 0 ? ((verified / total) * 100).toFixed(1) : "0.0";
  const fraudPrevention = total > 0 ? (((suspicious + rejected) / total) * 100).toFixed(1) : "0.0";

  return (
    <div className="space-y-8 max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <h1 className="text-3xl font-bold text-slate-900 tracking-tight">Analytics Dashboard</h1>
          <p className="text-slate-700 mt-1">Real-time identity verification metrics and logs.</p>
        </div>
        
        <div className="flex items-center gap-3">
           <button className="inline-flex items-center gap-2 px-4 py-2 bg-white border border-slate-200 rounded-lg text-sm font-semibold text-slate-700 hover:bg-slate-50 transition-colors shadow-sm">
              <Filter className="w-4 h-4" />
              <span>Filter</span>
           </button>
           <button className="inline-flex items-center gap-2 px-4 py-2 bg-slate-900 border border-slate-900 rounded-lg text-sm font-semibold text-white hover:bg-slate-800 transition-colors shadow-sm">
              <Download className="w-4 h-4" />
              <span>Export CSV</span>
           </button>
        </div>
      </div>

      {/* Metrics Row */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
         <MetricCard 
           label="Total Scans"
           value={total.toLocaleString()}
           trend="+12.5%"
           trendUp={true}
           icon={<Activity className="w-5 h-5" />}
         />
         <MetricCard 
           label="Verification Rate"
           value={`${successRate}%`}
           trend="+0.4%"
           trendUp={true}
           icon={<ShieldCheck className="w-5 h-5" />}
           color="blue"
         />
         <MetricCard 
           label="Fraud Prevented"
           value={`${fraudPrevention}%`}
           trend="+5.2%"
           trendUp={false}
           icon={<AlertCircle className="w-5 h-5" />}
           color="rose"
         />
         <MetricCard 
           label="Avg Latency"
           value="2.4s"
           trend="-0.2s"
           trendUp={true}
           icon={<Clock className="w-5 h-5" />}
         />
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
         {/* Main Chart Section */}
         <div className="lg:col-span-2 bg-white border border-slate-200 rounded-2xl p-6 shadow-sm">
            <div className="flex justify-between items-center mb-6">
               <h3 className="font-bold text-slate-900">Scan Volume Trends</h3>
               <div className="flex gap-4 text-xs font-semibold text-slate-500">
                  <span className="flex items-center gap-1.5"><div className="w-2 h-2 bg-blue-500 rounded-full"/> Valid</span>
                  <span className="flex items-center gap-1.5"><div className="w-2 h-2 bg-rose-500 rounded-full"/> Risk</span>
               </div>
            </div>
            
            <div className="h-64 w-full flex items-end justify-between gap-3 pt-4">
               {[0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11].map((i) => {
                 // Deterministic heights to avoid hydration errors
                 const validHeight = [45, 52, 38, 65, 48, 55, 72, 60, 42, 58, 68, 50][i];
                 const riskHeight = [8, 12, 5, 15, 10, 8, 12, 11, 7, 9, 14, 8][i];
                 
                 return (
                   <div key={i} className="flex-1 flex flex-col items-center gap-2 h-full">
                      <div className="w-full flex flex-col-reverse h-full bg-slate-50 rounded-md overflow-hidden">
                         <div className="bg-blue-500 w-full" style={{ height: `${validHeight}%` }} />
                         <div className="bg-rose-500 w-full" style={{ height: `${riskHeight}%` }} />
                      </div>
                   </div>
                 );
               })}
            </div>
            <div className="flex justify-between mt-4 px-1 text-[10px] font-bold text-slate-400 uppercase tracking-widest">
               <span>Mon</span>
               <span>Tue</span>
               <span>Wed</span>
               <span>Thu</span>
               <span>Fri</span>
               <span>Sat</span>
               <span>Sun</span>
            </div>
         </div>

         {/* Recent Activity Section */}
         <div className="bg-white border border-slate-200 rounded-2xl p-6 shadow-sm overflow-hidden flex flex-col">
            <div className="flex justify-between items-center mb-6">
               <h3 className="font-bold text-slate-900">Recent Scans</h3>
               <Link href="/history" className="text-xs font-bold text-blue-600 hover:text-blue-700">View All</Link>
            </div>

            <div className="space-y-4 overflow-y-auto max-h-[300px] flex-1">
               {data.slice(0, 5).map((record) => (
                 <Link key={record.id} href={`/results/${record.tracking_id}`} className="flex items-center justify-between p-3 rounded-xl hover:bg-slate-50 transition-colors group">
                    <div className="flex items-center gap-3">
                       <div className={cn(
                          "w-10 h-10 rounded-lg flex items-center justify-center",
                          record.decision === 'VALID' ? "bg-emerald-50 text-emerald-600" : "bg-rose-50 text-rose-600"
                       )}>
                          {record.decision === 'VALID' ? <ShieldCheck className="w-5 h-5" /> : <AlertCircle className="w-5 h-5" />}
                       </div>
                       <div className="min-w-0">
                          <p className="text-sm font-bold text-slate-900 truncate">{record.name || 'Anonymous'}</p>
                          <p className="text-[10px] font-medium text-slate-400 uppercase tracking-tight">{record.created_at ? new Date(record.created_at).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }) : 'Pending'}</p>
                       </div>
                    </div>
                    <ChevronRight className="w-4 h-4 text-slate-300 group-hover:text-slate-400" />
                 </Link>
               ))}
               
               {data.length === 0 && (
                 <div className="py-12 text-center text-slate-400 opacity-50">
                    <Database className="w-8 h-8 mx-auto mb-2" />
                    <p className="text-xs font-bold">No data processed yet.</p>
                 </div>
               )}
            </div>
         </div>
      </div>
    </div>
  );
}

function MetricCard({ label, value, trend, trendUp, icon, color = "slate" }: any) {
  const colors = {
    slate: "text-slate-600",
    blue: "text-blue-600",
    rose: "text-rose-600"
  };

  return (
    <div className="bg-white border border-slate-200 p-6 rounded-2xl shadow-sm hover:border-slate-300 transition-colors">
      <div className="flex justify-between items-start mb-4">
        <div className="p-2 bg-slate-50 rounded-lg text-slate-400">
           {icon}
        </div>
        <div className={cn(
           "flex items-center gap-1 text-[10px] font-bold px-2 py-0.5 rounded-full",
           trendUp ? "bg-emerald-50 text-emerald-700" : "bg-rose-50 text-rose-700"
        )}>
           {trendUp ? <TrendingUp className="w-3 h-3" /> : <AlertCircle className="w-3 h-3" />}
           {trend}
        </div>
      </div>
      <div>
        <p className="text-sm font-medium text-slate-500 mb-1">{label}</p>
        <div className="text-2xl font-bold text-slate-900">{value}</div>
      </div>
    </div>
  );
}

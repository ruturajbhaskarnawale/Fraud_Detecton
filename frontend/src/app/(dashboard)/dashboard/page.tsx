"use client";
import { useEffect, useState } from 'react';
import { 
  ShieldCheck, 
  AlertCircle, 
  Clock, 
  Activity,
  Download,
} from 'lucide-react';
import { verificationService } from '@/services/api';
import { cn } from '@/lib/utils';
import { useResultStore } from '@/stores/useResultStore';
import { DashboardCardSkeleton } from '@/components/Skeleton';
import { MetricCard } from '@/components/dashboard/MetricCard';
import { TrendChart } from '@/components/dashboard/TrendChart';
import { RecentActivityList } from '@/components/dashboard/RecentActivityList';

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
      ...data.map(r => [r.tracking_id, r.decision, r.risk?.score || 'N/A', r.timestamp].join(','))
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
          <h1 className="text-3xl font-bold tracking-tight">Analytics Dashboard</h1>
          <p className="text-muted-foreground mt-1">Real-time identity verification metrics and logs.</p>
        </div>
        
        <div className="flex items-center gap-3">
           <div className="flex bg-secondary border border-border rounded-lg p-1 shadow-sm">
              {['ALL', 'ACCEPT', 'RISK'].map((f) => (
                <button
                  key={f}
                  onClick={() => setFilter(f)}
                  className={cn(
                    "px-3 py-1.5 text-xs font-bold rounded-md transition-all uppercase tracking-tight",
                    filter === f ? "bg-card text-foreground shadow-sm" : "text-muted-foreground hover:text-foreground"
                  )}
                >
                  {f}
                </button>
              ))}
           </div>
           <button onClick={handleExportCSV} className="inline-flex items-center gap-2 px-4 py-2.5 bg-secondary border border-border rounded-lg text-sm font-bold text-foreground hover:bg-muted transition-colors shadow-sm">
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
         <TrendChart />
         <RecentActivityList loading={loading} data={filteredData} />
      </div>
    </div>
  );
}

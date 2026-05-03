import { ReactNode } from 'react';
import { AlertCircle, TrendingUp } from 'lucide-react';
import { cn } from '@/lib/utils';

export interface MetricCardProps {
  label: string;
  value: string | number;
  trend: string;
  trendUp: boolean;
  icon: ReactNode;
  color?: 'blue' | 'emerald' | 'rose' | 'amber';
  isActive?: boolean;
  onClick?: () => void;
}

export function MetricCard({ label, value, trend, trendUp, icon, isActive, onClick }: MetricCardProps) {
  return (
    <button 
      onClick={onClick} 
      className={cn(
        "bg-card border p-6 rounded-2xl shadow-xl transition-all text-left group w-full", 
        isActive ? "border-blue-500 ring-1 ring-blue-500" : "border-border hover:border-accent/50 shadow-sm"
      )}
    >
      <div className="flex justify-between items-start mb-4">
        <div className={cn("p-2 rounded-lg transition-colors", isActive ? "bg-blue-500/10 text-blue-500" : "bg-secondary text-muted-foreground group-hover:text-foreground")}>
          {icon}
        </div>
        <div className={cn(
          "flex items-center gap-1 text-[10px] font-bold px-2 py-0.5 rounded-full border", 
          trendUp ? "bg-emerald-500/10 text-emerald-500 border-emerald-500/20" : "bg-rose-500/10 text-rose-500 border-rose-500/20"
        )}>
           {trendUp ? <TrendingUp className="w-3 h-3" /> : <AlertCircle className="w-3 h-3" />}
           {trend}
        </div>
      </div>
      <div>
        <p className="text-sm font-medium text-muted-foreground mb-1">{label}</p>
        <div className="text-2xl font-bold text-foreground">{value}</div>
      </div>
    </button>
  );
}

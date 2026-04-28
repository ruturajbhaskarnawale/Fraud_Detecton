import React from 'react';
import { cn } from '@/lib/utils';

export function Skeleton({ className, ...props }: React.HTMLAttributes<HTMLDivElement>) {
  return (
    <div
      className={cn("animate-pulse rounded-md bg-slate-200", className)}
      {...props}
    />
  );
}

export function HistoryRowSkeleton() {
  return (
    <div className="flex items-center justify-between p-6 border-b border-slate-50 last:border-0">
      <div className="flex items-center gap-4">
        <Skeleton className="w-10 h-10 rounded-2xl" />
        <div className="space-y-2">
          <Skeleton className="h-4 w-24" />
          <Skeleton className="h-3 w-16" />
        </div>
      </div>
      <div className="flex items-center gap-4">
        <div className="flex items-center gap-3">
          <Skeleton className="w-12 h-12 rounded-2xl" />
          <div className="space-y-2">
            <Skeleton className="h-3 w-32" />
            <Skeleton className="h-2 w-16" />
          </div>
        </div>
      </div>
      <Skeleton className="h-6 w-20 rounded-xl" />
      <Skeleton className="w-8 h-8 rounded-full" />
    </div>
  );
}

export function DashboardCardSkeleton() {
  return (
    <div className="bg-white border border-slate-200 p-6 rounded-2xl shadow-sm space-y-4">
      <div className="flex justify-between">
        <Skeleton className="w-10 h-10 rounded-lg" />
        <Skeleton className="w-14 h-5 rounded-full" />
      </div>
      <div className="space-y-2">
        <Skeleton className="h-4 w-20" />
        <Skeleton className="h-8 w-24" />
      </div>
    </div>
  );
}

export function ResultPanelSkeleton() {
  return (
    <div className="space-y-10 animate-pulse">
      <div className="flex justify-between items-end pb-6 border-b border-slate-100">
        <div className="space-y-3">
          <Skeleton className="h-4 w-32" />
          <Skeleton className="h-10 w-64" />
        </div>
        <div className="flex gap-3">
          <Skeleton className="w-12 h-12 rounded-2xl" />
          <Skeleton className="w-32 h-12 rounded-2xl" />
        </div>
      </div>
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-10">
        <div className="lg:col-span-4 space-y-8">
           <Skeleton className="h-[400px] rounded-[2.5rem]" />
           <Skeleton className="h-[200px] rounded-[2rem]" />
        </div>
        <div className="lg:col-span-8 space-y-10">
           <Skeleton className="h-[300px] rounded-[2.5rem]" />
           <div className="grid grid-cols-2 gap-8">
              <Skeleton className="h-[320px] rounded-[2rem]" />
              <Skeleton className="h-[320px] rounded-[2rem]" />
           </div>
        </div>
      </div>
    </div>
  );
}

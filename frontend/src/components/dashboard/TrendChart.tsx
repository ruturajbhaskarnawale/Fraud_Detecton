export function TrendChart() {
  return (
    <div className="lg:col-span-2 bg-card border border-border rounded-2xl p-6 shadow-xl">
      <div className="flex justify-between items-center mb-6">
        <h3 className="font-bold text-foreground">Scan Volume Trends</h3>
        <div className="flex gap-4 text-xs font-semibold text-muted-foreground">
          <span className="flex items-center gap-1.5"><div className="w-2 h-2 bg-blue-500 rounded-full"/> Valid</span>
          <span className="flex items-center gap-1.5"><div className="w-2 h-2 bg-rose-500 rounded-full"/> Risk</span>
        </div>
      </div>
      <div className="h-64 w-full flex items-end justify-between gap-3 pt-4">
        {[0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11].map((i) => (
          <div key={i} className="flex-1 flex flex-col items-center gap-2 h-full">
            <div className="w-full flex flex-col-reverse h-full bg-secondary rounded-md overflow-hidden">
              <div className="bg-blue-500 w-full" style={{ height: `${[45, 52, 38, 65, 48, 55, 72, 60, 42, 58, 68, 50][i]}%` }} />
              <div className="bg-rose-500 w-full" style={{ height: `${[8, 12, 5, 15, 10, 8, 12, 11, 7, 9, 14, 8][i]}%` }} />
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

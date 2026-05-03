import { BrainCircuit, FileText, Globe, SearchCode, Terminal } from 'lucide-react';
import { VerifyResponse } from '@/services/api';
import { cn } from '@/lib/utils';

export function DeepAnalysisGrid({ data }: { data: VerifyResponse }) {
  return (
    <div className="pt-10 border-t border-slate-800 space-y-6">
      <h3 className="text-xl font-bold text-white tracking-tight flex items-center gap-2">
        <SearchCode className="w-6 h-6 text-blue-500" /> Deep Verification Analysis
      </h3>
      <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-4 gap-6">
        
        {/* AI Reasoning */}
        <div className="bg-slate-900 border border-slate-800 rounded-3xl p-6 shadow-xl space-y-4">
          <div className="flex items-center gap-2 border-b border-slate-800 pb-3">
            <BrainCircuit className="w-4 h-4 text-emerald-500" />
            <h4 className="text-sm font-bold text-slate-300 uppercase tracking-widest">AI Reasoning</h4>
          </div>
          <p className="text-sm text-slate-400 leading-relaxed font-medium">
            {data.explanation || 'No explanation provided by the decision engine.'}
          </p>
          {data.risk?.breakdown && Object.keys(data.risk.breakdown).length > 0 && (
            <div className="space-y-3 pt-4 border-t border-slate-800">
              {Object.entries(data.risk.breakdown).map(([key, val]) => (
                <div key={key} className="space-y-1.5">
                  <div className="flex justify-between text-[10px] font-bold text-slate-500 uppercase tracking-widest">
                    <span>{key.replace(/_/g, ' ')}</span>
                    <span className="font-mono">{((val as number) * 100).toFixed(0)}%</span>
                  </div>
                  <div className="w-full h-1 bg-slate-800 rounded-full overflow-hidden">
                    <div className="h-full bg-rose-500" style={{ width: `${(val as number) * 100}%` }} />
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>

        {/* Extracted Data */}
        <div className="bg-slate-900 border border-slate-800 rounded-3xl p-6 shadow-xl space-y-4">
          <div className="flex items-center gap-2 border-b border-slate-800 pb-3">
            <FileText className="w-4 h-4 text-blue-500" />
            <h4 className="text-sm font-bold text-slate-300 uppercase tracking-widest">Extracted Fields</h4>
          </div>
          <div className="space-y-3 overflow-y-auto max-h-[300px] pr-2 custom-scrollbar">
            <div className="flex justify-between items-center py-2 border-b border-slate-800/50">
              <span className="text-xs font-bold text-slate-500 uppercase tracking-widest">Doc Type</span>
              <span className="text-xs font-bold text-white">{data.document?.document_type || 'Unknown'}</span>
            </div>
            {data.document?.fields && Object.entries(data.document.fields).map(([key, val]) => (
              <div key={key} className="flex justify-between items-center py-2 border-b border-slate-800/50">
                <span className="text-[10px] font-bold text-slate-500 uppercase tracking-widest">{key}</span>
                <span className="text-xs font-bold text-white max-w-[60%] truncate text-right" title={String(val)}>
                  {String(val)}
                </span>
              </div>
            ))}
          </div>
        </div>

        {/* Metadata / Network Telemetry */}
        <div className="bg-slate-900 border border-slate-800 rounded-3xl p-6 shadow-xl space-y-4">
          <div className="flex items-center gap-2 border-b border-slate-800 pb-3">
            <Globe className="w-4 h-4 text-indigo-500" />
            <h4 className="text-sm font-bold text-slate-300 uppercase tracking-widest">Network Telemetry</h4>
          </div>
          <div className="space-y-3">
            <div className="flex justify-between items-center py-2 border-b border-slate-800/50">
              <span className="text-xs font-bold text-slate-500 uppercase tracking-widest">IP Risk</span>
              <span className="text-xs font-bold text-white">
                {data.metadata?.ip_risk !== undefined ? `${(data.metadata.ip_risk * 100).toFixed(0)}%` : 'N/A'}
              </span>
            </div>
            <div className="flex justify-between items-center py-2 border-b border-slate-800/50">
              <span className="text-xs font-bold text-slate-500 uppercase tracking-widest">Device Risk</span>
              <span className="text-xs font-bold text-white">
                {data.metadata?.device_risk !== undefined ? `${(data.metadata.device_risk * 100).toFixed(0)}%` : 'N/A'}
              </span>
            </div>
            <div className="flex justify-between items-center py-2 border-b border-slate-800/50">
              <span className="text-xs font-bold text-slate-500 uppercase tracking-widest">Geo Risk</span>
              <span className="text-xs font-bold text-white">
                {data.metadata?.geo_risk !== undefined ? `${(data.metadata.geo_risk * 100).toFixed(0)}%` : 'N/A'}
              </span>
            </div>
            <div className="flex justify-between items-center py-2 border-b border-slate-800/50">
              <span className="text-xs font-bold text-slate-500 uppercase tracking-widest">VPN / Proxy</span>
              <span className={cn("text-xs font-bold", data.metadata?.is_vpn ? "text-rose-500" : "text-emerald-500")}>
                {data.metadata?.is_vpn ? 'DETECTED' : 'CLEAR'}
              </span>
            </div>
            <div className="flex justify-between items-center py-2 border-b border-slate-800/50">
              <span className="text-xs font-bold text-slate-500 uppercase tracking-widest">Geo Anomaly</span>
              <span className={cn("text-xs font-bold", data.metadata?.geo_anomaly ? "text-rose-500" : "text-white")}>
                {data.metadata?.geo_anomaly ? 'TRUE' : 'FALSE'}
              </span>
            </div>
            {data.metadata?.flags && data.metadata.flags.length > 0 && (
              <div className="pt-2">
                <span className="text-[10px] font-bold text-slate-500 uppercase tracking-widest block mb-2">Network Flags</span>
                <div className="flex flex-wrap gap-2">
                  {data.metadata.flags.map((f, i) => (
                    <span key={i} className="px-2 py-1 bg-slate-800 text-slate-300 rounded text-[9px] uppercase font-bold tracking-widest">
                      {f}
                    </span>
                  ))}
                </div>
              </div>
            )}
          </div>
        </div>

        {/* OCR Text */}
        <div className="bg-slate-950 border border-slate-800 rounded-3xl p-6 shadow-xl flex flex-col h-[400px]">
          <div className="flex items-center justify-between border-b border-slate-800 pb-3 mb-4">
            <div className="flex items-center gap-2">
              <Terminal className="w-4 h-4 text-slate-400" />
              <h4 className="text-sm font-bold text-slate-300 uppercase tracking-widest">Raw OCR Log</h4>
            </div>
            <span className="text-[10px] font-mono text-emerald-500">
              {((data.ocr?.confidence || 0) * 100).toFixed(1)}% CONF
            </span>
          </div>
          <div className="flex-1 overflow-auto bg-slate-900 rounded-xl p-4 border border-slate-800 custom-scrollbar">
            <pre className="text-[10px] text-emerald-400/80 font-mono whitespace-pre-wrap leading-relaxed">
              {data.ocr?.text || 'NO OCR TEXT EXTRACTED.'}
            </pre>
          </div>
        </div>

      </div>
    </div>
  );
}

"use client";
import Link from 'next/link';
import { motion } from 'framer-motion';
import { Code2, ChevronLeft, Globe, Terminal, Play, Save } from 'lucide-react';

export default function ApiReferencePage() {
  return (
    <div className="min-h-screen bg-white pt-32 pb-20 px-6">
      <div className="max-w-7xl mx-auto space-y-20">
        <div className="max-w-3xl space-y-8">
          <Link href="/" className="inline-flex items-center gap-2 text-slate-400 hover:text-blue-600 transition-colors font-bold text-sm uppercase tracking-widest">
            <ChevronLeft className="w-4 h-4" />
            Back to Home
          </Link>
          <div className="space-y-4">
             <div className="w-14 h-14 bg-slate-900 text-white rounded-2xl flex items-center justify-center shadow-2xl">
                <Terminal className="w-7 h-7" />
             </div>
             <h1 className="text-5xl md:text-7xl font-black tracking-tighter text-slate-900 leading-none">API Reference</h1>
             <p className="text-xl text-slate-500 font-medium leading-relaxed">
                Connect your existing stack to the Veridex forensic engine via our REST and GraphQL endpoints.
             </p>
          </div>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-12 gap-12 pt-10 border-t border-slate-100">
           <div className="lg:col-span-4 space-y-12">
              <div className="space-y-4">
                 <h3 className="text-sm font-black text-slate-900 uppercase tracking-widest">Authentication</h3>
                 <p className="text-slate-500 text-sm leading-6">All API requests must be authenticated using an API Key. Your API keys carry significant privileges, so be sure to keep them secure.</p>
              </div>
              <div className="space-y-4">
                 <h3 className="text-sm font-black text-slate-900 uppercase tracking-widest">Endpoints</h3>
                 <nav className="flex flex-col gap-2">
                    {['POST /v1/verify', 'GET /v1/sessions', 'PATCH /v1/metadata', 'DELETE /v1/purge'].map(ep => (
                      <button key={ep} className="text-left px-4 py-3 rounded-xl bg-slate-50 text-slate-700 font-mono text-xs font-bold border border-slate-100 hover:border-blue-500 hover:bg-blue-50 transition-all">
                        {ep}
                      </button>
                    ))}
                 </nav>
              </div>
           </div>

           <div className="lg:col-span-8 bg-slate-900 rounded-[3rem] p-8 md:p-12 text-slate-300 shadow-2xl relative overflow-hidden">
              <div className="absolute top-0 right-0 w-64 h-64 bg-blue-500/10 blur-[100px] rounded-full" />
              <div className="relative z-10 space-y-8 font-mono">
                 <div className="flex items-center justify-between border-b border-white/10 pb-6 text-xs font-bold text-white uppercase tracking-widest">
                    <span>Example Request</span>
                    <div className="flex gap-2">
                       <button className="px-3 py-1 bg-white/5 rounded-md hover:bg-white/10 transition-colors">Copy</button>
                       <button className="px-3 py-1 bg-blue-600 text-white rounded-md flex items-center gap-2"><Play className="w-3 h-3" /> Run</button>
                    </div>
                 </div>
                 <div className="space-y-4 text-sm leading-6">
                    <p className="text-slate-400"># Verify a document</p>
                    <p><span className="text-blue-400">curl</span> -X POST https://api.veridex.ai/v1/verify \</p>
                    <p>&nbsp;&nbsp;-H <span className="text-amber-300">"Authorization: Bearer YOUR_API_KEY"</span> \</p>
                    <p>&nbsp;&nbsp;-F <span className="text-amber-300">"file=@id_card.jpg"</span> \</p>
                    <p>&nbsp;&nbsp;-F <span className="text-amber-300">"type=aadhaar"</span></p>
                 </div>
                 <div className="pt-8 border-t border-white/10 space-y-4">
                    <p className="text-[10px] font-black text-white uppercase tracking-widest">Response Library</p>
                    <div className="bg-black/40 rounded-2xl p-6 text-emerald-400 text-xs shadow-inner">
                       {`{\n  "status": "success",\n  "request_id": "req_8812920",\n  "verification": {\n    "confidence": 0.998,\n    "verified_fields": ["name", "dob", "doc_number"]\n  }\n}`}
                    </div>
                 </div>
              </div>
           </div>
        </div>
      </div>
    </div>
  );
}

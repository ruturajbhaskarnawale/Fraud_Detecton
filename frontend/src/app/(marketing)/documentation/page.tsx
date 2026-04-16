"use client";
import Link from 'next/link';
import { motion } from 'framer-motion';
import { Book, ChevronLeft, Search, FileText, Code, Settings } from 'lucide-react';

export default function DocumentationPage() {
  return (
    <div className="min-h-screen bg-slate-50 pt-32 pb-20 px-6">
      <div className="max-w-7xl mx-auto grid grid-cols-1 lg:grid-cols-12 gap-12">
        {/* Sidebar */}
        <div className="lg:col-span-3 space-y-8">
          <Link href="/" className="inline-flex items-center gap-2 text-slate-500 hover:text-blue-600 transition-colors font-bold text-sm uppercase tracking-widest">
            <ChevronLeft className="w-4 h-4" />
            Back to Home
          </Link>
          
          <div className="space-y-6">
             <div className="relative">
                <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-400" />
                <input 
                  type="text" 
                  placeholder="Search docs..." 
                  className="w-full bg-white border border-slate-200 rounded-xl py-2 pl-10 pr-4 focus:ring-2 focus:ring-blue-500/20 focus:border-blue-500 outline-none transition-all text-sm"
                />
             </div>
             
             <nav className="space-y-1">
                <p className="px-3 text-[10px] font-black text-slate-400 uppercase tracking-[0.2em] mb-4">Getting Started</p>
                <DocLink active>Introduction</DocLink>
                <DocLink>Quickstart Guide</DocLink>
                <DocLink>Installation</DocLink>
                
                <p className="px-3 text-[10px] font-black text-slate-400 uppercase tracking-[0.2em] mt-8 mb-4">Core Concepts</p>
                <DocLink>Identity Verification</DocLink>
                <DocLink>Fraud Detection</DocLink>
                <DocLink>Biometric Matching</DocLink>
             </nav>
          </div>
        </div>

        {/* Content */}
        <div className="lg:col-span-9 bg-white rounded-[2.5rem] border border-slate-200 shadow-sm p-8 md:p-16">
          <motion.div 
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="max-w-3xl space-y-12"
          >
            <div className="space-y-4">
              <div className="w-12 h-12 bg-blue-50 text-blue-600 rounded-2xl flex items-center justify-center">
                 <Book className="w-6 h-6" />
              </div>
              <h1 className="text-4xl md:text-5xl font-black tracking-tighter text-slate-900">Documentation</h1>
              <p className="text-xl text-slate-600 leading-relaxed font-medium">
                Learn how to integrate Veridex AI into your workflow, from initial setup to advanced fraud detection logic.
              </p>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
               <DocCard 
                 title="Quickstart" 
                 desc="Get up and running in under 5 minutes with our simplified SDK."
                 icon={<Code className="w-5 h-5" />}
               />
               <DocCard 
                 title="Features" 
                 desc="Explore OCR, Biometric Sync, and Forensic engines."
                 icon={<FileText className="w-5 h-5" />}
               />
            </div>

            <div className="prose prose-slate max-w-none">
               <h2 className="text-2xl font-black tracking-tight mt-12 mb-6">Introduction to Veridex AI</h2>
               <p className="text-slate-600 leading-7">
                  Veridex AI is an industrial-grade identity verification platform designed for performance, accuracy, and security. Our unified API allows you to automate the full document verification lifecycle, from sub-pixel OCR extraction to encrypted decision-making logs.
               </p>
               <div className="my-8 p-6 bg-slate-900 rounded-2xl text-slate-300 font-mono text-sm leading-6 overflow-x-auto">
                  <span className="text-blue-400">const</span> veridex = <span className="text-emerald-400">require</span>(<span className="text-amber-300">'@veridex/sdk'</span>);<br/>
                  <span className="text-blue-400">await</span> veridex.<span className="text-blue-300">initialize</span>({'{'}<br/>
                  &nbsp;&nbsp;apiKey: <span className="text-amber-300">'VX_PROD_8812'</span>,<br/>
                  &nbsp;&nbsp;environment: <span className="text-amber-300">'production'</span><br/>
                  {'}'});
               </div>
            </div>
          </motion.div>
        </div>
      </div>
    </div>
  );
}

function DocLink({ children, active = false }: { children: React.ReactNode, active?: boolean }) {
  return (
    <Link 
      href="#" 
      className={cn(
        "block px-3 py-2 rounded-xl text-sm font-bold transition-all",
        active ? "bg-blue-50 text-blue-600" : "text-slate-500 hover:bg-slate-100"
      )}
    >
      {children}
    </Link>
  );
}

function DocCard({ title, desc, icon }: any) {
  return (
    <div className="p-6 rounded-2xl border border-slate-100 bg-slate-50 hover:border-blue-200 transition-all group cursor-pointer">
       <div className="w-10 h-10 bg-white rounded-xl flex items-center justify-center text-slate-400 group-hover:text-blue-600 transition-colors mb-4 shadow-sm">
          {icon}
       </div>
       <h3 className="font-black tracking-tight text-slate-900 mb-2">{title}</h3>
       <p className="text-sm text-slate-500 font-medium leading-relaxed">{desc}</p>
    </div>
  );
}

function cn(...inputs: any[]) {
  return inputs.filter(Boolean).join(' ');
}

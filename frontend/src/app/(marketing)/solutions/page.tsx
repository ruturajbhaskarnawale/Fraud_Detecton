"use client";
import { motion } from 'framer-motion';
import { ShieldCheck, UserCheck, Search, Database, Fingerprint, Globe, Lock, Cpu, Zap, Activity } from 'lucide-react';
import Link from 'next/link';

const solutions = [
  {
    title: "Document Forensics",
    desc: "Sub-pixel analysis of identity documents to detect font mismatches, field alterations, and sophisticated physical forgeries.",
    icon: Search,
    color: "blue",
    features: ["Font Integrity Check", "Texture Analysis", "Hologram Validation"]
  },
  {
    title: "Biometric Fusion",
    desc: "1:1 facial matching with 68-point vector mapping, integrated with 3D liveness checks to defeat print and screen-based spoofs.",
    icon: Fingerprint,
    color: "emerald",
    features: ["3D Face Mapping", "Passive Liveness", "Spoof Defense"]
  },
  {
    title: "Neural OCR",
    desc: "Industrial-grade text extraction optimized for low-light, skewed, and low-resolution images of over 150+ global ID formats.",
    icon: Cpu,
    color: "rose",
    features: ["Multi-Language Support", "MRZ Validation", "Auto-Redaction"]
  },
  {
    title: "Risk Orchestration",
    desc: "A centralized engine that fuses biometric, document, and metadata signals into a single, calibrated fraud risk score.",
    icon: Activity,
    color: "amber",
    features: ["Custom Decision Logic", "Real-time Auditing", "Behavioral Signals"]
  }
];

export default function SolutionsPage() {
  return (
    <div className="min-h-screen bg-background text-foreground pt-32 pb-24 px-6 overflow-hidden">
      {/* Background decoration */}
      <div className="fixed inset-0 z-0 pointer-events-none">
        <div className="absolute top-[-10%] right-[-10%] w-[50%] h-[50%] bg-blue-600/5 blur-[120px] rounded-full" />
        <div className="absolute bottom-[-10%] left-[-10%] w-[40%] h-[40%] bg-emerald-600/5 blur-[100px] rounded-full" />
      </div>

      <div className="max-w-7xl mx-auto relative z-10">
        <motion.div 
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="text-center space-y-8 mb-32"
        >
          <div className="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-blue-500/10 text-blue-500 text-xs font-black tracking-widest uppercase border border-blue-500/20 backdrop-blur-md">
            Enterprise Solutions
          </div>
          <h1 className="text-6xl md:text-8xl font-black tracking-tighter leading-none">
            Built for <span className="text-blue-500">Scale.</span> <br />
            Hardened for <span className="text-emerald-500">Security.</span>
          </h1>
          <p className="text-xl text-muted-foreground max-w-2xl mx-auto font-medium">
            Veridex AI provides the forensic-grade infrastructure required to protect high-volume platforms from sophisticated identity fraud and synthetic attacks.
          </p>
        </motion.div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
          {solutions.map((s, i) => (
            <motion.div
              key={s.title}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: i * 0.1 }}
              className="group"
            >
              <div className="bg-card/80 backdrop-blur-xl p-10 rounded-[2.5rem] h-full flex flex-col space-y-8 border border-border transition-all hover:border-blue-500/50 hover:shadow-2xl hover:shadow-blue-500/10">
                <div className="w-16 h-16 bg-blue-600/10 rounded-2xl flex items-center justify-center text-blue-500">
                  <s.icon className="w-8 h-8" />
                </div>
                <div className="space-y-4">
                  <h3 className="text-3xl font-black tracking-tight">{s.title}</h3>
                  <p className="text-muted-foreground leading-relaxed font-medium">{s.desc}</p>
                </div>

                <div className="flex flex-wrap gap-3 pt-4 border-t border-border mt-auto">
                  {s.features.map(f => (
                    <span key={f} className="px-4 py-1.5 rounded-full bg-secondary border border-border text-[10px] font-bold text-muted-foreground uppercase tracking-widest">
                      {f}
                    </span>
                  ))}
                </div>
              </div>
            </motion.div>
          ))}
        </div>

        {/* CTA */}
        <motion.div 
          initial={{ opacity: 0, scale: 0.95 }}
          whileInView={{ opacity: 1, scale: 1 }}
          viewport={{ once: true }}
          className="mt-32 p-12 md:p-24 rounded-[4rem] bg-blue-600 relative overflow-hidden text-center space-y-8"
        >
          <div className="absolute inset-0 bg-gradient-to-r from-blue-700 to-blue-500 opacity-50" />
          <div className="absolute top-0 right-0 w-96 h-96 bg-white/10 blur-[80px] rounded-full -mr-48 -mt-48" />
          
          <div className="relative z-10 space-y-6">
            <h2 className="text-5xl md:text-7xl font-black tracking-tighter leading-none">Ready to automate trust?</h2>
            <p className="text-blue-100 text-xl font-medium max-w-xl mx-auto">
              Deploy our forensic models into your production environment in under 30 minutes.
            </p>
            <div className="flex flex-col sm:flex-row items-center justify-center gap-4 pt-4">
              <Link href="/verify" className="px-10 py-5 bg-white text-blue-600 dark:bg-white dark:text-blue-600 rounded-2xl font-black text-xl hover:bg-slate-100 transition-all shadow-2xl">
                Get Started Now
              </Link>
              <Link href="/documentation" className="px-10 py-5 bg-blue-700 text-white dark:bg-blue-700 dark:text-white border border-blue-500 rounded-2xl font-black text-xl hover:bg-blue-800 transition-all">
                Read API Docs
              </Link>
            </div>
          </div>
        </motion.div>
      </div>
    </div>
  );
}

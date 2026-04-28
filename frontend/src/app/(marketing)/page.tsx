"use client";
import Link from 'next/link';
import Image from 'next/image';
import { motion, useScroll, useTransform, useSpring, useMotionValue, AnimatePresence } from 'framer-motion';
import { 
  ShieldCheck, 
  Cpu, 
  Zap, 
  ArrowRight,
  Lock,
  Globe,
  Fingerprint,
  User,
  Activity,
  ChevronRight,
  SearchCode,
  Layers,
  CheckCircle2,
  AlertCircle,
  Play
} from 'lucide-react';
import { useState, useEffect, useRef } from 'react';
import { cn } from '@/lib/utils';

export default function LandingPage() {
  const containerRef = useRef<HTMLDivElement>(null);
  const { scrollYProgress } = useScroll({
    target: containerRef,
    offset: ["start start", "end start"]
  });

  // Parallax transforms
  const backgroundY = useTransform(scrollYProgress, [0, 1], ["0%", "50%"]);
  const textY = useTransform(scrollYProgress, [0, 1], ["0%", "100%"]);
  const opacity = useTransform(scrollYProgress, [0, 0.5], [1, 0]);

  return (
    <div ref={containerRef} className="flex flex-col relative text-white bg-slate-950 min-h-screen selection:bg-blue-500/30">
      
      {/* Background Ambience */}
      <div className="fixed inset-0 z-0 pointer-events-none">
         <div className="absolute top-[-10%] left-[-10%] w-[50%] h-[50%] bg-blue-600/10 blur-[120px] rounded-full" />
         <div className="absolute bottom-[-10%] right-[-5%] w-[40%] h-[40%] bg-emerald-600/10 blur-[100px] rounded-full" />
         <div className="absolute top-[40%] left-[60%] w-[30%] h-[30%] bg-rose-600/5 blur-[120px] rounded-full" />
         <div className="absolute inset-0 bg-[url('/noise.png')] opacity-[0.03] mix-blend-overlay" />
      </div>

      {/* Hero Section */}
      <section className="relative min-h-screen flex items-center justify-center pt-32 pb-32 px-6 overflow-hidden z-10">
        <div className="max-w-7xl mx-auto w-full grid grid-cols-1 lg:grid-cols-2 gap-20 items-center">
          
          {/* Left Column: Messaging */}
          <motion.div 
            style={{ y: textY, opacity }}
            className="space-y-10 text-center lg:text-left relative z-20"
          >
            <motion.div 
              initial={{ opacity: 0, scale: 0.9 }}
              animate={{ opacity: 1, scale: 1 }}
              className="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-blue-900/20 text-blue-400 text-[10px] font-black tracking-[0.2em] uppercase border border-blue-500/20 backdrop-blur-md"
            >
              <div className="w-2 h-2 bg-blue-500 rounded-full animate-pulse shadow-[0_0_10px_rgba(59,130,246,0.8)]" />
              <span>Veridex Engine V4 Active</span>
            </motion.div>
            
            <div className="space-y-4">
              <h1 className="text-6xl md:text-8xl font-black tracking-tighter text-white leading-[0.85] perspective drop-shadow-2xl">
                <AnimatedText text="Identity Infrastructure." className="block" />
                <span className="text-transparent bg-clip-text bg-gradient-to-r from-blue-400 to-emerald-400 block relative py-2">
                   <AnimatedText text="For the AI Era." delay={0.5} />
                </span>
              </h1>
            </div>
            
            <motion.p 
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              transition={{ delay: 1.2 }}
              className="max-w-xl mx-auto lg:mx-0 text-lg text-slate-400 font-medium leading-relaxed"
            >
              Military-grade document parsing, biometric fusion, and forgery detection. Verify global identity records with sub-pixel precision and cryptographic certainty in under 500ms.
            </motion.p>

            <motion.div 
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 1.4 }}
              className="flex flex-col sm:flex-row items-center justify-center lg:justify-start gap-4 pt-4"
            >
              <MagneticButton>
                <Link 
                  href="/verify" 
                  className="px-8 py-5 bg-blue-600 text-white rounded-2xl font-bold text-lg hover:bg-blue-500 transition-all flex items-center justify-center gap-3 shadow-[0_0_40px_-10px_rgba(37,99,235,0.5)] group relative overflow-hidden"
                >
                  <span className="relative z-10">Start Verification Demo</span>
                  <Play className="w-4 h-4 fill-current relative z-10 group-hover:translate-x-1 transition-transform" />
                  <div className="absolute inset-0 bg-gradient-to-r from-blue-600 to-blue-400 opacity-0 group-hover:opacity-100 transition-opacity" />
                </Link>
              </MagneticButton>
              <Link 
                href="/dashboard" 
                className="px-8 py-5 bg-slate-900/50 text-white border border-slate-700 backdrop-blur-md rounded-2xl font-bold text-lg hover:bg-slate-800 transition-all flex items-center justify-center gap-2"
              >
                Developer API
              </Link>
            </motion.div>

            {/* Platform Metrics */}
            <motion.div 
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              transition={{ delay: 1.8 }}
              className="pt-8 flex flex-wrap justify-center lg:justify-start items-center gap-8 border-t border-slate-800"
            >
               <div className="flex flex-col">
                  <span className="text-2xl font-black text-white tracking-tighter">99.98%</span>
                  <span className="text-[10px] font-bold text-emerald-400 uppercase tracking-widest">Accuracy Level</span>
               </div>
               <div className="w-px h-8 bg-slate-800 hidden sm:block" />
               <div className="flex flex-col">
                  <span className="text-2xl font-black text-white tracking-tighter">42ms</span>
                  <span className="text-[10px] font-bold text-blue-400 uppercase tracking-widest">Avg Latency</span>
               </div>
               <div className="w-px h-8 bg-slate-800 hidden sm:block" />
               <div className="flex flex-col">
                  <span className="text-2xl font-black text-white tracking-tighter">150+</span>
                  <span className="text-[10px] font-bold text-slate-500 uppercase tracking-widest">Global IDs</span>
               </div>
            </motion.div>
          </motion.div>

          {/* Right Column: Forensic Console Visual */}
          <div className="hidden lg:block relative perspective h-[600px] z-20">
             <ForensicConsole />
          </div>
        </div>
      </section>

      {/* Product Roadmap / How it Works */}
      <section className="py-32 px-6 relative z-10 border-t border-slate-800/50 bg-slate-950/50 backdrop-blur-3xl">
        <div className="max-w-7xl mx-auto space-y-24">
          <motion.div 
            initial={{ opacity: 0, y: 30 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            className="text-center space-y-6"
          >
            <div className="inline-flex items-center gap-2 px-3 py-1 bg-slate-900 rounded-full text-[10px] font-black tracking-widest text-slate-400 uppercase border border-slate-800">
               <Activity className="w-3 h-3 text-emerald-500" />
               The Verification Pipeline
            </div>
            <h2 className="text-5xl md:text-7xl font-black tracking-tighter">Intelligent <span className="text-blue-500">Forensics.</span></h2>
            <p className="text-slate-400 max-w-2xl mx-auto font-medium text-lg">From sub-pixel OCR extraction to encrypted decision logic, our pipeline is built for high-stakes reliability.</p>
          </motion.div>

          {/* Featured Cards */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
             <StandardCard 
               title="Neural OCR"
               desc="Advanced text extraction that detects font manipulation, field displacement, and MRZ irregularities with industrial precision."
               icon={<SearchCode className="w-8 h-8" />}
               color="blue"
             />
             <StandardCard 
                title="Biometric Sync"
                desc="Map 68 vector points on facial records to ensure 1:1 match across various document types, defeating high-res print attacks."
                icon={<Fingerprint className="w-8 h-8" />}
                color="emerald"
                active
             />
             <StandardCard 
                title="Cryptic Ledger"
                desc="Every verification result is hashed and signed, ensuring a permanent, tamper-proof audit trail for regulatory compliance."
                icon={<Lock className="w-8 h-8" />}
                color="rose"
             />
          </div>
        </div>
      </section>

      {/* Interactive Demo Section */}
      <section className="py-32 px-6 relative z-10 border-t border-slate-800">
        <div className="max-w-7xl mx-auto grid grid-cols-1 lg:grid-cols-2 gap-20 items-center">
           <div className="space-y-8">
              <h2 className="text-5xl md:text-7xl font-black tracking-tighter leading-none">Trust, but <br/><span className="text-emerald-500">verify.</span></h2>
              <p className="text-xl text-slate-400 font-medium leading-relaxed">Veridex AI is the preferred security partner for high-volume Fintech and identity-first platforms worldwide.</p>
              
              <div className="space-y-6 pt-4">
                 {[
                   { title: 'Zero-Latency Integration', desc: 'Deploy via our REST API in minutes, not months.' },
                   { title: 'Deepfake Detection Ready', desc: 'Liveness checks that defeat masks, screens, and AI-generated faces.' },
                   { title: 'SOC2 & GDPR Compliant', desc: 'Enterprise-grade security architecture protecting PII data.' }
                 ].map((f, i) => (
                   <div key={i} className="flex gap-4">
                      <div className="w-10 h-10 mt-1 bg-slate-900 border border-slate-800 text-emerald-500 rounded-xl flex items-center justify-center flex-shrink-0">
                         <CheckCircle2 className="w-5 h-5" />
                      </div>
                      <div>
                         <h4 className="font-bold text-lg tracking-tight text-white">{f.title}</h4>
                         <p className="text-slate-500 font-medium">{f.desc}</p>
                      </div>
                   </div>
                 ))}
              </div>
           </div>
           
           {/* Visual Element */}
           <div className="relative h-[600px] w-full rounded-[3rem] border border-slate-800 bg-slate-900/50 backdrop-blur-xl shadow-2xl overflow-hidden flex items-center justify-center p-8 group">
              <div className="absolute inset-0 bg-gradient-to-b from-blue-500/5 to-transparent pointer-events-none" />
              
              <div className="w-full max-w-sm bg-slate-950 border border-slate-800 rounded-3xl p-6 space-y-6 shadow-2xl relative z-10 group-hover:scale-105 transition-transform duration-500">
                 <div className="flex justify-between items-center pb-4 border-b border-slate-800">
                    <div className="flex items-center gap-2">
                       <Activity className="w-4 h-4 text-emerald-500" />
                       <span className="text-[10px] font-black uppercase tracking-widest text-slate-400">Live API Response</span>
                    </div>
                    <span className="text-[10px] font-mono text-slate-500">200 OK</span>
                 </div>
                 
                 <div className="space-y-3 font-mono text-xs">
                    <p className="text-emerald-400">{"{"}</p>
                    <div className="pl-4 space-y-2">
                       <p><span className="text-blue-400">"status"</span><span className="text-slate-500">:</span> <span className="text-emerald-300">"ACCEPT"</span>,</p>
                       <p><span className="text-blue-400">"trust_index"</span><span className="text-slate-500">:</span> <span className="text-amber-400">99.4</span>,</p>
                       <p><span className="text-blue-400">"signals"</span><span className="text-slate-500">:</span> {"{"}</p>
                       <div className="pl-4 space-y-2">
                          <p><span className="text-blue-400">"ocr_confidence"</span><span className="text-slate-500">:</span> <span className="text-amber-400">0.998</span>,</p>
                          <p><span className="text-blue-400">"face_match"</span><span className="text-slate-500">:</span> <span className="text-emerald-300">true</span>,</p>
                          <p><span className="text-blue-400">"forgery_detected"</span><span className="text-slate-500">:</span> <span className="text-rose-400">false</span></p>
                       </div>
                       <p className="text-emerald-400">{"}"}</p>
                    </div>
                    <p className="text-emerald-400">{"}"}</p>
                 </div>
                 
                 <div className="pt-4 border-t border-slate-800 flex justify-between items-center">
                    <span className="text-[10px] text-slate-500 uppercase tracking-widest font-black">Response Time: 42ms</span>
                    <ShieldCheck className="w-5 h-5 text-emerald-500" />
                 </div>
              </div>
           </div>
        </div>
      </section>

      {/* Final CTA */}
      <section className="py-40 px-6 relative z-10 border-t border-slate-800 bg-gradient-to-b from-slate-950 to-blue-950/20 overflow-hidden">
        <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[800px] h-[800px] bg-blue-600/10 blur-[120px] rounded-full pointer-events-none" />
        <div className="max-w-4xl mx-auto text-center space-y-12 relative z-10">
           <h2 className="text-6xl md:text-8xl font-black tracking-tighter leading-[0.9] drop-shadow-2xl">Integrate with <br/><span className="text-transparent bg-clip-text bg-gradient-to-r from-blue-400 to-emerald-400">Certainty.</span></h2>
           <p className="text-xl text-slate-400 max-w-2xl mx-auto">Join the world's most secure identity verification network. Start verifying users in minutes.</p>
           <div className="flex flex-col sm:flex-row items-center justify-center gap-4">
              <Link href="/verify" className="px-12 py-6 bg-blue-600 text-white rounded-2xl font-black text-xl hover:bg-blue-500 transition-all shadow-[0_0_40px_-10px_rgba(37,99,235,0.6)]">
                 Start Free Integration
              </Link>
              <Link href="/documentation" className="px-12 py-6 bg-slate-900 text-white border border-slate-700 rounded-2xl font-bold text-xl hover:bg-slate-800 transition-all">
                 Read the Docs
              </Link>
           </div>
        </div>
      </section>

    </div>
  );
}

// Forensic Console Components

function ForensicConsole() {
  const mouseX = useMotionValue(0);
  const mouseY = useMotionValue(0);
  const springX = useSpring(mouseX, { stiffness: 60, damping: 20 });
  const springY = useSpring(mouseY, { stiffness: 60, damping: 20 });

  const rotateX = useTransform(springY, [-300, 300], [10, -10]);
  const rotateY = useTransform(springX, [-300, 300], [-10, 10]);

  useEffect(() => {
    const handleMouseMove = (e: MouseEvent) => {
      mouseX.set(e.clientX - window.innerWidth * 0.75);
      mouseY.set(e.clientY - window.innerHeight * 0.5);
    };
    window.addEventListener("mousemove", handleMouseMove);
    return () => window.removeEventListener("mousemove", handleMouseMove);
  }, [mouseX, mouseY]);

  return (
    <motion.div 
      style={{ rotateX, rotateY }}
      className="relative w-full h-full flex items-center justify-center preserve-3d group"
    >
       {/* Background Depth Frame */}
       <div className="absolute inset-x-0 inset-y-10 bg-blue-500/10 rounded-[3rem] blur-3xl transform translate-z-[-100px] scale-90" />
       
       {/* Main Glass Console Pane */}
       <motion.div 
         className="relative w-full max-w-[520px] bg-slate-900/60 backdrop-blur-2xl border border-slate-700 rounded-[3rem] shadow-[0_50px_100px_-20px_rgba(0,0,0,0.5)] overflow-hidden p-8 space-y-8 preserve-3d"
       >
          {/* Dashboard Header UI */}
          <div className="flex items-center justify-between">
             <div className="flex gap-1.5">
                <div className="w-3 h-3 rounded-full bg-rose-500" />
                <div className="w-3 h-3 rounded-full bg-amber-500" />
                <div className="w-3 h-3 rounded-full bg-emerald-500" />
             </div>
             <div className="text-[10px] font-black text-slate-400 uppercase tracking-widest bg-slate-950 px-4 py-1.5 rounded-full border border-slate-800">
                FORENSIC ENGINE v4.2
             </div>
          </div>

          <div className="grid grid-cols-12 gap-8 relative z-10">
             {/* Left side: The Card Scanner */}
             <div className="col-span-12 lg:col-span-7 space-y-6">
                <DocumentScanner />
                <div className="grid grid-cols-2 gap-4">
                   <MiniStat label="OCR MATCH" value="99.4%" color="blue" />
                   <MiniStat label="VECTOR SYNC" value="PASS" color="emerald" />
                </div>
             </div>

             {/* Right side: The Technical Log Feed */}
             <div className="col-span-12 lg:col-span-5 border-l border-slate-800 pl-8">
                <LiveLogFeed />
             </div>
          </div>

          {/* Bottom Summary Bar */}
          <div className="pt-8 border-t border-slate-800 flex items-center justify-between">
             <div className="flex items-center gap-3">
                <div className="w-10 h-10 rounded-xl bg-blue-600 flex items-center justify-center text-white shadow-lg shadow-blue-500/30 overflow-hidden">
                   <Image src="/logo2.png" alt="Veridex AI" width={24} height={24} className="w-6 h-6 object-contain" />
                </div>
                <div>
                   <p className="text-[10px] font-bold text-slate-500 uppercase tracking-tight">Active Protocol</p>
                   <p className="text-xs font-black text-white">IDENTITY_VERIFICATION_COMPLETE</p>
                </div>
             </div>
             <div className="flex items-center gap-2 px-3 py-1.5 bg-emerald-900/30 text-emerald-400 border border-emerald-500/20 rounded-lg shadow-[0_0_15px_rgba(16,185,129,0.2)]">
                <CheckCircle2 className="w-4 h-4" />
                <span className="text-[10px] font-black uppercase">Secure</span>
             </div>
          </div>
       </motion.div>

       {/* Floating Biometric Detail */}
       <motion.div 
         animate={{ y: [0, -15, 0] }}
         transition={{ duration: 6, repeat: Infinity, ease: "easeInOut" }}
         className="absolute -right-12 top-1/2 -translate-y-1/2 w-52 bg-slate-900/90 backdrop-blur-xl border border-slate-700 p-6 rounded-[2.5rem] shadow-2xl z-20 space-y-4"
       >
          <div className="text-[10px] font-black text-blue-400 uppercase tracking-widest flex items-center gap-2">
            <Scan className="w-3 h-3" /> Biometric Mesh
          </div>
          <div className="h-32 w-full bg-slate-950 rounded-2xl flex items-center justify-center relative overflow-hidden group border border-slate-800">
             <Fingerprint className="w-12 h-12 text-blue-500 relative z-10" />
             <div className="absolute inset-0 bg-gradient-to-t from-blue-600/20 to-transparent" />
             <motion.div 
               animate={{ y: [-50, 100] }}
               transition={{ duration: 3, repeat: Infinity, ease: "linear" }}
               className="absolute top-0 left-0 w-full h-1 bg-blue-400 blur-sm shadow-[0_0_10px_rgba(96,165,250,0.8)]"
             />
          </div>
          <p className="text-[10px] font-bold text-slate-500 leading-tight">68 LANDMARKS IDENTIFIED ACROSS VECTOR PLANE.</p>
       </motion.div>
    </motion.div>
  );
}

function Scan({className}: {className?: string}) {
  return <SearchCode className={className} />
}

function DocumentScanner() {
  return (
    <div className="relative group perspective">
       {/* Mockup ID Card */}
       <div className="w-full aspect-[1.6/1] bg-slate-950 rounded-2xl border-2 border-slate-800 p-6 space-y-4 relative overflow-hidden group-hover:border-blue-500/50 transition-colors">
          <div className="flex justify-between items-start">
             <div className="w-12 h-14 bg-slate-800 rounded-lg animate-pulse" />
             <div className="space-y-2 flex-1 ml-4">
                <div className="h-3 w-3/4 bg-slate-800 rounded-full" />
                <div className="h-2 w-1/2 bg-slate-800 rounded-full" />
                <div className="h-2 w-2/3 bg-slate-800/50 rounded-full" />
             </div>
             <div className="w-10 h-10 bg-slate-800 rounded-full" />
          </div>
          
          <div className="space-y-3 pt-4">
             <div className="h-2 w-full bg-slate-800 rounded-full" />
             <div className="h-2 w-full bg-slate-800 rounded-full" />
             <div className="h-6 w-3/4 bg-slate-900 rounded-lg flex items-center px-3 border border-slate-800">
                <div className="h-1.5 w-full bg-slate-700 rounded-full" />
             </div>
          </div>

          {/* The SVG Scan Beam */}
          <motion.div 
            animate={{ top: ['-10%', '110%'] }}
            transition={{ duration: 4, repeat: Infinity, ease: [0.4, 0, 0.2, 1] }}
            className="absolute left-0 w-full h-12 bg-gradient-to-b from-transparent via-blue-500/30 to-transparent pointer-events-none z-10"
          >
             <div className="w-full h-px bg-blue-400 shadow-[0_0_15px_rgba(96,165,250,1)]" />
          </motion.div>

          <AnimatePresence>
             <motion.div 
               initial={{ opacity: 0 }}
               whileInView={{ opacity: 1 }}
               className="absolute inset-0 bg-blue-600/10 mix-blend-overlay pointer-events-none"
             />
          </AnimatePresence>
       </div>
    </div>
  );
}

function LiveLogFeed() {
  const [logs, setLogs] = useState([
    "> INITIALIZING_ENGINE",
    "> LOADING_VECTORS",
    "> OCR_SCAN_READY",
    "> AUTHENTICATING...",
    "> SYNC_NODES_OK",
    "> FORENSIC_ANALYSIS_INIT",
  ]);

  useEffect(() => {
    const logInterval = setInterval(() => {
      setLogs(prev => {
        const next = [...prev.slice(1), `> LOG_${Math.floor(Math.random() * 1000)}_PASS_SYNC`];
        return next;
      });
    }, 2000);
    return () => clearInterval(logInterval);
  }, []);

  return (
    <div className="space-y-4 h-full flex flex-col justify-center">
       {logs.map((log, i) => (
         <motion.div 
           key={log + i}
           initial={{ opacity: 0, x: 10 }}
           animate={{ opacity: 1 - (i * 0.15), x: 0 }}
           className="text-[9px] font-mono font-bold text-blue-400 uppercase tracking-tight"
         >
            {log}
         </motion.div>
       ))}
    </div>
  );
}

function MiniStat({ label, value, color }: any) {
  const colors = {
    blue: "bg-blue-900/20 text-blue-400 border-blue-500/20",
    emerald: "bg-emerald-900/20 text-emerald-400 border-emerald-500/20"
  } as any;

  return (
    <div className={cn("p-4 rounded-2xl border", colors[color])}>
       <p className="text-[10px] font-black uppercase opacity-70 tracking-widest">{label}</p>
       <h4 className="text-lg font-black">{value}</h4>
    </div>
  );
}

function StandardCard({ title, desc, icon, active = false, color = "blue" }: any) {
  return (
    <div className={cn(
      "p-px rounded-[3rem] transition-all duration-500 transform hover:-translate-y-2 relative group overflow-hidden",
      active ? `bg-gradient-to-b from-${color}-500/50 to-transparent` : "bg-gradient-to-b from-slate-800 to-transparent hover:from-slate-700"
    )}>
       <div className="bg-slate-950 p-10 rounded-[3rem] space-y-6 flex flex-col items-center text-center h-full relative z-10 border border-slate-900/50">
          <div className={cn(
             "w-16 h-16 rounded-2xl flex items-center justify-center mb-2 shadow-xl",
             active ? `bg-${color}-900/30 text-${color}-400 border border-${color}-500/30` : "bg-slate-900 text-slate-500 border border-slate-800 group-hover:text-white"
          )}>
             {icon}
          </div>
          <div className="space-y-3 flex-1">
             <h3 className="text-2xl font-black tracking-tighter text-white">{title}</h3>
             <p className="text-sm font-medium leading-relaxed text-slate-400">{desc}</p>
          </div>
       </div>
    </div>
  );
}

function AnimatedText({ text, delay = 0, className = "" }: { text: string, delay?: number, className?: string }) {
  const words = text.split(" ");
  return (
    <span className={className}>
      {words.map((word, i) => (
        <motion.span 
          key={i} 
          initial={{ opacity: 0, y: 30 }} 
          animate={{ opacity: 1, y: 0 }} 
          transition={{ delay: delay + (i * 0.1), duration: 0.8, ease: "circOut" }} 
          className="inline-block mr-[0.2em]"
        >
          {word}
        </motion.span>
      ))}
    </span>
  );
}

function MagneticButton({ children }: { children: React.ReactNode }) {
  const x = useMotionValue(0);
  const y = useMotionValue(0);
  const springX = useSpring(x, { stiffness: 150, damping: 15 });
  const springY = useSpring(y, { stiffness: 150, damping: 15 });
  const handleMouseMove = (e: React.MouseEvent) => {
    const rect = e.currentTarget.getBoundingClientRect();
    x.set((e.clientX - (rect.left + rect.width / 2)) * 0.3);
    y.set((e.clientY - (rect.top + rect.height / 2)) * 0.3);
  };
  return <motion.div style={{ x: springX, y: springY }} onMouseMove={handleMouseMove} onMouseLeave={() => { x.set(0); y.set(0); }}>{children}</motion.div>;
}

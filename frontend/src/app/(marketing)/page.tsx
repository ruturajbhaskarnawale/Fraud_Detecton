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
  AlertCircle
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
    <div ref={containerRef} className="flex flex-col relative text-slate-900">
      {/* Hero Section */}
      <section className="relative min-h-screen flex items-center justify-center pt-20 pb-32 px-6 overflow-hidden bg-[#f8fafc]">
        {/* Interactive Background */}
        <motion.div 
          style={{ y: backgroundY }}
          className="absolute inset-0 -z-10"
        >
          <div className="absolute top-[-10%] left-[-10%] w-[50%] h-[50%] bg-blue-400/10 blur-[120px] rounded-full" />
          <div className="absolute bottom-[10%] right-[-5%] w-[40%] h-[40%] bg-indigo-400/10 blur-[100px] rounded-full" />
        </motion.div>

        <div className="max-w-7xl mx-auto w-full grid grid-cols-1 lg:grid-cols-2 gap-20 items-center relative z-10">
          {/* Left Column: Messaging */}
          <motion.div 
            style={{ y: textY, opacity }}
            className="space-y-10 text-center lg:text-left"
          >
            <motion.div 
              initial={{ opacity: 0, scale: 0.9 }}
              animate={{ opacity: 1, scale: 1 }}
              className="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-blue-50 text-blue-700 text-[10px] font-black tracking-[0.2em] uppercase border border-blue-100/50"
            >
              <div className="w-2 h-2 bg-blue-600 rounded-full animate-pulse" />
              <span>System Status: Optimal</span>
            </motion.div>
            
            <div className="space-y-4">
              <h1 className="text-6xl md:text-8xl font-black tracking-tighter text-slate-900 leading-[0.85] perspective">
                <AnimatedText text="Identity Check." className="block" />
                <span className="gradient-text block relative">
                   <AnimatedText text="Simplified." delay={0.5} />
                   <motion.div 
                     initial={{ width: 0 }}
                     animate={{ width: "100%" }}
                     transition={{ delay: 1.5, duration: 1, ease: "circOut" }}
                     className="absolute -bottom-2 left-0 h-1.5 bg-blue-600/20 rounded-full"
                   />
                </span>
              </h1>
            </div>
            
            <motion.p 
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              transition={{ delay: 1.2 }}
              className="max-w-xl mx-auto lg:mx-0 text-lg text-slate-600 font-medium leading-relaxed"
            >
              Industry-leading document forensic and biometric matching engine. Verify identity records with sub-pixel precision and cryptographic certainty.
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
                  className="px-8 py-5 bg-blue-600 text-white rounded-2xl font-bold text-lg hover:bg-blue-700 transition-all flex items-center justify-center gap-2 shadow-2xl shadow-blue-200 group relative overflow-hidden"
                >
                  <span>Launch Verify</span>
                  <ArrowRight className="w-5 h-5 group-hover:translate-x-1 transition-transform" />
                </Link>
              </MagneticButton>
              <Link 
                href="/dashboard" 
                className="px-8 py-5 bg-white text-slate-700 border border-slate-200 rounded-2xl font-bold text-lg hover:bg-slate-50 transition-all flex items-center justify-center gap-2 shadow-sm"
              >
                Open Dashboard
              </Link>
            </motion.div>

            {/* Platform Metrics */}
            <motion.div 
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              transition={{ delay: 1.8 }}
              className="pt-8 flex flex-wrap justify-center lg:justify-start items-center gap-8 border-t border-slate-100"
            >
               <div className="flex flex-col">
                  <span className="text-2xl font-black text-slate-900 tracking-tighter">99.9%</span>
                  <span className="text-[10px] font-bold text-slate-400 uppercase tracking-widest">Uptime Record</span>
               </div>
               <div className="w-px h-8 bg-slate-100 hidden sm:block" />
               <div className="flex flex-col">
                  <span className="text-2xl font-black text-slate-900 tracking-tighter">&lt; 3s</span>
                  <span className="text-[10px] font-bold text-slate-400 uppercase tracking-widest">Global Latency</span>
               </div>
               <div className="w-px h-8 bg-slate-100 hidden sm:block" />
               <div className="flex flex-col">
                  <span className="text-2xl font-black text-slate-900 tracking-tighter">2.4M</span>
                  <span className="text-[10px] font-bold text-slate-400 uppercase tracking-widest">Assets Verified</span>
               </div>
            </motion.div>
          </motion.div>

          {/* Right Column: Forensic Console Visual */}
          <div className="hidden lg:block relative perspective h-[600px]">
             <ForensicConsole />
          </div>
        </div>

        {/* Layered Wave Divider */}
        <LayeredWaveDivider />
      </section>

      {/* Product Roadmap / How it Works */}
      <section className="py-40 px-6 bg-[#0f172a] text-white relative overflow-visible z-10">
        <div className="max-w-7xl mx-auto space-y-24">
          <motion.div 
            initial={{ opacity: 0, y: 30 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            className="text-center space-y-6"
          >
            <div className="inline-flex items-center gap-2 px-3 py-1 bg-white/5 rounded-full text-[10px] font-black tracking-widest text-slate-400 uppercase border border-white/10">
               <Activity className="w-3 h-3 text-blue-500" />
               Automated Protocol
            </div>
            <h2 className="text-5xl md:text-7xl font-black tracking-tighter">Intelligent <span className="text-blue-500">Forensics.</span></h2>
            <p className="text-slate-400 max-w-2xl mx-auto font-medium text-lg">From sub-pixel OCR extraction to encrypted decision logic, our pipeline is built for high-stakes reliability.</p>
          </motion.div>

          {/* Featured Cards */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
             <StandardCard 
               title="Neural OCR"
               desc="Advanced text extraction that detects font manipulation and field displacement with industrial precision."
               icon={<SearchCode className="w-8 h-8" />}
             />
             <StandardCard 
                title="Biometric Sync"
                desc="Map 68 vector points on facial records to ensure 1:1 match across various document types."
                icon={<Fingerprint className="w-8 h-8" />}
                active
             />
             <StandardCard 
                title="Cryptic Ledger"
                desc="Every verification result is hashed and signed, ensuring a permanent, tamper-proof audit trail."
                icon={<Lock className="w-8 h-8" />}
             />
          </div>
        </div>
      </section>

      {/* Stats/Social Proof Section 3 */}
      <section className="py-40 px-6 bg-[#f8fafc] border-b border-slate-100">
        <div className="max-w-7xl mx-auto grid grid-cols-1 lg:grid-cols-2 gap-20 items-center">
           <div className="space-y-8">
              <h2 className="text-5xl md:text-8xl font-black tracking-tighter text-slate-900 leading-none italic">Results that <br/><span className="text-blue-600 not-italic">matter.</span></h2>
              <div className="space-y-4">
                 <p className="text-xl text-slate-600 font-medium leading-relaxed">Veridex AI is the preferred security partner for high-volume Fintech and identity-first platforms worldwide.</p>
                 <div className="flex flex-col gap-3">
                    {['Zero-Latency Integration', 'Deepfake Detection Ready', 'SOC2 Compliant Architecture'].map((f, i) => (
                      <div key={i} className="flex items-center gap-3">
                         <div className="w-5 h-5 bg-emerald-100 text-emerald-600 rounded-full flex items-center justify-center">
                            <CheckCircle2 className="w-3 h-3 fill-current" />
                         </div>
                         <span className="font-bold text-slate-800 tracking-tight">{f}</span>
                      </div>
                    ))}
                 </div>
              </div>
           </div>
           
           <div className="grid grid-cols-2 gap-4">
              <div className="bg-white p-8 rounded-[2rem] border border-slate-200 shadow-sm space-y-4 transform hover:-translate-y-2 transition-transform">
                 <div className="w-12 h-12 bg-blue-50 text-blue-600 rounded-2xl flex items-center justify-center">
                    <Activity className="w-6 h-6" />
                 </div>
                 <div>
                    <h4 className="font-black text-2xl tracking-tighter text-slate-900">42ms</h4>
                    <p className="text-[10px] font-bold text-slate-400 uppercase tracking-widest">Avg Pulse Time</p>
                 </div>
              </div>
              <div className="bg-slate-900 p-8 rounded-[2rem] text-white space-y-4 translate-y-8 transform hover:translate-y-6 transition-transform">
                 <div className="w-12 h-12 bg-white/10 rounded-2xl flex items-center justify-center">
                    <Image src="/logo2.png" alt="Logo" width={24} height={24} className="w-6 h-6 object-contain" />
                 </div>
                 <div>
                    <h4 className="font-black text-2xl tracking-tighter text-white">99.8%</h4>
                    <p className="text-[10px] font-bold text-white/40 uppercase tracking-widest">Fraud Accuracy</p>
                 </div>
              </div>
           </div>
        </div>
      </section>

      {/* Final CTA */}
      <section className="py-40 px-6 bg-white relative">
        <div className="max-w-4xl mx-auto text-center space-y-12">
           <h2 className="text-6xl md:text-9xl font-black tracking-tighter text-slate-900 leading-[0.8]">Build with <br/><span className="gradient-text">Certainty.</span></h2>
           <div className="flex flex-col sm:flex-row items-center justify-center gap-4">
              <Link href="/verify" className="px-12 py-6 bg-slate-900 text-white rounded-[2rem] font-black text-xl hover:bg-slate-800 transition-all shadow-2xl">
                 Start Free Integration
              </Link>
              <Link href="/dashboard" className="px-12 py-6 bg-slate-50 text-slate-900 rounded-[2rem] font-bold text-xl hover:bg-slate-100 transition-all">
                 System Overview
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
       <div className="absolute inset-x-0 inset-y-10 bg-slate-200/20 rounded-[3rem] blur-3xl transform translate-z-[-100px] scale-90" />
       
       {/* Main Glass Console Pane */}
       <motion.div 
         className="relative w-full max-w-[520px] bg-white/40 backdrop-blur-3xl border border-white/60 rounded-[3rem] shadow-[0_50px_100px_-20px_rgba(0,0,0,0.1)] overflow-hidden p-8 space-y-8 preserve-3d"
       >
          {/* Dashboard Header UI */}
          <div className="flex items-center justify-between">
             <div className="flex gap-1.5">
                <div className="w-2.5 h-2.5 rounded-full bg-rose-400" />
                <div className="w-2.5 h-2.5 rounded-full bg-amber-400" />
                <div className="w-2.5 h-2.5 rounded-full bg-emerald-400" />
             </div>
             <div className="text-[10px] font-black text-slate-400 uppercase tracking-widest bg-slate-50 px-3 py-1 rounded-full border border-slate-100">
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
             <div className="col-span-12 lg:col-span-5 border-l border-slate-100 pl-8">
                <LiveLogFeed />
             </div>
          </div>

          {/* Bottom Summary Bar */}
          <div className="pt-8 border-t border-slate-100 flex items-center justify-between">
             <div className="flex items-center gap-3">
                <div className="w-10 h-10 rounded-xl bg-blue-600 flex items-center justify-center text-white shadow-lg shadow-blue-200 overflow-hidden">
                   <Image src="/logo2.png" alt="Veridex AI" width={24} height={24} className="w-6 h-6 object-contain" />
                </div>
                <div>
                   <p className="text-[10px] font-bold text-slate-400 uppercase tracking-tight">Active Protocol</p>
                   <p className="text-xs font-black text-slate-800">IDENTITY_VERIFICATION_COMPLETE</p>
                </div>
             </div>
             <div className="flex items-center gap-2 px-3 py-1.5 bg-emerald-50 text-emerald-600 rounded-lg">
                <CheckCircle2 className="w-4 h-4" />
                <span className="text-[10px] font-black uppercase">Secure</span>
             </div>
          </div>
       </motion.div>

       {/* Floating Biometric Detail */}
       <motion.div 
         animate={{ y: [0, -15, 0] }}
         transition={{ duration: 6, repeat: Infinity, ease: "easeInOut" }}
         className="absolute -right-12 top-1/2 -translate-y-1/2 w-48 bg-white/90 backdrop-blur-xl border border-slate-100 p-6 rounded-[2.5rem] shadow-2xl z-20 space-y-4"
       >
          <div className="text-[10px] font-black text-blue-600 uppercase tracking-widest">Biometric Mesh</div>
          <div className="h-32 w-full bg-slate-50 rounded-2xl flex items-center justify-center relative overflow-hidden group">
             <Fingerprint className="w-12 h-12 text-blue-500 relative z-10" />
             <div className="absolute inset-0 bg-gradient-to-t from-blue-500/10 to-transparent" />
             <motion.div 
               animate={{ y: [-50, 100] }}
               transition={{ duration: 3, repeat: Infinity, ease: "linear" }}
               className="absolute top-0 left-0 w-full h-1 bg-blue-400 blur-sm"
             />
          </div>
          <p className="text-[10px] font-bold text-slate-400 leading-tight">68 LANDMARKS IDENTIFIED ACROSS VECTOR PLANE.</p>
       </motion.div>
    </motion.div>
  );
}

function DocumentScanner() {
  return (
    <div className="relative group perspective">
       {/* Mockup ID Card */}
       <div className="w-full aspect-[1.6/1] bg-slate-50 rounded-2xl border-2 border-slate-200 p-6 space-y-4 relative overflow-hidden group-hover:border-blue-400 transition-colors">
          <div className="flex justify-between items-start">
             <div className="w-12 h-14 bg-slate-200 rounded-lg animate-pulse" />
             <div className="space-y-2 flex-1 ml-4">
                <div className="h-3 w-3/4 bg-slate-200 rounded-full" />
                <div className="h-2 w-1/2 bg-slate-200 rounded-full" />
                <div className="h-2 w-2/3 bg-slate-100 rounded-full" />
             </div>
             <div className="w-10 h-10 bg-slate-100 rounded-full" />
          </div>
          
          <div className="space-y-3 pt-4">
             <div className="h-2 w-full bg-slate-200 rounded-full" />
             <div className="h-2 w-full bg-slate-200 rounded-full" />
             <div className="h-6 w-3/4 bg-slate-100 rounded-lg flex items-center px-3">
                <div className="h-1.5 w-full bg-slate-200 rounded-full" />
             </div>
          </div>

          {/* The SVG Scan Beam */}
          <motion.div 
            animate={{ top: ['-10%', '110%'] }}
            transition={{ duration: 4, repeat: Infinity, ease: [0.4, 0, 0.2, 1] }}
            className="absolute left-0 w-full h-12 bg-gradient-to-b from-transparent via-blue-500/20 to-transparent pointer-events-none z-10"
          >
             <div className="w-full h-px bg-blue-500 shadow-[0_0_15px_rgba(59,130,246,0.8)]" />
          </motion.div>

          <AnimatePresence>
             <motion.div 
               initial={{ opacity: 0 }}
               whileInView={{ opacity: 1 }}
               className="absolute inset-0 bg-blue-600/5 mix-blend-overlay pointer-events-none"
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
           className="text-[9px] font-mono font-bold text-blue-600 uppercase tracking-tight"
         >
            {log}
         </motion.div>
       ))}
    </div>
  );
}

function MiniStat({ label, value, color }: any) {
  const colors = {
    blue: "bg-blue-50 text-blue-600",
    emerald: "bg-emerald-50 text-emerald-600"
  } as any;

  return (
    <div className={cn("p-4 rounded-2xl border border-slate-100", colors[color])}>
       <p className="text-[10px] font-black uppercase opacity-60 tracking-widest">{label}</p>
       <h4 className="text-lg font-black">{value}</h4>
    </div>
  );
}

function StandardCard({ title, desc, icon, active = false }: any) {
  return (
    <div className={cn(
      "p-1.5 rounded-[3rem] border transition-all duration-500 transform hover:-translate-y-2",
      active ? "bg-blue-600 border-blue-500 text-white" : "bg-white/5 border-white/10 text-white"
    )}>
       <div className="bg-slate-900 p-10 rounded-[2.8rem] space-y-6 flex flex-col items-center text-center h-full">
          <div className={cn(
             "w-16 h-16 rounded-2xl flex items-center justify-center mb-2",
             active ? "bg-white/10 text-white" : "bg-blue-500/10 text-blue-500"
          )}>
             {icon}
          </div>
          <div className="space-y-3 flex-1">
             <h3 className="text-2xl font-black italic tracking-tighter">{title}</h3>
             <p className={cn(
                "text-sm font-medium leading-relaxed",
                active ? "text-white/60" : "text-slate-500"
             )}>{desc}</p>
          </div>
       </div>
    </div>
  );
}

function LayeredWaveDivider() {
  const { scrollYProgress } = useScroll();
  const wave1X = useTransform(scrollYProgress, [0, 1], ["-10%", "10%"]);

  return (
    <div className="absolute bottom-0 left-0 w-full h-32 pointer-events-none overflow-hidden z-20">
      <motion.svg style={{ x: wave1X }} className="absolute bottom-0 w-[120%] h-48 opacity-20" viewBox="0 0 1440 320" preserveAspectRatio="none">
        <path d="M0,160L48,176C96,192,192,224,288,224C384,224,480,192,576,165.3C672,139,768,117,864,128C960,139,1056,181,1152,197.3C1248,213,1344,203,1392,197.3L1440,192L1440,320L1392,320C1344,320,1248,320,1152,320C1056,320,960,320,864,320C768,320,672,320,576,320C480,320,384,320,288,320C192,320,96,320,48,320L0,320Z" fill="#0f172a" />
      </motion.svg>
      <div className="absolute bottom-0 left-0 w-full h-12 bg-[#0f172a]" />
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


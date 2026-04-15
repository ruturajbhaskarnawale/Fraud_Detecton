"use client";
import Link from 'next/link';
import Image from 'next/image';
import { motion, useScroll, useTransform, useSpring, useMotionValue } from 'framer-motion';
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
  CheckCircle2,
  ChevronRight,
  Database,
  Layers,
  SearchCode
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
    <div ref={containerRef} className="flex flex-col relative">
      {/* Hero Section */}
      <section className="relative min-h-screen flex items-center justify-center pt-20 pb-24 px-6 overflow-hidden bg-[#f8fafc]">
        {/* Interactive Background */}
        <motion.div 
          style={{ y: backgroundY }}
          className="absolute inset-0 -z-10"
        >
          <div className="absolute top-[-10%] left-[-10%] w-[50%] h-[50%] bg-blue-400/10 blur-[120px] rounded-full" />
          <div className="absolute bottom-[10%] right-[-5%] w-[40%] h-[40%] bg-indigo-400/10 blur-[100px] rounded-full" />
        </motion.div>

        <div className="max-w-7xl mx-auto w-full grid grid-cols-1 lg:grid-cols-2 gap-12 items-center relative z-10">
          {/* Left Column: Messaging */}
          <motion.div 
            style={{ y: textY, opacity }}
            className="space-y-10 text-center lg:text-left"
          >
            <motion.div 
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              className="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-blue-50 text-blue-700 text-[10px] font-black tracking-[0.2em] uppercase border border-blue-100/50"
            >
              <Zap className="w-3 h-3 fill-current" />
              <span>Autonomy in Identity</span>
            </motion.div>
            
            <div className="space-y-4">
              <h1 className="text-6xl md:text-8xl font-black tracking-tighter text-slate-900 leading-[0.85] perspective">
                <AnimatedText text="Verify Humans." className="block" />
                <span className="gradient-text block relative">
                   <AnimatedText text="Detect Fraud." delay={0.5} />
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
              className="max-w-xl mx-auto lg:mx-0 text-lg text-slate-700 font-medium leading-relaxed"
            >
              Industrial-grade document forensic, biometric match, and real-time fraud telemetry. Secure your ecosystem with Veridex.
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
                  <span>Start Verification</span>
                  <ArrowRight className="w-5 h-5 group-hover:translate-x-1 transition-transform" />
                </Link>
              </MagneticButton>
              <Link 
                href="/dashboard" 
                className="px-8 py-5 bg-white text-slate-900 border border-slate-200 rounded-2xl font-bold text-lg hover:bg-slate-50 transition-all flex items-center justify-center gap-2"
              >
                Access Dashboard
              </Link>
            </motion.div>

            {/* Trusted By */}
            <motion.div 
              initial={{ opacity: 0 }}
              animate={{ opacity: 0.4 }}
              transition={{ delay: 1.8 }}
              className="pt-8 flex flex-wrap justify-center lg:justify-start items-center gap-8 text-slate-400 font-black tracking-tighter text-sm uppercase"
            >
               <span className="flex items-center gap-1.5"><Globe className="w-4 h-4"/> Nexus</span>
               <span className="flex items-center gap-1.5"><Lock className="w-4 h-4"/> Secure</span>
               <span className="flex items-center gap-1.5"><Activity className="w-4 h-4"/> Live Audit</span>
            </motion.div>
          </motion.div>

          {/* Right Column: Visual Component */}
          <div className="hidden lg:block relative perspective">
             <IdentityCluster scrollYProgress={scrollYProgress} />
          </div>
        </div>

        {/* New Layered Wave Divider */}
        <LayeredWaveDivider />
      </section>

      {/* How it Works: Section 2 */}
      <section className="py-32 px-6 bg-[#0f172a] text-white relative overflow-visible z-10">
        {/* Ambient Glows */}
        <div className="absolute top-1/4 left-1/4 w-[30%] h-[30%] bg-blue-600/10 blur-[120px] rounded-full pointer-events-none" />
        <div className="absolute bottom-1/4 right-1/4 w-[30%] h-[30%] bg-indigo-600/10 blur-[120px] rounded-full pointer-events-none" />

        <div className="max-w-7xl mx-auto space-y-24 relative z-10">
          <motion.div 
            initial={{ opacity: 0, y: 30 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true, margin: "-100px" }}
            className="text-center space-y-6"
          >
            <div className="inline-flex items-center gap-2 px-3 py-1 bg-white/5 rounded-full text-[10px] font-black tracking-widest text-slate-400 uppercase border border-white/10">
               <Activity className="w-3 h-3" />
               Automated Pipeline
            </div>
            <h2 className="text-5xl md:text-7xl font-black tracking-tighter italic">Three Steps to <span className="text-blue-500 not-italic">Certainty.</span></h2>
            <p className="text-slate-400 max-w-2xl mx-auto font-medium text-lg">Our neural network handles the complexity, delivering forensic-grade results in milliseconds.</p>
          </motion.div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-8 relative">
            {/* Animated Connector Line (Desktop) */}
            <div className="hidden md:block absolute top-1/2 left-[15%] right-[15%] h-px bg-gradient-to-r from-transparent via-blue-500/30 to-transparent -translate-y-12 -z-10" />

            {[
              { 
                step: "01", 
                title: "Asset Handshake", 
                desc: "Securely transmit Aadhaar, PAN, or Passport imagery via our encrypted high-speed portal.",
                icon: <Zap className="w-8 h-8 text-blue-500" />
              },
              { 
                step: "02", 
                title: "Neural Synthesis", 
                desc: "Proprietary AI clusters execute deep OCR extraction and distance-vector match forensics.",
                icon: <Cpu className="w-8 h-8 text-indigo-500" />
              },
              { 
                step: "03", 
                title: "Protocol Verdict", 
                desc: "Final decision logic computed with sub-pixel precision reports relayed back to your node.",
                icon: <ShieldCheck className="w-8 h-8 text-emerald-500" />
              }
            ].map((item, i) => (
              <motion.div 
                key={i} 
                initial={{ opacity: 0, scale: 0.9, y: 30 }}
                whileInView={{ opacity: 1, scale: 1, y: 0 }}
                viewport={{ once: true, margin: "-50px" }}
                transition={{ delay: i * 0.2, duration: 0.8 }}
                className="group relative"
              >
                <div className="p-1.5 rounded-[3rem] bg-gradient-to-b from-white/10 to-transparent border border-white/5 h-full transition-transform hover:-translate-y-2">
                   <div className="bg-slate-900/40 backdrop-blur-xl p-10 rounded-[2.8rem] space-y-8 h-full flex flex-col items-center text-center">
                      <div className="relative">
                         <div className="w-20 h-20 bg-slate-800 rounded-3xl flex items-center justify-center group-hover:bg-blue-600 transition-all duration-500 group-hover:rotate-6 shadow-2xl overflow-hidden">
                            <div className="absolute inset-0 bg-blue-500/10 opacity-0 group-hover:opacity-100 transition-opacity" />
                            {item.icon}
                         </div>
                         <span className="absolute -top-4 -right-4 text-4xl font-black text-white/10 group-hover:text-blue-500/20 transition-colors italic">{item.step}</span>
                      </div>
                      <div className="space-y-3 flex-1">
                        <h3 className="text-2xl font-black tracking-tight">{item.title}</h3>
                        <p className="text-slate-400 font-medium leading-relaxed text-sm">{item.desc}</p>
                      </div>
                   </div>
                </div>
              </motion.div>
            ))}
          </div>
        </div>

        {/* Geometric Slant Divider: Section 2 -> 3 */}
        <div className="absolute -bottom-24 left-0 w-full h-48 bg-[#f8fafc] -skew-y-3 origin-bottom-left -z-10 border-t border-slate-100" />
      </section>

      {/* Features Grid: Section 3 (Bento Overhaul) */}
      <section className="py-40 px-6 bg-[#f8fafc] overflow-visible relative">
        <div className="max-w-7xl mx-auto space-y-24 pt-12">
          <motion.div 
            initial={{ opacity: 0, x: -30 }}
            whileInView={{ opacity: 1, x: 0 }}
            viewport={{ once: true }}
            className="flex flex-col md:flex-row md:items-end justify-between gap-8"
          >
            <div className="space-y-6 max-w-2xl">
              <div className="inline-flex items-center gap-2 text-blue-600 font-black tracking-[0.2em] text-[10px] uppercase">
                 <ShieldCheck className="w-4 h-4" />
                 Product Core
              </div>
              <h2 className="text-5xl md:text-8xl font-black tracking-tighter text-slate-900 italic leading-[0.8]">Security that <br/><span className="text-blue-600 not-italic">outpaces fraud.</span></h2>
              <p className="text-xl text-slate-600 font-medium max-w-xl">Built on top of sub-pixel precision OCR and distance-metric face verification labs.</p>
            </div>
          </motion.div>

          <div className="grid grid-cols-1 md:grid-cols-6 gap-6">
             <BentoCard 
               className="md:col-span-4"
               title="Multi-Signal OCR"
               desc="Our proprietary extraction engine identifies text, font weights, and field positioning with 99.8% precision. It handles over 14+ Indian ID variations with sub-pixel alignment detection."
               icon={<SearchCode className="w-10 h-10" />}
             />
             <BentoCard 
               className="md:col-span-2"
               title="Biometric Vectoring"
               desc="Map 68 facial landmarks to verify presence and detect deepfakes."
               icon={<Fingerprint className="w-10 h-10" />}
               variant="blue"
             />
             <BentoCard 
               className="md:col-span-3"
               title="Fraud Heatmaps"
               desc="Visual breakdown of font inconsistencies and sub-surface manipulation."
               icon={<Layers className="w-10 h-10" />}
             />
             <BentoCard 
               className="md:col-span-3"
               title="Compliance Ready"
               desc="GDPR & DPDP built-in with zero-persistence processing."
               icon={<Lock className="w-10 h-10" />}
               variant="dark"
             />
          </div>
        </div>

        {/* Faded Radiance Transition: Section 3 -> CTA */}
        <div className="absolute bottom-0 left-0 w-full h-64 bg-gradient-to-t from-blue-600 to-transparent opacity-20 pointer-events-none" />
      </section>

      {/* CTA Section */}
      <section className="py-40 px-6 bg-blue-600 relative overflow-hidden">
        <div className="absolute top-0 right-0 w-[40%] h-full bg-white opacity-5 -skew-x-12 translate-x-1/2" />
        <div className="max-w-4xl mx-auto text-center space-y-10 relative z-10">
          <h2 className="text-5xl md:text-8xl font-black text-white tracking-tighter leading-none">Ready to secure <br/>your ecosystem?</h2>
          <div className="flex flex-col sm:flex-row items-center justify-center gap-6">
            <Link 
              href="/verify" 
              className="px-12 py-6 bg-white text-blue-600 rounded-2xl font-black text-xl hover:bg-slate-50 transition-all shadow-2xl shadow-blue-900/20"
            >
              Start Free Trial
            </Link>
          </div>
        </div>
      </section>
    </div>
  );
}

// Support Components

function LayeredWaveDivider() {
  const { scrollYProgress } = useScroll();
  
  // Parallax layers for the waves
  const wave1X = useTransform(scrollYProgress, [0, 1], ["-10%", "10%"]);
  const wave2X = useTransform(scrollYProgress, [0, 1], ["10%", "-10%"]);
  const wave3X = useTransform(scrollYProgress, [0, 1], ["-5%", "5%"]);

  return (
    <div className="absolute bottom-0 left-0 w-full h-48 pointer-events-none overflow-hidden z-20">
      {/* Wave Layer 1: Base */}
      <motion.svg 
        style={{ x: wave1X }}
        className="absolute bottom-0 w-[120%] h-48 opacity-20" 
        viewBox="0 0 1440 320" 
        preserveAspectRatio="none"
      >
        <path d="M0,160L48,176C96,192,192,224,288,224C384,224,480,192,576,165.3C672,139,768,117,864,128C960,139,1056,181,1152,197.3C1248,213,1344,203,1392,197.3L1440,192L1440,320L1392,320C1344,320,1248,320,1152,320C1056,320,960,320,864,320C768,320,672,320,576,320C480,320,384,320,288,320C192,320,96,320,48,320L0,320Z" fill="#0f172a" />
      </motion.svg>

      {/* Wave Layer 2: Mid */}
      <motion.svg 
        style={{ x: wave2X }}
        className="absolute bottom-0 w-[120%] h-32 opacity-40 ml-[-10%]" 
        viewBox="0 0 1440 320" 
        preserveAspectRatio="none"
      >
        <path d="M0,96L60,106.7C120,117,240,139,360,138.7C480,139,600,117,720,122.7C840,128,960,160,1080,160C1200,160,1320,128,1380,112L1440,96L1440,320L1380,320C1320,320,1200,320,1080,320C960,320,840,320,720,320C600,320,480,320,360,320C240,320,120,320,60,320L0,320Z" fill="#0f172a" />
      </motion.svg>

      {/* Wave Layer 3: Top (Main Section Color) */}
      <motion.svg 
        style={{ x: wave3X }}
        className="absolute bottom-0 w-[110%] h-24" 
        viewBox="0 0 1440 320" 
        preserveAspectRatio="none"
      >
        <path d="M0,224L80,213.3C160,203,320,181,480,192C640,203,800,245,960,245.3C1120,245,1280,203,1360,181.3L1440,160L1440,320L1360,320C1280,320,1120,320,960,320C800,320,640,320,480,320C320,320,160,320,80,320L0,320Z" fill="#0f172a" />
      </motion.svg>
    </div>
  );
}

function BentoCard({ title, desc, icon, className = "", variant = "white" }: { title: string, desc: string, icon: any, className?: string, variant?: "white" | "blue" | "dark" }) {
  const variants = {
    white: "bg-white text-slate-900 border-slate-200",
    blue: "bg-blue-600 text-white border-blue-500",
    dark: "bg-slate-900 text-white border-slate-800"
  };

  return (
    <motion.div
      initial={{ opacity: 0, y: 30 }}
      whileInView={{ opacity: 1, y: 0 }}
      viewport={{ once: true }}
      className={cn("perspective preserve-3d group cursor-pointer", className)}
    >
      <div className={cn("p-10 rounded-2xl border h-full transition-all flex flex-col justify-between relative overflow-hidden shadow-sm hover:shadow-xl hover:border-blue-200", variants[variant])}>
         <div className="space-y-6">
            <div className={cn("w-12 h-12 rounded-xl flex items-center justify-center transition-transform group-hover:scale-110", variant === 'white' ? 'bg-blue-50 text-blue-600' : 'bg-white/10 text-white')}>
               {icon}
            </div>
            <div className="space-y-3">
               <h3 className="text-xl font-bold tracking-tight">{title}</h3>
               <p className={cn("text-sm font-medium leading-relaxed opacity-70", variant === 'white' ? 'text-slate-600' : 'text-white/80')}>{desc}</p>
            </div>
         </div>
         <div className="pt-6">
            <div className={cn("w-8 h-8 rounded-full border flex items-center justify-center opacity-0 group-hover:opacity-100 translate-x-4 group-hover:translate-x-0 transition-all", variant === 'white' ? 'border-slate-200 text-blue-600' : 'border-white/20 text-white')}>
               <ArrowRight className="w-4 h-4" />
            </div>
         </div>
      </div>
    </motion.div>
  );
}

function AnimatedText({ text, delay = 0, className = "" }: { text: string, delay?: number, className?: string }) {
  const words = text.split(" ");
  
  return (
    <span className={className}>
      {words.map((word, i) => (
        <motion.span
          key={i}
          initial={{ opacity: 0, y: 40 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ 
            delay: delay + (i * 0.1), 
            duration: 0.8, 
            ease: [0.2, 0.65, 0.3, 0.9] 
          }}
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
    const centerX = rect.left + rect.width / 2;
    const centerY = rect.top + rect.height / 2;
    x.set((e.clientX - centerX) * 0.35);
    y.set((e.clientY - centerY) * 0.35);
  };

  const handleMouseLeave = () => {
    x.set(0);
    y.set(0);
  };

  return (
    <motion.div
      style={{ x: springX, y: springY }}
      onMouseMove={handleMouseMove}
      onMouseLeave={handleMouseLeave}
    >
      {children}
    </motion.div>
  );
}

function IdentityCluster({ scrollYProgress }: { scrollYProgress: any }) {
  const mouseX = useMotionValue(0);
  const mouseY = useMotionValue(0);
  
  const rotateX = useSpring(useTransform(mouseY, [-300, 300], [15, -15]));
  const rotateY = useSpring(useTransform(mouseX, [-300, 300], [-15, 15]));
  
  const scrollRotate = useTransform(scrollYProgress, [0, 1], [0, 45]);
  const scrollY = useTransform(scrollYProgress, [0, 1], [0, -200]);

  useEffect(() => {
    const handleMouse = (e: MouseEvent) => {
      mouseX.set(e.clientX - window.innerWidth / 2);
      mouseY.set(e.clientY - window.innerHeight / 2);
    };
    window.addEventListener("mousemove", handleMouse);
    return () => window.removeEventListener("mousemove", handleMouse);
  }, [mouseX, mouseY]);

  // Coordinates for mesh connections
  const assets = [
    { id: 'identity', icon: <User/>, label: "Identity", x: -160, y: -120, delay: 0 },
    { id: 'biometrics', icon: <Fingerprint/>, label: "Biometrics", x: 180, y: -80, delay: 1 },
    { id: 'realtime', icon: <Activity/>, label: "Realtime", x: 140, y: 140, delay: 2 },
    { id: 'encryption', icon: <Lock/>, label: "Encryption", x: -180, y: 120, delay: 0.5 },
  ];

  return (
    <motion.div 
      style={{ rotateX, rotateY, y: scrollY }}
      className="relative w-full aspect-square flex items-center justify-center preserve-3d"
    >
      {/* Background Data Cloud */}
      <DataNodeCloud />

      {/* Radar Scanning Pulses */}
      <RadarPulse />

      {/* Neural Mesh Connections */}
      <svg className="absolute inset-0 w-full h-full pointer-events-none z-10" viewBox="-300 -300 600 600 overflow-visible">
        <defs>
          <linearGradient id="lineGradient" x1="0%" y1="0%" x2="100%" y2="100%">
            <stop offset="0%" stopColor="rgba(59, 130, 246, 0.4)" />
            <stop offset="100%" stopColor="rgba(59, 130, 246, 0.05)" />
          </linearGradient>
          <filter id="glow">
             <feGaussianBlur stdDeviation="2" result="coloredBlur"/>
             <feMerge>
                <feMergeNode in="coloredBlur"/>
                <feMergeNode in="SourceGraphic"/>
             </feMerge>
          </filter>
        </defs>
        
        {assets.map((asset, i) => (
          <g key={`mesh-${i}`}>
            {/* Base Connection Line */}
            <motion.line
              initial={{ pathLength: 0, opacity: 0 }}
              animate={{ pathLength: 1, opacity: 1 }}
              transition={{ delay: 1.5 + asset.delay, duration: 1.5, ease: "easeInOut" }}
              x1="0" y1="0" x2={asset.x} y2={asset.y}
              stroke="url(#lineGradient)"
              strokeWidth="1.5"
              strokeDasharray="4 4"
            />
            {/* Animated Data Pulse */}
            <motion.circle
              r="2.5"
              fill="#3b82f6"
              filter="url(#glow)"
              animate={{
                offsetDistance: ["0%", "100%"]
              }}
              transition={{
                duration: 3,
                repeat: Infinity,
                delay: asset.delay,
                ease: "linear"
              }}
              style={{
                offsetPath: `path('M 0 0 L ${asset.x} ${asset.y}')`
              }}
            />
          </g>
        ))}
      </svg>

      {/* Central Hub */}
      <motion.div 
        animate={{ scale: [1, 1.05, 1] }} 
        transition={{ duration: 4, repeat: Infinity }}
        className="relative w-48 h-48 flex items-center justify-center z-20"
      >
        {/* Core Glow */}
        <div className="absolute inset-0 bg-blue-500/10 blur-[60px] rounded-full animate-pulse" />
        <Image 
          src="/logo.png" 
          alt="Veridex Logo" 
          width={140} 
          height={140} 
          className="w-36 h-36 object-contain relative z-10" 
        />
      </motion.div>

      {/* Floating Asset Cards */}
      {assets.map((asset, i) => (
        <FloatingAsset 
          key={asset.id}
          icon={asset.icon} 
          label={asset.label} 
          x={asset.x} 
          y={asset.y} 
          delay={asset.delay} 
        />
      ))}
    </motion.div>
  );
}

function RadarPulse() {
  return (
    <div className="absolute inset-0 flex items-center justify-center pointer-events-none">
      {[1, 2, 3].map((i) => (
        <motion.div
          key={i}
          initial={{ scale: 0.5, opacity: 0 }}
          animate={{ scale: 2.5, opacity: [0, 0.2, 0] }}
          transition={{
            duration: 4,
            repeat: Infinity,
            delay: i * 1.3,
            ease: "easeOut"
          }}
          className="absolute w-64 h-64 border border-blue-400/30 rounded-full"
        />
      ))}
    </div>
  );
}

function DataNodeCloud() {
  const nodes = Array.from({ length: 20 });
  return (
    <div className="absolute inset-0 pointer-events-none opacity-20">
      {nodes.map((_, i) => (
        <motion.div
          key={i}
          initial={{ opacity: 0 }}
          animate={{ opacity: [0, 1, 0] }}
          transition={{
            duration: 2 + Math.random() * 3,
            repeat: Infinity,
            delay: Math.random() * 5
          }}
          style={{
            left: `${Math.random() * 100}%`,
            top: `${Math.random() * 100}%`,
          }}
          className="absolute w-1 h-1 bg-blue-300 rounded-full"
        />
      ))}
    </div>
  );
}

function FloatingAsset({ icon, label, x, y, delay }: { icon: any, label: string, x: number, y: number, delay: number }) {
  return (
    <motion.div
      initial={{ opacity: 0, scale: 0.8, x: 0, y: 0 }}
      animate={{ opacity: 1, scale: 1, x, y }}
      transition={{ 
        delay: 0.5 + delay, 
        type: "spring", 
        stiffness: 100, 
        damping: 15 
      }}
      className="absolute bg-white/40 backdrop-blur-2xl p-5 rounded-[2rem] shadow-[0_20px_50px_rgba(0,0,0,0.1)] flex items-center gap-4 border border-white/60 group hover:bg-blue-600 hover:text-white transition-all duration-500 cursor-default z-30 group"
    >
      <div className="relative">
        <div className="absolute inset-0 bg-blue-400/20 blur-lg rounded-full opacity-0 group-hover:opacity-100 transition-opacity" />
        <div className="text-blue-600 group-hover:text-white transition-colors relative z-10">{icon}</div>
      </div>
      <div className="flex flex-col">
        <span className="text-[10px] font-black uppercase tracking-[0.2em] opacity-40 group-hover:opacity-60">{label}</span>
        <span className="text-[9px] font-bold text-blue-600/80 group-hover:text-white/80 uppercase">Verified</span>
      </div>
      
      {/* Small Connector dot */}
      <div className="absolute -left-1.5 top-1/2 -translate-y-1/2 w-3 h-3 bg-white rounded-full border-2 border-blue-400 opacity-0 group-hover:opacity-100 transition-opacity" />
    </motion.div>
  );
}


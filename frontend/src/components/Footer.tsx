import Link from 'next/link';
import Image from 'next/image';
import { ShieldCheck, ArrowRight } from 'lucide-react';

export default function Footer() {
  return (
    <footer className="relative bg-slate-950 pt-24 pb-16 px-6 overflow-hidden border-t border-slate-800">
      {/* Subtle glow background */}
      <div className="absolute top-0 left-1/2 -translate-x-1/2 w-full h-px bg-gradient-to-r from-transparent via-blue-500/50 to-transparent" />
      
      <div className="max-w-7xl mx-auto grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-12 relative z-10">
         {/* Column 1: Branding */}
         <div className="lg:col-span-2 space-y-6">
            <div className="flex items-center gap-2">
               <Image src="/logo2.png" alt="Veridex AI" width={32} height={32} className="w-8 h-8 object-contain" />
               <span className="text-2xl font-black tracking-tighter italic text-white">Veridex<span className="text-blue-500 not-italic">.</span></span>
            </div>
            <p className="max-w-xs text-sm font-medium text-slate-400 leading-relaxed">
               Industrial-grade identity verification for high-stakes environments. Autonomy in trust, powered by forensics.
            </p>
         </div>

         {/* Column 2: RESOURCES */}
         <div className="space-y-6">
            <h4 className="text-[10px] font-black text-slate-500 uppercase tracking-[0.3em]">Resources</h4>
            <nav className="flex flex-col gap-4">
               <FooterLink href="/documentation">Documentation</FooterLink>
               <FooterLink href="/api-reference">API Reference</FooterLink>
               <FooterLink href="/status">System Status</FooterLink>
            </nav>
         </div>

         {/* Column 3: LEGAL */}
         <div className="space-y-6">
            <h4 className="text-[10px] font-black text-slate-500 uppercase tracking-[0.3em]">Legal</h4>
            <nav className="flex flex-col gap-4">
               <FooterLink href="/privacy" arrow>Privacy Policy</FooterLink>
               <FooterLink href="/security">Security Protocol</FooterLink>
               <FooterLink href="/cookies">Cookie Policy</FooterLink>
            </nav>
         </div>
      </div>

      <div className="max-w-7xl mx-auto mt-24 pt-8 border-t border-white/5 flex flex-col items-center justify-center gap-4">
         <p className="text-[10px] font-bold text-slate-600 uppercase tracking-[0.3em]">
           © 2026 Veridex AI • All Verification Rights Reserved
         </p>
      </div>
    </footer>
  );
}

function FooterLink({ href, children, arrow = false }: { href: string, children: React.ReactNode, arrow?: boolean }) {
  return (
    <Link 
      href={href} 
      className="text-lg font-black text-white hover:text-blue-500 transition-colors flex items-center gap-1.5 group font-sans tracking-tight"
    >
      {children}
      {arrow && <ArrowRight className="w-4 h-4 text-slate-600 group-hover:text-blue-500 transition-colors" />}
    </Link>
  );
}

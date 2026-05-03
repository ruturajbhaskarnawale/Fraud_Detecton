import Link from 'next/link';
import Image from 'next/image';
import { ShieldCheck, ArrowRight, Twitter, Github, Linkedin, Mail, Globe, Lock, Cpu } from 'lucide-react';

export default function Footer() {
  return (
    <footer className="relative bg-background pt-32 pb-16 px-6 overflow-hidden border-t border-border">
      {/* Background decoration */}
      <div className="absolute top-0 left-1/4 w-1/2 h-px bg-gradient-to-r from-transparent via-blue-500/50 to-transparent" />
      <div className="absolute bottom-0 right-0 w-[500px] h-[500px] bg-blue-600/5 blur-[120px] rounded-full -mr-64 -mb-64" />
      
      <div className="max-w-7xl mx-auto relative z-10">
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-12 gap-16 lg:gap-8">
          
          {/* Brand Identity */}
          <div className="lg:col-span-4 space-y-8">
            <div className="flex items-center gap-3">
               <div className="p-2 bg-blue-600 rounded-xl shadow-lg shadow-blue-500/20">
                 <Image src="/logo2.png" alt="Veridex AI" width={32} height={32} className="w-8 h-8 object-contain invert" />
               </div>
               <span className="text-3xl font-black tracking-tighter text-foreground font-outfit uppercase italic">
                 Veridex<span className="text-blue-500 not-italic">.</span>
               </span>
            </div>
            <p className="max-w-sm text-lg font-medium text-muted-foreground leading-relaxed">
               Next-generation identity infrastructure for high-growth platforms. Military-grade forensics, sub-second latency.
            </p>
            <div className="flex items-center gap-4">
              <SocialLink href="#" icon={Twitter} />
              <SocialLink href="#" icon={Github} />
              <SocialLink href="#" icon={Linkedin} />
              <SocialLink href="#" icon={Mail} />
            </div>
          </div>

          {/* Navigation Matrix */}
          <div className="lg:col-span-8 grid grid-cols-2 sm:grid-cols-3 gap-12">
            <div className="space-y-6">
              <h4 className="text-xs font-black text-foreground uppercase tracking-[0.2em]">Platform</h4>
              <nav className="flex flex-col gap-4">
                <FooterLink href="/solutions">Solutions</FooterLink>
                <FooterLink href="/features">Features</FooterLink>
                <FooterLink href="/security">Security</FooterLink>
                <FooterLink href="/pricing">Enterprise</FooterLink>
              </nav>
            </div>

            <div className="space-y-6">
              <h4 className="text-xs font-black text-foreground uppercase tracking-[0.2em]">Developers</h4>
              <nav className="flex flex-col gap-4">
                <FooterLink href="/documentation">API Docs</FooterLink>
                <FooterLink href="/status">System Status</FooterLink>
                <FooterLink href="/changelog">Changelog</FooterLink>
                <FooterLink href="/verify">Demo Lab</FooterLink>
              </nav>
            </div>

            <div className="space-y-6">
              <h4 className="text-xs font-black text-foreground uppercase tracking-[0.2em]">Company</h4>
              <nav className="flex flex-col gap-4">
                <FooterLink href="/privacy">Privacy</FooterLink>
                <FooterLink href="/terms">Terms</FooterLink>
                <FooterLink href="/compliance">Compliance</FooterLink>
                <FooterLink href="/cookies">Cookies</FooterLink>
              </nav>
            </div>
          </div>
        </div>

        {/* Bottom Bar */}
        <div className="mt-32 pt-12 border-t border-border flex flex-col md:flex-row items-center justify-between gap-8">
           <div className="flex items-center gap-6">
              <div className="flex items-center gap-2 text-emerald-500">
                <div className="w-2 h-2 rounded-full bg-current animate-pulse" />
                <span className="text-[10px] font-black uppercase tracking-widest">Global Status: Operational</span>
              </div>
              <div className="w-px h-4 bg-border" />
              <span className="text-[10px] font-bold text-muted-foreground uppercase tracking-widest">v4.2.1-forensic</span>
           </div>
           
           <p className="text-[10px] font-black text-muted-foreground uppercase tracking-[0.3em]">
             © 2026 VERIDEX AI • ALL RIGHTS RESERVED.
           </p>
        </div>
      </div>
    </footer>
  );
}

function FooterLink({ href, children }: { href: string, children: React.ReactNode }) {
  return (
    <Link 
      href={href} 
      className="text-sm font-bold text-muted-foreground hover:text-foreground transition-all flex items-center gap-2 group"
    >
      <div className="w-0 h-0.5 bg-blue-500 transition-all group-hover:w-3" />
      {children}
    </Link>
  );
}

function SocialLink({ href, icon: Icon }: { href: string, icon: any }) {
  return (
    <Link 
      href={href} 
      className="w-10 h-10 rounded-xl bg-card border border-border flex items-center justify-center text-muted-foreground hover:text-foreground hover:bg-blue-600 hover:border-blue-500 transition-all group"
    >
      <Icon className="w-5 h-5 transition-transform group-hover:scale-110" />
    </Link>
  );
}

"use client";
import Link from 'next/link';
import Image from 'next/image';
import { ShieldCheck, ArrowRight, Menu, X, Terminal, Fingerprint, Activity } from 'lucide-react';
import { useState, useEffect } from 'react';
import { motion, useScroll, useTransform, AnimatePresence, useSpring } from 'framer-motion';
import { cn } from '@/lib/utils';
import { usePathname } from 'next/navigation';
import { ThemeToggle } from './ThemeToggle';

interface NavbarProps {
  variant?: 'marketing' | 'dashboard';
}

const navLinks = [
  { name: 'Solutions', href: '/solutions', icon: ShieldCheck },
  { name: 'Developers', href: '/dashboard', icon: Terminal },
  { name: 'Identity', href: '/verify', icon: Fingerprint },
  { name: 'Network', href: '/status', icon: Activity },
];

export default function Navbar({ variant = 'marketing' }: NavbarProps) {
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);
  const [scrolled, setScrolled] = useState(false);
  const pathname = usePathname();
  const { scrollY } = useScroll();
  const isMarketing = variant === 'marketing';

  // Smooth scroll listener
  useEffect(() => {
    const updateScrolled = () => {
      setScrolled(window.scrollY > 20);
    };
    window.addEventListener("scroll", updateScrolled);
    return () => window.removeEventListener("scroll", updateScrolled);
  }, []);

  const navHeight = scrolled ? "h-16" : "h-24";
  
  return (
    <motion.nav 
      initial={{ y: -100 }}
      animate={{ y: 0 }}
      transition={{ duration: 0.8, ease: "circOut" }}
      className={cn(
        "fixed top-0 w-full z-[100] transition-all duration-500 flex items-center",
        navHeight,
        scrolled 
          ? "bg-background/80 backdrop-blur-xl border-b border-border shadow-[0_4px_30px_rgba(0,0,0,0.1)]" 
          : "bg-transparent border-b border-transparent"
      )}
    >
      <div className="max-w-7xl mx-auto px-6 lg:px-8 w-full">
        <div className="flex justify-between items-center">
          {/* Logo Area */}
          <Link href="/" className="flex items-center space-x-3 group">
            <div className="relative">
              <div className="absolute inset-0 bg-blue-500 blur-lg opacity-0 group-hover:opacity-40 transition-opacity duration-500" />
              <Image 
                src="/logo2.png" 
                alt="Veridex Logo" 
                width={36} 
                height={36} 
                className="w-9 h-9 object-contain relative z-10 filter drop-shadow-[0_0_8px_rgba(59,130,246,0.5)]"
              />
            </div>
            <span className="text-2xl font-black tracking-tighter text-foreground font-outfit italic">
              VERIDEX<span className="text-blue-500 not-italic">.</span>
            </span>
          </Link>
          
          {/* Desktop Links */}
          <div className="hidden lg:flex items-center space-x-1">
            {navLinks.map((link) => (
              <Link 
                key={link.name}
                href={link.href}
                className={cn(
                  "px-4 py-2 rounded-xl text-sm font-bold transition-all flex items-center gap-2 group/link",
                  pathname === link.href 
                    ? "text-blue-400 bg-blue-500/10" 
                    : "text-slate-400 hover:text-white hover:bg-white/5"
                )}
              >
                <link.icon className={cn(
                  "w-4 h-4 transition-transform group-hover/link:scale-110",
                  pathname === link.href ? "text-blue-400" : "text-slate-500 group-hover/link:text-blue-400"
                )} />
                {link.name}
              </Link>
            ))}
            
            <div className="h-6 w-px bg-white/10 mx-4" />
            
            <div className="flex items-center gap-4">
               <ThemeToggle />
               {isMarketing ? (
                 <Link 
                   href="/verify" 
                   className="relative group px-6 py-2.5 bg-white text-slate-950 dark:bg-white dark:text-slate-950 rounded-xl text-sm font-black transition-all hover:scale-105 active:scale-95 shadow-[0_0_20px_rgba(255,255,255,0.2)] overflow-hidden"
                 >
                   <span className="relative z-10 flex items-center gap-2">
                     START VERIFYING
                     <ArrowRight className="w-4 h-4 transition-transform group-hover:translate-x-1" />
                   </span>
                   <div className="absolute inset-0 bg-gradient-to-r from-white via-blue-100 to-white opacity-0 group-hover:opacity-100 transition-opacity" />
                 </Link>
               ) : (
                 <Link 
                   href="/dashboard" 
                   className="px-6 py-2.5 bg-blue-600 text-white rounded-xl text-sm font-black hover:bg-blue-500 transition-all shadow-[0_0_20px_rgba(37,99,235,0.4)]"
                 >
                   DASHBOARD
                 </Link>
               )}
            </div>
          </div>

          {/* Mobile Toggle */}
          <div className="lg:hidden">
             <button 
               onClick={() => setMobileMenuOpen(!mobileMenuOpen)} 
               className="p-2 text-white bg-white/5 border border-white/10 rounded-xl transition-all hover:bg-white/10"
             >
                {mobileMenuOpen ? <X className="w-6 h-6" /> : <Menu className="w-6 h-6" />}
             </button>
          </div>
        </div>
      </div>

      {/* Mobile Menu */}
      <AnimatePresence>
        {mobileMenuOpen && (
          <motion.div 
            initial={{ opacity: 0, height: 0 }}
            animate={{ opacity: 1, height: 'auto' }}
            exit={{ opacity: 0, height: 0 }}
            className="absolute top-full left-0 w-full bg-slate-950/95 backdrop-blur-2xl border-b border-white/10 overflow-hidden lg:hidden"
          >
            <div className="p-6 space-y-4">
              {navLinks.map((link) => (
                <Link 
                  key={link.name}
                  href={link.href} 
                  onClick={() => setMobileMenuOpen(false)}
                  className="flex items-center gap-4 p-4 rounded-2xl bg-white/5 text-lg font-black text-white hover:bg-white/10 transition-colors"
                >
                  <link.icon className="w-6 h-6 text-blue-500" />
                  {link.name}
                </Link>
              ))}
              <Link 
                href="/verify" 
                onClick={() => setMobileMenuOpen(false)}
                className="flex items-center justify-center gap-2 w-full bg-blue-600 text-white p-5 rounded-2xl text-center font-black text-lg shadow-lg shadow-blue-500/20"
              >
                GET STARTED
                <ArrowRight className="w-5 h-5" />
              </Link>
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </motion.nav>
  );
}


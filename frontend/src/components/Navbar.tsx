"use client";
import Link from 'next/link';
import Image from 'next/image';
import { ShieldCheck, ArrowRight } from 'lucide-react';
import { useState } from 'react';
import { motion, useScroll, useTransform, AnimatePresence } from 'framer-motion';
import { cn } from '@/lib/utils';
import { usePathname } from 'next/navigation';

interface NavbarProps {
  variant?: 'marketing' | 'dashboard';
}

const navLinks = [
  { name: 'Verify', href: '/verify' },
  { name: 'Analytics', href: '/dashboard' },
  { name: 'History', href: '/history' },
];

export default function Navbar({ variant = 'marketing' }: NavbarProps) {
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);
  const pathname = usePathname();
  const { scrollY } = useScroll();
  const isMarketing = variant === 'marketing';

  // Subtle background transition on scroll
  const navBg = useTransform(
    scrollY, 
    [0, 50], 
    ["rgba(255, 255, 255, 0)", "rgba(255, 255, 255, 0.9)"]
  );
  
  const navBorder = useTransform(
    scrollY,
    [0, 50],
    ["rgba(255, 255, 255, 0)", "rgba(226, 232, 240, 1)"]
  );

  return (
    <motion.nav 
      style={{ backgroundColor: navBg, borderColor: navBorder }}
      className={cn(
        "fixed top-0 w-full z-50 transition-all backdrop-blur-md border-b h-16 flex items-center",
        !isMarketing && "bg-white border-slate-200"
      )}
    >
      <div className="max-w-7xl mx-auto px-6 lg:px-8 w-full">
        <div className="flex justify-between items-center">
          {/* Logo Area */}
          <Link href="/" className="flex items-center space-x-2 group">
            <Image 
              src="/logo.png" 
              alt="Veridex Logo" 
              width={28} 
              height={28} 
              className="w-7 h-7 object-contain"
            />
            <span className="text-xl font-bold text-slate-900 tracking-tight">
              VERI<span className="text-blue-600">DEX</span>
            </span>
          </Link>
          
          {/* Desktop Links */}
          <div className="hidden md:flex items-center space-x-6">
            {navLinks.map((link) => (
              <Link 
                key={link.name}
                href={link.href}
                className={cn(
                  "text-sm font-semibold transition-colors",
                  pathname === link.href ? "text-blue-600" : "text-slate-600 hover:text-slate-900"
                )}
              >
                {link.name}
              </Link>
            ))}
            
            <div className="flex items-center gap-4">
               {isMarketing && (
                 <Link 
                   href="/verify" 
                   className="bg-slate-900 text-white px-5 py-2 rounded-lg text-sm font-bold hover:bg-slate-800 transition-colors flex items-center gap-2 shadow-sm"
                 >
                   <span>Get Started</span>
                   <ArrowRight className="w-4 h-4" />
                 </Link>
               )}
            </div>
          </div>

          {/* Mobile Toggle Placeholder (Standardizing logic) */}
          <div className="md:hidden flex items-center">
             <button onClick={() => setMobileMenuOpen(!mobileMenuOpen)} className="text-slate-900">
                <div className="space-y-1.5">
                   <div className={cn("w-6 h-0.5 bg-current transition-all", mobileMenuOpen && "rotate-45 translate-y-2")} />
                   <div className={cn("w-6 h-0.5 bg-current transition-all", mobileMenuOpen && "opacity-0")} />
                   <div className={cn("w-6 h-0.5 bg-current transition-all", mobileMenuOpen && "-rotate-45 -translate-y-2")} />
                </div>
             </button>
          </div>
        </div>
      </div>

      {/* Mobile Menu */}
      <AnimatePresence>
        {mobileMenuOpen && (
          <motion.div 
            initial={{ opacity: 0, y: -10 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -10 }}
            className="absolute top-16 left-0 w-full bg-white border-b border-slate-200 shadow-xl p-6 space-y-4 md:hidden"
          >
            {navLinks.map((link) => (
              <Link 
                key={link.name}
                href={link.href} 
                onClick={() => setMobileMenuOpen(false)}
                className="block text-lg font-bold text-slate-900"
              >
                {link.name}
              </Link>
            ))}
            <Link 
              href="/verify" 
              onClick={() => setMobileMenuOpen(false)}
              className="block w-full bg-blue-600 text-white px-6 py-3 rounded-xl text-center font-bold"
            >
              Get Started
            </Link>
          </motion.div>
        )}
      </AnimatePresence>
    </motion.nav>
  );
}

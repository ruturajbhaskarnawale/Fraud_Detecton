import Link from 'next/link';
import { ShieldCheck, ArrowUpRight } from 'lucide-react';

export default function Footer() {
  return (
    <footer className="bg-slate-950 text-slate-400 py-16 px-6 border-t border-slate-900">
      <div className="max-w-7xl mx-auto space-y-12">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-12">
          {/* Brand Column */}
          <div className="col-span-1 md:col-span-1 space-y-6">
            <div className="flex items-center gap-2 text-white">
              <div className="bg-blue-600 p-1.5 rounded-lg">
                <ShieldCheck className="w-5 h-5 text-white" />
              </div>
              <span className="font-bold text-xl tracking-tight">Jotex <span className="text-blue-500">AI</span></span>
            </div>
            <p className="text-sm leading-relaxed font-medium max-w-xs">
              Industrial-grade document forensic and biometric verification solutions for high-growth modern enterprises.
            </p>
          </div>

          {/* Links Columns */}
          <div className="md:col-span-3 grid grid-cols-2 md:grid-cols-3 gap-8">
            <FooterGroup title="Platform" links={[
              { name: 'Identity Lab', href: '/verify' },
              { name: 'Intelligence Hub', href: '/dashboard' },
              { name: 'Audit History', href: '/history' },
            ]} />
            <FooterGroup title="Resources" links={[
              { name: 'Documentation', href: '#' },
              { name: 'API Reference', href: '#' },
              { name: 'System Status', href: '#' },
            ]} />
            <FooterGroup title="Legal" links={[
              { name: 'Privacy Policy', href: '#' },
              { name: 'Security Protocol', href: '#' },
              { name: 'Cookie Policy', href: '#' },
            ]} />
          </div>
        </div>

        <div className="pt-8 border-t border-slate-900 flex flex-col md:flex-row justify-between items-center gap-6 text-[10px] font-bold uppercase tracking-widest opacity-50">
          <p>© 2026 Jotex AI Labs. All rights reserved.</p>
          <div className="flex gap-8">
             <span>GDPR Compliant</span>
             <span>SOC2 Type II</span>
             <span>ISO 27001</span>
          </div>
        </div>
      </div>
    </footer>
  );
}

function FooterGroup({ title, links }: { title: string, links: { name: string, href: string }[] }) {
  return (
    <div className="space-y-4">
      <h4 className="text-white font-bold uppercase tracking-widest text-[10px] opacity-40">{title}</h4>
      <ul className="space-y-2">
        {links.map((link) => (
          <li key={link.name}>
            <Link href={link.href} className="group flex items-center gap-1 hover:text-white transition-all text-sm font-medium">
              {link.name}
              <ArrowUpRight className="w-3 h-3 opacity-0 group-hover:opacity-100 transition-all" />
            </Link>
          </li>
        ))}
      </ul>
    </div>
  );
}

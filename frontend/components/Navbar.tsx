import Link from 'next/link';
import { ShieldCheck, History, LayoutDashboard } from 'lucide-react';

export default function Navbar() {
  return (
    <nav className="fixed top-0 w-full z-50 bg-white/70 backdrop-blur-lg border-b border-slate-200">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between h-16 items-center">
          <Link href="/" className="flex items-center space-x-2">
            <div className="bg-blue-600 p-1.5 rounded-lg">
              <ShieldCheck className="w-6 h-6 text-white" />
            </div>
            <span className="text-xl font-bold text-slate-900 tracking-tight">CampusHub <span className="text-blue-600">ID Scan</span></span>
          </Link>
          
          <div className="flex space-x-6">
            <Link href="/" className="flex items-center space-x-1 text-sm font-medium text-slate-600 hover:text-blue-600 transition-colors">
              <LayoutDashboard className="w-4 h-4" />
              <span>Verifier</span>
            </Link>
            <Link href="/history" className="flex items-center space-x-1 text-sm font-medium text-slate-600 hover:text-blue-600 transition-colors">
              <History className="w-4 h-4" />
              <span>History</span>
            </Link>
          </div>
        </div>
      </div>
    </nav>
  );
}

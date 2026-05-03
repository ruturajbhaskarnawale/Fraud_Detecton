import { Eye } from 'lucide-react';
import { ReactNode } from 'react';

export interface AssetCardProps {
  label: string;
  src: string | null;
  icon: ReactNode;
  onExpand: (src: string) => void;
}

export function AssetCard({ label, src, icon, onExpand }: AssetCardProps) {
  return (
    <div 
      className="group relative bg-slate-900 border border-slate-800 rounded-[2rem] p-6 shadow-xl hover:shadow-2xl transition-all cursor-zoom-in h-[320px] flex flex-col" 
      onClick={() => src && onExpand(src)}
    >
       <div className="flex-1 rounded-2xl overflow-hidden bg-slate-950 mb-6 border border-slate-800 relative">
          {src ? (
            <img src={src} alt={label} className="w-full h-full object-cover grayscale-[0.3] group-hover:grayscale-0 transition-all group-hover:scale-105" />
          ) : (
            <div className="w-full h-full flex items-center justify-center text-slate-800">
               {icon}
            </div>
          )}
          <div className="absolute inset-0 bg-gradient-to-t from-slate-950/80 to-transparent opacity-0 group-hover:opacity-100 transition-opacity" />
       </div>
       <div className="flex justify-between items-center px-2">
         <p className="text-[10px] font-black text-slate-300 uppercase tracking-widest flex items-center gap-2">
           {icon} {label}
         </p>
         <Eye className="w-4 h-4 text-slate-600 group-hover:text-blue-500 transition-colors" />
       </div>
    </div>
  );
}

import { SearchCode } from 'lucide-react';
import Dropzone from '@/components/Dropzone';

interface DocumentNodeProps {
  idFile: File | null;
  setIdFile: (file: File | null) => void;
}

export function DocumentNode({ idFile, setIdFile }: DocumentNodeProps) {
  return (
    <div className="space-y-4">
      <div className="flex justify-between items-center px-1">
        <p className="text-[10px] font-black uppercase tracking-[0.2em] text-slate-500">Node 01: Document</p>
        <span className="text-[9px] font-bold text-blue-400 border border-blue-800/50 bg-blue-900/20 px-2 py-0.5 rounded">Required</span>
      </div>
      <Dropzone 
        label="ID Card (Front)" 
        onFileSelect={setIdFile}
        accept=".jpg,.jpeg,.png,.pdf"
        icon={<SearchCode className="w-8 h-8 text-slate-300" />}
        className="h-[300px] rounded-[2rem]"
      />
    </div>
  );
}

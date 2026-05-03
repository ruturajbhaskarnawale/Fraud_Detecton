import { useState } from 'react';
import { motion } from 'framer-motion';
import { Camera, Fingerprint, UploadCloud } from 'lucide-react';
import Dropzone from '@/components/Dropzone';
import WebcamCapture from '@/components/WebcamCapture';

interface BiometricNodeProps {
  selfieFile: File | null;
  setSelfieFile: (file: File | null) => void;
}

export function BiometricNode({ selfieFile, setSelfieFile }: BiometricNodeProps) {
  const [isCameraOpen, setIsCameraOpen] = useState(false);

  return (
    <div className="space-y-4">
      <div className="flex justify-between items-center px-1">
        <p className="text-[10px] font-black uppercase tracking-[0.2em] text-slate-500">Node 02: Biometric</p>
        <span className="text-[9px] font-bold text-emerald-400 border border-emerald-800/50 bg-emerald-900/20 px-2 py-0.5 rounded">Required</span>
      </div>
      
      {isCameraOpen ? (
        <motion.div 
          initial={{ opacity: 0, scale: 0.95 }}
          animate={{ opacity: 1, scale: 1 }}
          className="h-[300px]"
        >
          <WebcamCapture 
            onCapture={(file) => {
              setSelfieFile(file);
              setIsCameraOpen(false);
            }}
            onCancel={() => setIsCameraOpen(false)}
          />
        </motion.div>
      ) : selfieFile ? (
        <Dropzone 
          label="Live Selfie" 
          onFileSelect={setSelfieFile}
          accept=".jpg,.jpeg,.png"
          icon={<Fingerprint className="w-8 h-8 text-slate-300" />}
          className="h-[300px] rounded-[2rem]"
        />
      ) : (
        <div className="grid grid-cols-2 gap-4 h-[300px]">
          <button 
            onClick={() => setIsCameraOpen(true)}
            className="flex flex-col items-center justify-center gap-4 bg-slate-900/50 hover:bg-blue-900/20 border-2 border-dashed border-slate-800 hover:border-blue-500 rounded-[2rem] transition-all group"
          >
            <div className="w-14 h-14 rounded-2xl bg-blue-500/20 text-blue-400 flex items-center justify-center group-hover:scale-110 transition-transform">
              <Camera className="w-7 h-7" />
            </div>
            <div className="text-center">
              <p className="font-bold text-slate-200">Open Camera</p>
              <p className="text-xs text-slate-500 font-medium mt-1">Take live selfie</p>
            </div>
          </button>
          
          <div className="relative h-full">
            <Dropzone 
              label="Upload File" 
              onFileSelect={setSelfieFile}
              accept=".jpg,.jpeg,.png"
              icon={<UploadCloud className="w-7 h-7 text-slate-400" />}
              className="h-full rounded-[2rem] border-slate-800"
            />
          </div>
        </div>
      )}
    </div>
  );
}

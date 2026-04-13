"use client";
import { useCallback, useState } from 'react';
import { Upload, FileText, X, CheckCircle2 } from 'lucide-react';
import { cn } from '@/lib/utils';
import { motion, AnimatePresence } from 'framer-motion';

interface DropzoneProps {
  label: string;
  onFileSelect: (file: File | null) => void;
  accept?: string;
  icon?: React.ReactNode;
}

export default function Dropzone({ label, onFileSelect, accept = "image/*", icon }: DropzoneProps) {
  const [file, setFile] = useState<File | null>(null);
  const [isDragOver, setIsDragOver] = useState(false);

  const handleFile = (f: File) => {
    setFile(f);
    onFileSelect(f);
  };

  const removeFile = (e: React.MouseEvent) => {
    e.stopPropagation();
    setFile(null);
    onFileSelect(null);
  };

  return (
    <div 
      className={cn(
        "relative group cursor-pointer transition-all duration-300",
        "border-2 border-dashed rounded-2xl p-6 h-48 flex flex-col items-center justify-center text-center",
        isDragOver ? "border-blue-500 bg-blue-50/50" : "border-slate-200 bg-slate-50/30 hover:bg-slate-50",
        file ? "border-blue-500 bg-blue-50/30" : ""
      )}
      onDragOver={(e) => { e.preventDefault(); setIsDragOver(true); }}
      onDragLeave={() => setIsDragOver(false)}
      onDrop={(e) => {
        e.preventDefault();
        setIsDragOver(false);
        const droppedFile = e.dataTransfer.files[0];
        if (droppedFile) handleFile(droppedFile);
      }}
      onClick={() => document.getElementById(`input-${label}`)?.click()}
    >
      <input 
        type="file" 
        id={`input-${label}`}
        hidden 
        accept={accept}
        onChange={(e) => {
          const selectedFile = e.target.files?.[0];
          if (selectedFile) handleFile(selectedFile);
        }}
      />

      <AnimatePresence mode="wait">
        {!file ? (
          <motion.div 
            key="empty"
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -10 }}
            className="flex flex-col items-center"
          >
            <div className="w-12 h-12 rounded-full bg-blue-100 flex items-center justify-center mb-3 text-blue-600 group-hover:scale-110 transition-transform">
              {icon || <Upload className="w-6 h-6" />}
            </div>
            <p className="text-sm font-semibold text-slate-700">{label}</p>
            <p className="text-xs text-slate-500 mt-1">Drag and drop or click to upload</p>
          </motion.div>
        ) : (
          <motion.div 
            key="selected"
            initial={{ opacity: 0, scale: 0.9 }}
            animate={{ opacity: 1, scale: 1 }}
            className="flex flex-col items-center"
          >
            <div className="w-12 h-12 rounded-full bg-success/10 flex items-center justify-center mb-3 text-green-600">
              <CheckCircle2 className="w-6 h-6" />
            </div>
            <p className="text-sm font-semibold text-slate-700 truncate max-w-[200px]">{file.name}</p>
            <button 
              onClick={removeFile}
              className="mt-3 p-1 rounded-full hover:bg-slate-200 text-slate-400 hover:text-red-500 transition-colors"
            >
              <X className="w-4 h-4" />
            </button>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}

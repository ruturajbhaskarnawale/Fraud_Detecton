"use client";
import React, { useState } from 'react';
import { motion } from 'framer-motion';
import { UploadCloud, ShieldCheck, X } from 'lucide-react';
import { cn } from '@/lib/utils';

interface DropzoneProps {
  onFileSelect: (file: File | null) => void;
  label: string;
  icon?: React.ReactNode;
  className?: string;
}

export default function Dropzone({ onFileSelect, label, icon, className }: DropzoneProps) {
  const [dragActive, setDragActive] = useState(false);
  const [fileName, setFileName] = useState<string | null>(null);

  const handleDrag = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === "dragenter" || e.type === "dragover") {
      setDragActive(true);
    } else if (e.type === "dragleave") {
      setDragActive(false);
    }
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);
    
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      const file = e.dataTransfer.files[0];
      setFileName(file.name);
      onFileSelect(file);
    }
  };

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      const file = e.target.files[0];
      setFileName(file.name);
      onFileSelect(file);
    }
  };

  const clearFile = (e: React.MouseEvent) => {
    e.stopPropagation();
    setFileName(null);
    onFileSelect(null);
  };

  return (
    <div 
      onDragEnter={handleDrag}
      onDragLeave={handleDrag}
      onDragOver={handleDrag}
      onDrop={handleDrop}
      className={cn(
        "relative flex flex-col items-center justify-center p-8 border-2 border-dashed rounded-2xl transition-all duration-300 bg-slate-50 min-h-[220px] cursor-pointer group",
        dragActive ? "border-blue-500 bg-blue-50/50" : "border-slate-200 hover:border-slate-300 hover:bg-slate-100/50",
        fileName ? "border-emerald-500 bg-emerald-50/30" : "",
        className
      )}
    >
      <input 
        type="file" 
        className="absolute inset-0 w-full h-full opacity-0 cursor-pointer z-10" 
        onChange={handleFileChange}
        accept="image/*"
      />

      {fileName ? (
        <motion.div 
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          className="text-center space-y-4 relative z-20"
        >
          <div className="w-12 h-12 bg-emerald-100 rounded-xl flex items-center justify-center mx-auto">
            <ShieldCheck className="w-6 h-6 text-emerald-600" />
          </div>
          <div className="space-y-1">
            <p className="font-bold text-slate-800 text-sm truncate max-w-[200px]">{fileName}</p>
            <p className="text-[10px] font-bold uppercase tracking-widest text-emerald-600">File Selected</p>
          </div>
          <button 
            onClick={clearFile}
            className="px-4 py-2 bg-slate-900 text-white rounded-lg text-[10px] font-bold uppercase tracking-widest hover:bg-rose-600 transition-colors shadow-sm"
          >
            Change File
          </button>
        </motion.div>
      ) : (
        <div className="text-center space-y-4 relative z-20">
          <div className={cn(
            "w-12 h-12 rounded-xl flex items-center justify-center mx-auto transition-colors",
            dragActive ? "bg-blue-500 text-white" : "bg-white text-slate-700 border border-slate-100 group-hover:text-blue-500 shadow-sm"
          )}>
            {icon || <UploadCloud className="w-6 h-6" />}
          </div>
          <div className="space-y-1">
            <p className="text-base font-bold text-slate-900">{label}</p>
            <p className="text-xs font-medium text-slate-700">
              Drag and drop or <span className="text-blue-600 font-bold">browse</span>
            </p>
          </div>
        </div>
      )}
    </div>
  );
}

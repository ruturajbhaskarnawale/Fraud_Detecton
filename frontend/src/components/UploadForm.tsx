'use client';

import React, { useState } from 'react';
import { Upload, FileText, Camera, ShieldCheck, ArrowRight } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';

interface UploadFormProps {
  onVerify: (document: File, selfie: File) => void;
  isLoading: boolean;
}

export const UploadForm: React.FC<UploadFormProps> = ({ onVerify, isLoading }) => {
  const [document, setDocument] = useState<File | null>(null);
  const [selfie, setSelfie] = useState<File | null>(null);

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>, type: 'doc' | 'selfie') => {
    if (e.target.files && e.target.files[0]) {
      if (type === 'doc') setDocument(e.target.files[0]);
      else setSelfie(e.target.files[0]);
    }
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (document && selfie) {
      onVerify(document, selfie);
    }
  };

  return (
    <motion.div 
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className="max-w-4xl mx-auto p-8"
    >
      <div className="text-center mb-12">
        <h1 className="text-4xl font-bold text-slate-900 mb-4 tracking-tight">Identity Verification</h1>
        <p className="text-slate-500 text-lg">Securely verify your identity using Veridex AI multi-modal engine.</p>
      </div>

      <form onSubmit={handleSubmit} className="grid grid-cols-1 md:grid-cols-2 gap-8">
        {/* ID Document Upload */}
        <div className="relative group">
          <label className="block text-sm font-semibold text-slate-700 mb-3 ml-1">ID Document (Front)</label>
          <div className={`
            border-2 border-dashed rounded-2xl p-8 transition-all duration-300 flex flex-col items-center justify-center min-h-[300px]
            ${document ? 'border-emerald-500 bg-emerald-50/50' : 'border-slate-200 hover:border-blue-400 bg-white hover:bg-blue-50/20'}
          `}>
            <input 
              type="file" 
              className="absolute inset-0 w-full h-full opacity-0 cursor-pointer" 
              onChange={(e) => handleFileChange(e, 'doc')}
              accept="image/*,application/pdf"
            />
            {document ? (
              <div className="text-center">
                <FileText className="w-16 h-16 text-emerald-500 mx-auto mb-4" />
                <p className="text-emerald-700 font-medium truncate max-w-[200px]">{document.name}</p>
              </div>
            ) : (
              <div className="text-center">
                <div className="w-16 h-16 bg-slate-100 rounded-full flex items-center justify-center mx-auto mb-4">
                  <Upload className="w-8 h-8 text-slate-400" />
                </div>
                <p className="text-slate-600 font-medium">Drop ID here or click</p>
                <p className="text-slate-400 text-sm mt-1">Supports PNG, JPG, PDF</p>
              </div>
            )}
          </div>
        </div>

        {/* Selfie Upload */}
        <div className="relative group">
          <label className="block text-sm font-semibold text-slate-700 mb-3 ml-1">Live Selfie</label>
          <div className={`
            border-2 border-dashed rounded-2xl p-8 transition-all duration-300 flex flex-col items-center justify-center min-h-[300px]
            ${selfie ? 'border-emerald-500 bg-emerald-50/50' : 'border-slate-200 hover:border-blue-400 bg-white hover:bg-blue-50/20'}
          `}>
            <input 
              type="file" 
              className="absolute inset-0 w-full h-full opacity-0 cursor-pointer" 
              onChange={(e) => handleFileChange(e, 'selfie')}
              accept="image/*"
            />
            {selfie ? (
              <div className="text-center">
                <Camera className="w-16 h-16 text-emerald-500 mx-auto mb-4" />
                <p className="text-emerald-700 font-medium truncate max-w-[200px]">{selfie.name}</p>
              </div>
            ) : (
              <div className="text-center">
                <div className="w-16 h-16 bg-slate-100 rounded-full flex items-center justify-center mx-auto mb-4">
                  <Camera className="w-8 h-8 text-slate-400" />
                </div>
                <p className="text-slate-600 font-medium">Capture or drop selfie</p>
                <p className="text-slate-400 text-sm mt-1">High-res portrait preferred</p>
              </div>
            )}
          </div>
        </div>

        <div className="md:col-span-2 flex justify-center mt-8">
          <button
            type="submit"
            disabled={!document || !selfie || isLoading}
            className={`
              flex items-center gap-3 px-10 py-4 rounded-full font-bold text-lg shadow-xl transition-all duration-300
              ${document && selfie && !isLoading 
                ? 'bg-blue-600 hover:bg-blue-700 text-white transform hover:-translate-y-1' 
                : 'bg-slate-200 text-slate-400 cursor-not-allowed'}
            `}
          >
            {isLoading ? (
              <div className="animate-spin rounded-full h-6 w-6 border-b-2 border-white"></div>
            ) : (
              <>
                <ShieldCheck className="w-6 h-6" />
                Run Verification
                <ArrowRight className="w-5 h-5" />
              </>
            )}
          </button>
        </div>
      </form>
    </motion.div>
  );
};

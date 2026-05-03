"use client";
import React, { useState, useRef, useCallback } from 'react';
import { Camera, X, RefreshCw, Check, AlertCircle } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';

interface WebcamCaptureProps {
  onCapture: (file: File) => void;
  onCancel: () => void;
}

export default function WebcamCapture({ onCapture, onCancel }: WebcamCaptureProps) {
  const videoRef = useRef<HTMLVideoElement>(null);
  const streamRef = useRef<MediaStream | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [capturedImage, setCapturedImage] = useState<string | null>(null);
  const [file, setFile] = useState<File | null>(null);
  const [isInitializing, setIsInitializing] = useState(false);

  const startCamera = async () => {
    setIsInitializing(true);
    setError(null);
    try {
      const mediaStream = await navigator.mediaDevices.getUserMedia({
        video: { facingMode: 'user', width: { ideal: 1280 }, height: { ideal: 720 } },
        audio: false,
      });
      streamRef.current = mediaStream;
      if (videoRef.current) {
        videoRef.current.srcObject = mediaStream;
      }
    } catch (err: any) {
      console.error('Error accessing camera:', err);
      setError('Camera access denied or unavailable. Please check permissions.');
    } finally {
      setIsInitializing(false);
    }
  };

  const stopCamera = useCallback(() => {
    if (streamRef.current) {
      streamRef.current.getTracks().forEach((track) => track.stop());
      streamRef.current = null;
    }
  }, []);

  const capture = () => {
    if (videoRef.current) {
      const canvas = document.createElement('canvas');
      canvas.width = videoRef.current.videoWidth;
      canvas.height = videoRef.current.videoHeight;
      const ctx = canvas.getContext('2d');
      if (ctx) {
        // Draw the video frame to the canvas
        ctx.drawImage(videoRef.current, 0, 0, canvas.width, canvas.height);
        
        // Convert to data URL to show the preview
        const dataUrl = canvas.toDataURL('image/jpeg', 0.9);
        setCapturedImage(dataUrl);

        // Convert to Blob and then File
        canvas.toBlob((blob) => {
          if (blob) {
            const newFile = new File([blob], `selfie_${Date.now()}.jpg`, { type: 'image/jpeg' });
            setFile(newFile);
            stopCamera();
          }
        }, 'image/jpeg', 0.9);
      }
    }
  };

  const retake = () => {
    setCapturedImage(null);
    setFile(null);
    startCamera();
  };

  const confirmCapture = () => {
    if (file) {
      onCapture(file);
    }
  };

  // Start camera when component mounts if not already captured
  React.useEffect(() => {
    if (!capturedImage && !error) {
      startCamera();
    }
    return () => stopCamera();
  }, [stopCamera, capturedImage, error]);

  return (
    <div className="relative w-full h-[300px] bg-slate-900 rounded-2xl overflow-hidden border border-slate-700/50 flex flex-col shadow-inner group">
      <AnimatePresence mode="wait">
        {error ? (
          <motion.div 
            key="error"
            initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }}
            className="absolute inset-0 flex flex-col items-center justify-center p-6 text-center z-10 bg-slate-900/90 backdrop-blur-sm"
          >
            <AlertCircle className="w-10 h-10 text-rose-500 mb-3" />
            <p className="text-sm font-medium text-slate-300">{error}</p>
            <button onClick={onCancel} className="mt-4 px-4 py-2 bg-slate-800 text-white rounded-lg text-xs font-bold uppercase hover:bg-slate-700 transition-colors">
              Go Back
            </button>
          </motion.div>
        ) : capturedImage ? (
          <motion.div 
            key="preview"
            initial={{ opacity: 0, scale: 0.95 }} animate={{ opacity: 1, scale: 1 }} exit={{ opacity: 0 }}
            className="absolute inset-0 z-10"
          >
            <img src={capturedImage} alt="Captured selfie" className="w-full h-full object-cover" />
            <div className="absolute inset-0 bg-gradient-to-t from-slate-900/90 via-transparent to-transparent flex items-end justify-center pb-6 gap-4">
              <button onClick={retake} className="flex items-center gap-2 px-4 py-2.5 bg-slate-800/80 hover:bg-slate-700 backdrop-blur-md text-white rounded-xl text-xs font-bold uppercase transition-all shadow-lg border border-slate-600/50">
                <RefreshCw className="w-4 h-4" /> Retake
              </button>
              <button onClick={confirmCapture} className="flex items-center gap-2 px-6 py-2.5 bg-emerald-600 hover:bg-emerald-500 text-white rounded-xl text-xs font-bold uppercase transition-all shadow-lg shadow-emerald-900/50 border border-emerald-500/50">
                <Check className="w-4 h-4" /> Use Photo
              </button>
            </div>
          </motion.div>
        ) : (
          <motion.div 
            key="camera"
            initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }}
            className="absolute inset-0 z-0 bg-black"
          >
            {/* The Video Feed */}
            <video
              ref={videoRef}
              autoPlay
              playsInline
              muted
              className="w-full h-full object-cover transform -scale-x-100" // Mirror effect
            />
            
            {/* Overlay UI */}
            <div className="absolute inset-0 pointer-events-none border-[6px] border-slate-900/20 rounded-2xl" />
            <div className="absolute inset-0 flex items-center justify-center pointer-events-none">
              {/* Face Guide Box */}
              <div className="w-48 h-64 border-2 border-dashed border-white/40 rounded-[3rem] shadow-[0_0_0_9999px_rgba(0,0,0,0.5)] transition-all" />
            </div>

            {/* Controls */}
            <div className="absolute bottom-0 inset-x-0 p-4 bg-gradient-to-t from-black/80 to-transparent flex items-center justify-between">
              <button onClick={onCancel} className="p-2.5 bg-slate-800/80 hover:bg-slate-700 backdrop-blur-md text-slate-300 rounded-full transition-colors">
                <X className="w-5 h-5" />
              </button>
              
              <button 
                onClick={capture} 
                disabled={isInitializing}
                className="w-14 h-14 bg-white/20 hover:bg-white/30 backdrop-blur-md border-4 border-white rounded-full flex items-center justify-center transition-all group active:scale-95 disabled:opacity-50"
              >
                <div className="w-10 h-10 bg-white rounded-full scale-0 group-hover:scale-100 transition-transform origin-center" />
              </button>

              <div className="w-10" /> {/* Spacer to balance flex-between */}
            </div>

            {isInitializing && (
              <div className="absolute inset-0 flex items-center justify-center bg-slate-900/80 backdrop-blur-sm z-20">
                <div className="w-8 h-8 border-4 border-blue-500 border-t-transparent rounded-full animate-spin" />
              </div>
            )}
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}

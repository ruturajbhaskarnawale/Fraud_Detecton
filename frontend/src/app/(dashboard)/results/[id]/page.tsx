"use client";
import { useEffect, useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { 
  ShieldCheck, 
  User, 
  Calendar, 
  Fingerprint, 
  AlertCircle, 
  Clock,
  ArrowLeft,
  Share2,
  Download,
  Activity,
  FileText,
  Eye,
  X,
  SearchCode
} from 'lucide-react';
import { useParams, useRouter } from 'next/navigation';
import Link from 'next/link';
import { verificationService } from '@/services/api';
import { cn } from '@/lib/utils';

export default function ResultsPage() {
  const { id } = useParams();
  const router = useRouter();
  const [data, setData] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [selectedAsset, setSelectedAsset] = useState<string | null>(null);

  const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

  useEffect(() => {
    const fetchResult = async () => {
      try {
        const record = await verificationService.getRecord(id as string);
        setData(record);
      } catch (err: any) {
        console.error("Failed to fetch result:", err);
        setError("Unable to find the requested verification record.");
      } finally {
        setLoading(false);
      }
    };
    if (id) fetchResult();
  }, [id]);

  const handleShare = async () => {
    const url = window.location.href;
    if (navigator.share) {
      try {
        await navigator.share({
          title: 'Veridex Forensic Report',
          text: `KYC Verification for ${data?.name || 'Identity'}`,
          url: url
        });
      } catch (err) {
        console.log("Share cancelled");
      }
    } else {
      navigator.clipboard.writeText(url);
      alert("Link copied to clipboard!");
    }
  };

  const handleExportPDF = () => {
    window.print();
  };

  if (loading) return (
    <div className="flex flex-col items-center justify-center min-h-screen space-y-4 bg-slate-50">
      <div className="w-12 h-12 border-4 border-blue-100 border-t-blue-600 rounded-full animate-spin" />
      <p className="text-sm font-bold text-slate-500 uppercase tracking-widest">Loading Report...</p>
    </div>
  );

  if (error) return (
    <div className="max-w-xl mx-auto py-20 px-6 text-center space-y-6">
      <div className="w-16 h-16 bg-rose-50 text-rose-500 rounded-2xl flex items-center justify-center mx-auto shadow-sm">
        <AlertCircle className="w-8 h-8" />
      </div>
      <div className="space-y-2">
         <h1 className="text-2xl font-bold text-slate-900">Report Error</h1>
         <p className="text-slate-600 font-medium">{error}</p>
      </div>
      <Link href="/history" className="inline-flex items-center gap-2 px-6 py-3 bg-slate-100 text-slate-700 rounded-xl font-bold text-sm tracking-tight hover:bg-slate-200 transition-all">
         <ArrowLeft className="w-4 h-4" />
         Back to History
      </Link>
    </div>
  );

  const { decision, risk_score, reasons, fraud_status, face_match_distance, image_paths } = data;
  const isOk = decision === 'VALID';
  const isSuspicious = decision === 'SUSPICIOUS';

  return (
    <div className="space-y-8 max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 print:p-0 print:max-w-none">
      {/* Header Bar */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-6 border-b border-slate-200 pb-8 print:border-none">
        <div className="flex items-center gap-4">
           <button onClick={() => router.back()} className="p-2 hover:bg-slate-100 rounded-lg transition-colors text-slate-400 print:hidden">
              <ArrowLeft className="w-6 h-6" />
           </button>
           <div>
              <p className="text-[10px] font-bold text-blue-600 uppercase tracking-widest bg-blue-50 px-2 py-0.5 rounded-md inline-block mb-1">Audit Record</p>
              <h1 className="text-2xl font-bold text-slate-900 flex items-center gap-3">
                 Verification Result
                 <span className="text-xs font-mono font-medium text-slate-400">#{id?.toString().slice(0, 8)}</span>
              </h1>
           </div>
        </div>
        <div className="flex items-center gap-3 print:hidden">
           <button 
             onClick={handleShare}
             className="px-4 py-2 border border-slate-200 rounded-lg text-sm font-semibold text-slate-600 hover:bg-slate-50 transition-colors flex items-center gap-2"
           >
             <Share2 className="w-4 h-4" /> Share
           </button>
           <button 
             onClick={handleExportPDF}
             className="px-4 py-2 bg-slate-900 text-white rounded-lg text-sm font-semibold hover:bg-slate-800 transition-colors flex items-center gap-2 shadow-sm"
           >
             <Download className="w-4 h-4" /> Export PDF
           </button>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-12 gap-8">
         {/* Main Summary Section */}
         <div className="lg:col-span-4 space-y-6">
            <div className={cn(
              "p-8 rounded-2xl border flex flex-col items-center text-center space-y-6",
              isOk ? "bg-emerald-50 border-emerald-100 text-emerald-900 shadow-sm" : 
              isSuspicious ? "bg-amber-50 border-amber-100 text-amber-900 shadow-sm" : 
              "bg-rose-50 border-rose-100 text-rose-900 shadow-sm"
            )}>
               <div className="w-16 h-16 rounded-xl bg-white flex items-center justify-center shadow-lg">
                  {isOk ? <ShieldCheck className="w-10 h-10 text-emerald-500" /> : <AlertCircle className="w-10 h-10 text-rose-500" />}
               </div>
               <div>
                  <p className="text-xs font-bold uppercase tracking-widest opacity-60 mb-1">Final Verdict</p>
                  <h2 className="text-4xl font-black tracking-tight">{decision}</h2>
               </div>
               <div className="w-full h-2 bg-black/5 rounded-full overflow-hidden">
                  <div className={cn("h-full", isOk ? "bg-emerald-500" : "bg-rose-500")} style={{ width: `${100 - risk_score}%` }} />
               </div>
               <p className="text-xs font-bold uppercase opacity-60 tracking-widest">Trust Level: {(100 - risk_score).toFixed(1)}%</p>
            </div>

            <div className="bg-white border border-slate-200 rounded-2xl p-6 shadow-sm space-y-6">
               <h3 className="font-bold text-slate-900 text-sm uppercase tracking-widest flex items-center gap-2">
                 <Activity className="w-4 h-4 text-blue-600" /> Security Signals
               </h3>
               <div className="space-y-4">
                  {reasons.map((reason: string, i: number) => (
                    <div key={i} className="flex gap-3 items-start p-3 bg-slate-50 rounded-lg">
                       <div className={cn("mt-1.5 w-1.5 h-1.5 rounded-full flex-shrink-0", isOk ? "bg-emerald-500" : "bg-amber-500")} />
                       <p className="text-xs font-semibold text-slate-700 leading-snug">{reason}</p>
                    </div>
                  ))}
               </div>
            </div>
         </div>

         {/* Detailed Data Section */}
         <div className="lg:col-span-8 space-y-8">
            <div className="bg-white border border-slate-200 rounded-2xl shadow-sm overflow-hidden">
               <div className="px-6 py-4 bg-slate-50 border-b border-slate-200 flex justify-between items-center">
                  <h3 className="font-bold text-slate-900 text-sm uppercase tracking-widest">Document Insight</h3>
                  <p className="text-[10px] font-bold text-slate-400 uppercase tracking-widest">{new Date(data.timestamp).toLocaleString()}</p>
               </div>
               <div className="p-8 grid grid-cols-1 md:grid-cols-2 gap-8">
                  <DataRow icon={User} label="Legal Full Name" value={data.name} />
                  <DataRow icon={Fingerprint} label="Identity Number" value={data.id_number} />
                  <DataRow icon={Calendar} label="Date of Birth" value={data.dob} />
                  <DataRow icon={FileText} label="Tracking Reference" value={data.tracking_id} className="font-mono text-[10px]" />
               </div>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-6 print:break-inside-avoid">
               <AssetDisplay 
                 label="Identity Asset" 
                 src={image_paths?.id_card ? `${API_URL}${image_paths.id_card}` : null} 
                 onExpand={(src) => setSelectedAsset(src)}
               />
               <AssetDisplay 
                 label="Biometric Asset" 
                 src={image_paths?.selfie ? `${API_URL}${image_paths.selfie}` : null} 
                 onExpand={(src) => setSelectedAsset(src)}
               />
            </div>

            <div className="bg-white border border-slate-200 rounded-2xl p-8 shadow-sm print:break-inside-avoid">
               <h3 className="font-bold text-slate-900 text-sm uppercase tracking-widest mb-8">Forensic Pipeline Status</h3>
               <div className="space-y-6">
                  <PipelineStatus label="Neural Extraction" progress={98.8} />
                  <PipelineStatus label="Signal Match" progress={100 - risk_score} />
                  <PipelineStatus label="Biometric Scaling" progress={face_match_distance < 0.6 ? 100 : 40} />
               </div>
            </div>
         </div>
      </div>

      {/* Lightbox Modal */}
      <AnimatePresence>
        {selectedAsset && (
          <motion.div 
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            onClick={() => setSelectedAsset(null)}
            className="fixed inset-0 z-50 bg-black/90 flex items-center justify-center p-8 backdrop-blur-sm cursor-zoom-out print:hidden"
          >
            <button className="absolute top-8 right-8 text-white p-2 hover:bg-white/10 rounded-full">
              <X className="w-8 h-8" />
            </button>
            <motion.img 
              initial={{ scale: 0.9, opacity: 0 }}
              animate={{ scale: 1, opacity: 1 }}
              src={selectedAsset} 
              alt="Forensic Asset" 
              className="max-w-full max-h-full rounded-lg shadow-2xl"
              onClick={(e) => e.stopPropagation()}
            />
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}

function DataRow({ icon: Icon, label, value, className }: any) {
  return (
    <div className="space-y-1">
       <div className="flex items-center gap-2 text-[10px] font-bold text-slate-400 uppercase tracking-widest">
          <Icon className="w-3.5 h-3.5" />
          {label}
       </div>
       <p className={cn("text-base font-bold text-slate-800", className)}>{value || 'Not Captured'}</p>
    </div>
  );
}

function AssetDisplay({ label, src, onExpand }: { label: string; src: string | null; onExpand: (src: string) => void }) {
  return (
    <div className="bg-slate-50 border border-slate-200 rounded-2xl p-6 flex flex-col items-center justify-center gap-4 group transition-all hover:bg-white hover:border-slate-300 shadow-sm hover:shadow-md h-[240px]">
       {src ? (
         <div className="relative w-full h-full rounded-xl overflow-hidden cursor-zoom-in" onClick={() => onExpand(src)}>
           <img src={src} alt={label} className="w-full h-full object-cover transition-transform group-hover:scale-105" />
           <div className="absolute inset-0 bg-black/20 opacity-0 group-hover:opacity-100 transition-opacity flex items-center justify-center">
             <Eye className="w-6 h-6 text-white" />
           </div>
         </div>
       ) : (
         <div className="w-12 h-12 bg-white rounded-xl flex items-center justify-center text-slate-300 shadow-sm border border-slate-100">
            <Eye className="w-6 h-6" />
         </div>
       )}
       <p className="text-[10px] font-bold text-slate-400 uppercase tracking-widest">{label}</p>
       {src ? (
         <p className="text-[9px] font-bold text-slate-500 uppercase tracking-widest opacity-0 group-hover:opacity-100 transition-opacity">Click to Expand</p>
       ) : (
         <span className="px-3 py-1 bg-slate-100 text-[9px] font-bold text-slate-500 rounded-md uppercase tracking-widest">Not Uploaded</span>
       )}
    </div>
  );
}

function PipelineStatus({ label, progress }: any) {
  return (
    <div className="space-y-2">
       <div className="flex justify-between items-center text-[10px] font-bold uppercase tracking-widest text-slate-600">
          <span>{label}</span>
          <span className="text-blue-600 italic">{progress.toFixed(1)}%</span>
       </div>
       <div className="w-full h-1.5 bg-slate-100 rounded-full overflow-hidden">
          <div className="h-full bg-blue-600 transition-all duration-1000" style={{ width: `${progress}%` }} />
       </div>
    </div>
  );
}

"use client";
import { motion } from 'framer-motion';
import { AlertCircle, CheckCircle, XCircle, Info, Calendar, User, FileDigit, Fingerprint } from 'lucide-react';
import { cn } from '@/lib/utils';

interface ResultCardProps {
  data: any;
}

export default function ResultCard({ data }: ResultCardProps) {
  const { decision, risk_score, reasons } = data.final_decision;
  const { extracted_fields, type } = data.id_validation;
  
  const isRejected = decision === 'REJECTED';
  const isSuspicious = decision === 'SUSPICIOUS';
  const isValid = decision === 'VALID';

  const statusConfig = {
    REJECTED: { icon: XCircle, color: 'text-red-600', bg: 'bg-red-50', border: 'border-red-200' },
    SUSPICIOUS: { icon: AlertCircle, color: 'text-amber-600', bg: 'bg-amber-50', border: 'border-amber-200' },
    VALID: { icon: CheckCircle, color: 'text-green-600', bg: 'bg-green-50', border: 'border-green-200' },
  }[decision as keyof typeof statusConfig] || { icon: Info, color: 'text-blue-600', bg: 'bg-blue-50', border: 'border-blue-200' };

  return (
    <motion.div 
      initial={{ opacity: 0, scale: 0.95 }}
      animate={{ opacity: 1, scale: 1 }}
      className="space-y-6"
    >
      {/* Hero Status */}
      <div className={cn("p-6 rounded-3xl border-2 shadow-sm flex flex-col items-center text-center", statusConfig.bg, statusConfig.border)}>
        <statusConfig.icon className={cn("w-16 h-16 mb-4", statusConfig.color)} />
        <h2 className={cn("text-3xl font-extrabold", statusConfig.color)}>{decision}</h2>
        <p className="text-slate-600 mt-2 font-medium">Risk Score: <span className="text-slate-900">{risk_score}/100</span></p>
      </div>

      {/* Extracted Data */}
      <div className="bg-white rounded-3xl border border-slate-200 overflow-hidden">
        <div className="bg-slate-50 px-6 py-4 border-b border-slate-200">
          <h3 className="font-bold text-slate-800 flex items-center gap-2">
            <FileDigit className="w-5 h-5 text-blue-600" />
            Extracted Information
          </h3>
        </div>
        <div className="p-6 grid grid-cols-1 md:grid-cols-2 gap-6">
          <DataField icon={User} label="Name" value={extracted_fields?.name} />
          <DataField icon={Fingerprint} label="ID Number" value={extracted_fields?.id_number} />
          <DataField icon={Calendar} label="Date of Birth" value={extracted_fields?.dob} />
          <DataField icon={Info} label="Document Type" value={type} />
        </div>
      </div>

      {/* Analysis Details */}
      {reasons && reasons.length > 0 && (
        <div className="bg-white rounded-3xl border border-slate-200 overflow-hidden">
          <div className="bg-slate-50 px-6 py-4 border-b border-slate-200">
            <h3 className="font-bold text-slate-800">Security Audit Logs</h3>
          </div>
          <div className="p-6 space-y-3">
            {reasons.map((reason: string, i: number) => (
              <div key={i} className="flex items-start gap-3 p-3 rounded-xl bg-slate-50 text-sm text-slate-600 border border-slate-100">
                <AlertCircle className="w-4 h-4 text-amber-500 mt-0.5 shrink-0" />
                <span>{reason}</span>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Fraud Detailed Metrics */}
      <div className="grid grid-cols-2 gap-4">
        <MetricCard label="ELA Score" value={data.fraud_validation.tampering_results[0].tamper_score.toFixed(2)} unit="pts" />
        <MetricCard label="Face Match" value={(data.face_validation.similarity * 100).toFixed(1)} unit="%" />
      </div>
    </motion.div>
  );
}

function DataField({ icon: Icon, label, value }: { icon: any, label: string, value: string }) {
  return (
    <div className="space-y-1">
      <div className="flex items-center gap-1.5 text-xs font-bold text-slate-400 uppercase tracking-wider">
        <Icon className="w-3.5 h-3.5" />
        {label}
      </div>
      <p className="font-semibold text-slate-900">{value || 'N/A'}</p>
    </div>
  );
}

function MetricCard({ label, value, unit }: { label: string, value: string, unit: string }) {
  return (
    <div className="bg-slate-50 p-4 rounded-2xl border border-slate-100 text-center">
      <p className="text-[10px] uppercase font-black text-slate-400 tracking-widest mb-1">{label}</p>
      <div className="text-xl font-bold text-slate-900">
        {value}<span className="text-xs text-slate-400 ml-0.5">{unit}</span>
      </div>
    </div>
  );
}

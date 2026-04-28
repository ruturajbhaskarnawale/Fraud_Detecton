'use client';

import React from 'react';
import { motion } from 'framer-motion';
import { 
  ShieldCheck, ShieldAlert, ShieldQuestion, 
  User, FileText, Fingerprint, Activity,
  Info, AlertTriangle
} from 'lucide-react';
import { 
  BarChart, Bar, XAxis, YAxis, CartesianGrid, 
  Tooltip, ResponsiveContainer, Cell,
  PieChart, Pie
} from 'recharts';
import { VerifyResponse } from '../lib/api';

interface ResultDashboardProps {
  data: VerifyResponse;
  onReset: () => void;
}

export const ResultDashboard: React.FC<ResultDashboardProps> = ({ data, onReset }) => {
  const { decision, confidence_score, module_breakdown } = data;
  const { 
    risk = { risk_score: 0, risk_level: 'UNKNOWN' }, 
    intelligence_layer = { identity_score: 0, document_score: 0, liveness_score: 0, forensic_score: 0 }, 
    fusion = { conflict_flags: [] } 
  } = module_breakdown || {};

  const getDecisionConfig = () => {
    switch (decision) {
      case 'ACCEPT': return { color: 'emerald', icon: ShieldCheck, label: 'Verified' };
      case 'REJECT': return { color: 'rose', icon: ShieldAlert, label: 'Rejected' };
      case 'REVIEW': return { color: 'amber', icon: ShieldQuestion, label: 'Under Review' };
      case 'ABSTAIN': return { color: 'slate', icon: AlertTriangle, label: 'Quality Reject' };
      default: return { color: 'slate', icon: Info, label: 'Inconclusive' };
    }
  };

  const config = getDecisionConfig();
  const moduleData = [
    { name: 'Identity', score: Math.round((intelligence_layer?.identity_score || 0) * 100) },
    { name: 'Document', score: Math.round((intelligence_layer?.document_score || 0) * 100) },
    { name: 'Liveness', score: Math.round((intelligence_layer?.liveness_score || 0) * 100) },
    { name: 'Forensic', score: Math.round((1 - (intelligence_layer?.forensic_score || 0)) * 100) },
  ];

  const riskGaugeData = [
    { name: 'Risk', value: Math.round((risk?.risk_score || 0) * 100) },
    { name: 'Safe', value: 100 - Math.round((risk?.risk_score || 0) * 100) },
  ];

  return (
    <motion.div 
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      className="max-w-6xl mx-auto p-6 md:p-10 space-y-8"
    >
      {/* Header Status */}
      <div className={`
        bg-white border-b-4 border-${config.color}-500 rounded-3xl p-8 shadow-2xl flex flex-col md:flex-row items-center justify-between gap-6
      `}>
        <div className="flex items-center gap-6">
          <div className={`p-5 bg-${config.color}-100 rounded-2xl`}>
            <config.icon className={`w-12 h-12 text-${config.color}-600`} />
          </div>
          <div>
            <h2 className="text-3xl font-bold text-slate-900 tracking-tight">{config.label}</h2>
            <p className="text-slate-500 font-medium mt-1">Session ID: <span className="font-mono text-xs">{data.session_id}</span></p>
          </div>
        </div>
        <div className="text-center md:text-right">
          <p className="text-sm font-semibold text-slate-400 uppercase tracking-widest mb-1">Confidence Score</p>
          <p className={`text-5xl font-black text-${config.color}-600`}>{(confidence_score * 100).toFixed(1)}%</p>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        {/* Left Column: Analytics */}
        <div className="lg:col-span-2 space-y-8">
          {/* Module Performance */}
          <div className="bg-white rounded-3xl p-8 shadow-lg border border-slate-100">
            <div className="flex items-center justify-between mb-8">
              <h3 className="text-xl font-bold text-slate-800 flex items-center gap-3">
                <Activity className="w-5 h-5 text-blue-500" />
                Intelligence Layer Breakdown
              </h3>
            </div>
            <div className="h-[300px] w-full">
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={moduleData} layout="vertical" margin={{ left: 20 }}>
                  <XAxis type="number" domain={[0, 100]} hide />
                  <YAxis dataKey="name" type="category" axisLine={false} tickLine={false} width={100} fontSize={14} fontWeight={600} />
                  <Tooltip cursor={{ fill: 'transparent' }} contentStyle={{ borderRadius: '12px', border: 'none', boxShadow: '0 10px 15px -3px rgb(0 0 0 / 0.1)' }} />
                  <Bar dataKey="score" radius={[0, 8, 8, 0]} barSize={32}>
                    {moduleData.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={entry.score > 70 ? '#10b981' : entry.score > 40 ? '#f59e0b' : '#ef4444'} />
                    ))}
                  </Bar>
                </BarChart>
              </ResponsiveContainer>
            </div>
          </div>

          {/* Reasoning & Conflicts */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
            <div className="bg-slate-50 rounded-3xl p-8 border border-slate-200">
              <h3 className="text-lg font-bold text-slate-800 mb-4 flex items-center gap-2">
                <ShieldCheck className="w-5 h-5 text-emerald-500" />
                Explainability
              </h3>
              <p className="text-slate-600 leading-relaxed text-sm">{data.explanation}</p>
            </div>
            <div className="bg-slate-50 rounded-3xl p-8 border border-slate-200">
              <h3 className="text-lg font-bold text-slate-800 mb-4 flex items-center gap-2">
                <AlertTriangle className="w-5 h-5 text-amber-500" />
                Security Flags
              </h3>
              <div className="flex flex-wrap gap-2">
                {fusion.conflict_flags.length > 0 ? (
                  fusion.conflict_flags.map((flag, i) => (
                    <span key={i} className="bg-amber-100 text-amber-700 text-xs font-bold px-3 py-1.5 rounded-full border border-amber-200 uppercase">
                      {flag.replace(/_/g, ' ')}
                    </span>
                  ))
                ) : (
                  <p className="text-emerald-600 font-medium text-sm">No critical conflicts detected.</p>
                )}
              </div>
            </div>
          </div>
        </div>

        {/* Right Column: Risk & Actions */}
        <div className="space-y-8">
          {/* Risk Gauge */}
          <div className="bg-white rounded-3xl p-8 shadow-lg border border-slate-100 text-center">
            <h3 className="text-lg font-bold text-slate-800 mb-6">Identity Risk Level</h3>
            <div className="h-[200px] relative">
              <ResponsiveContainer width="100%" height="100%">
                <PieChart>
                  <Pie
                    data={riskGaugeData}
                    cx="50%"
                    cy="80%"
                    startAngle={180}
                    endAngle={0}
                    innerRadius={60}
                    outerRadius={90}
                    paddingAngle={0}
                    dataKey="value"
                  >
                    <Cell fill={risk.risk_score > 0.7 ? '#ef4444' : risk.risk_score > 0.4 ? '#f59e0b' : '#10b981'} />
                    <Cell fill="#f1f5f9" />
                  </Pie>
                </PieChart>
              </ResponsiveContainer>
              <div className="absolute bottom-4 left-0 right-0">
                <p className="text-4xl font-black text-slate-800">{(risk.risk_score * 100).toFixed(0)}</p>
                <p className="text-xs font-bold text-slate-400 uppercase tracking-widest">{risk.risk_level} RISK</p>
              </div>
            </div>
          </div>

          {/* Action Button */}
          <button
            onClick={onReset}
            className="w-full bg-slate-900 hover:bg-black text-white font-bold py-5 rounded-2xl transition-all duration-300 shadow-xl flex items-center justify-center gap-3"
          >
            New Verification
          </button>
        </div>
      </div>
    </motion.div>
  );
};

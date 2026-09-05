import React from 'react';
import { Sparkles, Brain, CheckCircle2, AlertTriangle, Info, HelpCircle } from 'lucide-react';

export default function AiExplanation({ explanation, verdict, riskScore }) {
  if (!explanation) return null;

  const { provider, summary, key_findings = [], limitations = [], recommendation } = explanation;

  const isHighRisk = riskScore >= 50;

  return (
    <div className="w-full glass-panel rounded-2xl p-6 border border-slate-800 space-y-5 shadow-xl relative overflow-hidden">
      {/* Ambient background glow effect */}
      <div className="absolute -right-20 -top-20 w-64 h-64 bg-cyan-500/10 rounded-full blur-3xl pointer-events-none" />
      <div className="absolute -left-20 -bottom-20 w-64 h-64 bg-indigo-500/10 rounded-full blur-3xl pointer-events-none" />

      {/* Header */}
      <div className="flex flex-wrap items-center justify-between gap-3 border-b border-slate-800/80 pb-4">
        <div className="flex items-center space-x-2.5">
          <div className="p-2 rounded-lg bg-cyan-500/10 border border-cyan-500/20 text-cyan-400">
            <Sparkles className="w-5 h-5 animate-pulse" />
          </div>
          <div>
            <h3 className="text-base font-bold text-white flex items-center gap-2">
              GenAI Forensic Evidence Explanation
            </h3>
            <p className="text-xs text-slate-400">
              Grounded, factual analysis summary derived strictly from extracted signal metrics
            </p>
          </div>
        </div>

        {/* Provider badge */}
        <div className="flex items-center space-x-1.5 px-3 py-1.5 rounded-full bg-slate-900 border border-slate-800 text-xs font-medium text-cyan-300">
          <Brain className="w-3.5 h-3.5 text-cyan-400" />
          <span>{provider || 'Grounded Evidence Engine'}</span>
        </div>
      </div>

      {/* Overview Summary Box */}
      <div className={`p-4 rounded-xl border leading-relaxed text-sm ${
        isHighRisk
          ? 'bg-rose-950/20 border-rose-500/30 text-rose-200'
          : verdict === 'Inconclusive'
          ? 'bg-amber-950/20 border-amber-500/30 text-amber-200'
          : 'bg-slate-900/60 border-slate-800 text-slate-200'
      }`}>
        <p className="font-medium">{summary}</p>
      </div>

      {/* Grid: Key Findings & Limitations */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {/* Key Findings */}
        <div className="p-4 rounded-xl bg-slate-900/50 border border-slate-800/80 space-y-3">
          <div className="flex items-center space-x-2 text-xs font-bold uppercase tracking-wider text-slate-300">
            <CheckCircle2 className="w-4 h-4 text-cyan-400" />
            <span>Key Forensic Evidence</span>
          </div>
          <ul className="space-y-2 text-xs text-slate-300">
            {key_findings.map((item, idx) => (
              <li key={idx} className="flex items-start space-x-2">
                <span className="text-cyan-400 font-bold mt-0.5">•</span>
                <span className="leading-relaxed">{item}</span>
              </li>
            ))}
          </ul>
        </div>

        {/* Missing Evidence & Limitations */}
        <div className="p-4 rounded-xl bg-slate-900/50 border border-slate-800/80 space-y-3">
          <div className="flex items-center space-x-2 text-xs font-bold uppercase tracking-wider text-slate-300">
            <HelpCircle className="w-4 h-4 text-indigo-400" />
            <span>Limitations & Provenance Context</span>
          </div>
          <ul className="space-y-2 text-xs text-slate-400">
            {limitations.map((item, idx) => (
              <li key={idx} className="flex items-start space-x-2">
                <span className="text-indigo-400 font-bold mt-0.5">•</span>
                <span className="leading-relaxed">{item}</span>
              </li>
            ))}
          </ul>
        </div>
      </div>

      {/* Grounded Recommendation Banner */}
      {recommendation && (
        <div className="p-3.5 rounded-xl bg-cyan-950/20 border border-cyan-500/30 flex items-start space-x-3 text-xs text-cyan-200">
          <Info className="w-4.5 h-4.5 text-cyan-400 flex-shrink-0 mt-0.5" />
          <div>
            <strong className="text-cyan-300 font-semibold">Assessment Advisory: </strong>
            <span>{recommendation}</span>
          </div>
        </div>
      )}
    </div>
  );
}

import React from 'react';
import { ShieldCheck, ShieldAlert, AlertTriangle, Info, FileText } from 'lucide-react';
import { getVerdictColor } from '../utils/formatters';

export default function VerdictBanner({ result }) {
  if (!result) return null;

  const { verdict, risk_score, confidence, summary_explanation, filename, format, dimensions, file_size } = result;
  const style = getVerdictColor(verdict, risk_score);

  const getIcon = () => {
    if (verdict === 'Likely Authentic') return <ShieldCheck className="w-8 h-8 text-emerald-400 stroke-[2.2]" />;
    if (verdict === 'Inconclusive') return <AlertTriangle className="w-8 h-8 text-amber-400 stroke-[2.2]" />;
    return <ShieldAlert className="w-8 h-8 text-rose-400 stroke-[2.2]" />;
  };

  return (
    <div className={`w-full rounded-2xl border p-6 md:p-8 ${style.bg} ${style.border} shadow-2xl relative overflow-hidden`}>
      {/* Background Accent Blur */}
      <div
        className="absolute -right-20 -top-20 w-64 h-64 rounded-full blur-3xl opacity-15 pointer-events-none"
        style={{ backgroundColor: style.accent }}
      />

      <div className="flex flex-col lg:flex-row items-start lg:items-center justify-between gap-6 relative z-10">
        {/* Verdict Badge & Summary */}
        <div className="space-y-3 flex-1">
          <div className="flex flex-wrap items-center gap-3">
            <div className={`flex items-center space-x-2.5 px-4 py-1.5 rounded-full border ${style.badge} font-bold text-sm uppercase tracking-wider`}>
              {getIcon()}
              <span>{verdict}</span>
            </div>

            <div className="px-3 py-1 rounded-full bg-slate-900/80 border border-slate-800 text-xs font-semibold text-slate-300">
              Confidence: <strong className="text-white">{confidence}%</strong>
            </div>

            <div className="px-3 py-1 rounded-full bg-slate-900/80 border border-slate-800 text-xs font-mono text-slate-400">
              {filename} ({format} · {dimensions?.width}x{dimensions?.height})
            </div>
          </div>

          <div>
            <h2 className="text-2xl md:text-3xl font-black text-white tracking-tight">
              Forensic Assessment Summary
            </h2>
            <p className="text-slate-300 text-sm md:text-base leading-relaxed mt-1 max-w-3xl">
              {summary_explanation}
            </p>
          </div>
        </div>

        {/* Risk Score Meter (0 - 100) */}
        <div className="flex items-center justify-center space-x-6 p-4 rounded-xl bg-slate-950/70 border border-slate-800/80 flex-shrink-0 min-w-[240px]">
          <div className="text-center">
            <span className="text-xs uppercase font-bold text-slate-400 tracking-wider block mb-1">
              Manipulation Risk
            </span>
            <div className="flex items-baseline justify-center space-x-1">
              <span className={`text-4xl md:text-5xl font-black ${style.text}`}>
                {risk_score}
              </span>
              <span className="text-slate-500 font-bold text-lg">/100</span>
            </div>
            {/* Linear Progress Bar */}
            <div className="w-36 h-2 bg-slate-800 rounded-full mt-2.5 overflow-hidden mx-auto">
              <div
                className="h-full transition-all duration-1000 ease-out rounded-full"
                style={{
                  width: `${risk_score}%`,
                  backgroundColor: style.accent,
                }}
              />
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

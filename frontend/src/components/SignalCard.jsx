import React, { useState } from 'react';
import { Camera, Layers, Activity, Cpu, ChevronDown, ChevronUp, AlertCircle } from 'lucide-react';
import { getSeverityBadge } from '../utils/formatters';

export default function SignalCard({ signal }) {
  const [showMetrics, setShowMetrics] = useState(false);

  if (!signal) return null;

  const { id, name, score, severity, confidence, description, metrics } = signal;

  const getSignalIcon = (signalId) => {
    switch (signalId) {
      case 'exif_software_tag':
        return <Camera className="w-5 h-5 text-cyan-400" />;
      case 'error_level_analysis':
        return <Layers className="w-5 h-5 text-emerald-400" />;
      case 'fft_spectral_grid':
        return <Cpu className="w-5 h-5 text-indigo-400" />;
      case 'noise_residual':
        return <Activity className="w-5 h-5 text-amber-400" />;
      default:
        return <AlertCircle className="w-5 h-5 text-cyan-400" />;
    }
  };

  const severityBadgeClass = getSeverityBadge(severity);

  return (
    <div className="glass-panel glass-panel-hover rounded-2xl p-5 border border-slate-800 space-y-3 flex flex-col justify-between">
      <div>
        {/* Header with Title & Badges */}
        <div className="flex items-start justify-between gap-3 mb-2">
          <div className="flex items-center space-x-2.5">
            <div className="p-2 rounded-xl bg-slate-900 border border-slate-800">
              {getSignalIcon(id)}
            </div>
            <div>
              <h4 className="text-base font-bold text-white leading-tight">{name}</h4>
              <span className="text-[11px] text-slate-400 font-medium">Confidence: {confidence}%</span>
            </div>
          </div>

          <div className="flex items-center space-x-2">
            <span className={`px-2.5 py-1 rounded-full border text-xs font-bold ${severityBadgeClass}`}>
              {severity}
            </span>
            <div className="px-2.5 py-1 rounded-full bg-slate-900 border border-slate-800 text-xs font-black text-slate-200">
              {score}<span className="text-[10px] text-slate-500 font-bold">/100</span>
            </div>
          </div>
        </div>

        {/* Plain Language Description */}
        <p className="text-xs text-slate-300 leading-relaxed pt-1">
          {description}
        </p>
      </div>

      {/* Expandable Technical Metrics */}
      {metrics && Object.keys(metrics).length > 0 && (
        <div className="pt-2 border-t border-slate-800/80">
          <button
            onClick={() => setShowMetrics(!showMetrics)}
            className="w-full flex items-center justify-between text-[11px] font-semibold text-slate-400 hover:text-cyan-400 py-1 transition"
          >
            <span>Technical Metrics Breakdown</span>
            {showMetrics ? <ChevronUp className="w-3.5 h-3.5" /> : <ChevronDown className="w-3.5 h-3.5" />}
          </button>

          {showMetrics && (
            <div className="mt-2 grid grid-cols-2 gap-2 p-2.5 rounded-xl bg-slate-950/80 border border-slate-800 text-[11px] font-mono text-slate-300">
              {Object.entries(metrics).map(([key, val]) => (
                <div key={key} className="truncate">
                  <span className="text-slate-500 block text-[10px]">{key}</span>
                  <span className="font-semibold text-slate-200 truncate">
                    {Array.isArray(val) ? val.join(', ') || 'None' : val === null ? 'N/A' : String(val)}
                  </span>
                </div>
              ))}
            </div>
          )}
        </div>
      )}
    </div>
  );
}

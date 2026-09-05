import React, { useEffect, useState } from 'react';
import { Loader2, CheckCircle2, ShieldCheck, Scan, Cpu } from 'lucide-react';

const ANALYSIS_STEPS = [
  'Validating binary structure & MIME headers',
  'Extracting camera EXIF & software parameters',
  'Computing Error Level Analysis (ELA) variance',
  'Analyzing high-pass noise & channel covariance',
  'Calculating 2D FFT frequency grid artifacts',
  'Synthesizing weighted risk score & verdict',
];

export default function ProcessingState({ file }) {
  const [activeStep, setActiveStep] = useState(0);

  useEffect(() => {
    const timer = setInterval(() => {
      setActiveStep((prev) => (prev < ANALYSIS_STEPS.length - 1 ? prev + 1 : prev));
    }, 450);
    return () => clearInterval(timer);
  }, []);

  return (
    <div className="w-full max-w-2xl mx-auto glass-panel rounded-2xl p-8 border border-slate-800 text-center space-y-6 shadow-2xl">
      {/* Scanning Graphic */}
      <div className="relative w-24 h-24 mx-auto flex items-center justify-center rounded-2xl bg-cyan-500/10 border border-cyan-500/30 overflow-hidden shadow-xl shadow-cyan-500/10">
        <Scan className="w-12 h-12 text-cyan-400 animate-pulse" />
        <div className="absolute inset-x-0 h-1 bg-gradient-to-r from-transparent via-cyan-400 to-transparent animate-radar top-0"></div>
      </div>

      <div>
        <h3 className="text-xl font-extrabold text-white mb-1">
          Executing Multi-Signal Forensic Pipeline
        </h3>
        <p className="text-xs text-slate-400">
          Target Media: <span className="text-slate-200 font-semibold">{file?.name || 'Image'}</span>
        </p>
      </div>

      {/* Progress Steps List */}
      <div className="space-y-2.5 text-left max-w-md mx-auto pt-2">
        {ANALYSIS_STEPS.map((step, idx) => {
          const isDone = idx < activeStep;
          const isCurrent = idx === activeStep;

          return (
            <div
              key={idx}
              className={`flex items-center space-x-3 p-2.5 rounded-lg border transition duration-200 ${
                isCurrent
                  ? 'bg-cyan-500/10 border-cyan-500/30 text-cyan-300 font-medium'
                  : isDone
                  ? 'bg-slate-900/60 border-slate-800 text-slate-400'
                  : 'bg-slate-950/40 border-slate-900 text-slate-600'
              }`}
            >
              {isDone ? (
                <CheckCircle2 className="w-4 h-4 text-emerald-400 flex-shrink-0" />
              ) : isCurrent ? (
                <Loader2 className="w-4 h-4 text-cyan-400 animate-spin flex-shrink-0" />
              ) : (
                <div className="w-4 h-4 rounded-full border border-slate-700 flex-shrink-0" />
              )}
              <span className="text-xs truncate">{step}</span>
            </div>
          );
        })}
      </div>
    </div>
  );
}

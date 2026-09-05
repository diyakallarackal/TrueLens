import React from 'react';
import { Activity, Info, BarChart2 } from 'lucide-react';

export default function SpectrogramViewer({ spectrogramBase64 }) {
  if (!spectrogramBase64) return null;

  return (
    <div className="w-full glass-panel rounded-2xl p-6 border border-slate-800 space-y-4 shadow-xl">
      <div className="flex items-center justify-between pb-3 border-b border-slate-800">
        <div>
          <div className="flex items-center space-x-2 text-cyan-400 text-xs font-bold uppercase tracking-wider mb-0.5">
            <Activity className="w-4 h-4" />
            <span>Short-Time Fourier Transform (STFT)</span>
          </div>
          <h3 className="text-lg font-bold text-white">
            Log-Magnitude Spectrogram Heatmap
          </h3>
        </div>
      </div>

      {/* Spectrogram Canvas Image Container */}
      <div className="relative w-full h-64 md:h-80 rounded-xl overflow-hidden bg-slate-950 border border-slate-800 flex items-center justify-center p-2 group">
        <img
          src={spectrogramBase64}
          alt="STFT Spectrogram Heatmap"
          className="w-full h-full object-fill rounded-lg"
        />
        
        {/* Frequency Y-axis labels */}
        <div className="absolute left-4 top-4 bottom-4 flex flex-col justify-between text-[10px] font-mono text-cyan-300 pointer-events-none bg-slate-950/80 px-1.5 py-1 rounded border border-slate-800">
          <span>High (22kHz)</span>
          <span>Mid (5kHz)</span>
          <span>Low (0Hz)</span>
        </div>
      </div>

      <div className="p-3.5 rounded-xl bg-slate-900/90 border border-slate-800 flex items-start space-x-3 text-xs text-slate-300">
        <Info className="w-4 h-4 text-cyan-400 flex-shrink-0 mt-0.5" />
        <p>
          <strong className="text-white">Understanding Spectrograms:</strong> The STFT spectrogram maps acoustic energy intensity across frequency bands (vertical axis) over time (horizontal axis). Synthetic voices often show unnatural high-frequency cutoffs, phase smearing, or artificial energy bands.
        </p>
      </div>
    </div>
  );
}

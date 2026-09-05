import React from 'react';
import { Search, CheckCircle2, Info } from 'lucide-react';

export default function WhatWeFound({ observations }) {
  if (!observations || observations.length === 0) return null;

  return (
    <div className="w-full glass-panel rounded-2xl p-6 border border-slate-800 space-y-4 shadow-xl">
      <div className="flex items-center space-x-2 text-cyan-400 text-xs font-bold uppercase tracking-wider pb-2 border-b border-slate-800">
        <Search className="w-4 h-4" />
        <span>Media Verification Findings Summary</span>
      </div>

      <div className="space-y-2.5">
        <h3 className="text-lg font-extrabold text-white">WHAT WE FOUND</h3>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
          {observations.map((item, idx) => (
            <div
              key={idx}
              className="flex items-start space-x-3 p-3.5 rounded-xl bg-slate-900/90 border border-slate-800 text-xs text-slate-200"
            >
              <CheckCircle2 className="w-4 h-4 text-cyan-400 flex-shrink-0 mt-0.5" />
              <span className="leading-relaxed font-medium">{item}</span>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}

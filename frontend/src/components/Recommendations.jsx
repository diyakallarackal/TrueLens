import React from 'react';
import { AlertCircle, ExternalLink, ShieldCheck, HelpCircle, FileCheck2 } from 'lucide-react';

export default function Recommendations({ recommendation, disclaimer, riskScore }) {
  return (
    <div className="w-full glass-panel rounded-2xl p-6 border border-slate-800 space-y-5 shadow-xl">
      <div className="flex items-center space-x-2 text-cyan-400 text-xs font-bold uppercase tracking-wider">
        <FileCheck2 className="w-4 h-4" />
        <span>Actionable Guidance & Verification Advisory</span>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {/* Recommendation Box */}
        <div className={`p-4 rounded-xl border flex items-start space-x-3.5 ${
          riskScore >= 50
            ? 'bg-rose-500/10 border-rose-500/30 text-rose-300'
            : 'bg-emerald-500/10 border-emerald-500/30 text-emerald-300'
        }`}>
          <AlertCircle className="w-5 h-5 flex-shrink-0 mt-0.5" />
          <div>
            <h4 className="text-sm font-bold text-white mb-1">Recommended Action</h4>
            <p className="text-xs leading-relaxed">
              {recommendation || "Treat as potentially manipulated and verify the source before sharing."}
            </p>
          </div>
        </div>

        {/* Modular Source Verification / Reverse Search Architecture Badge */}
        <div className="p-4 rounded-xl bg-slate-900/80 border border-slate-800 flex items-start space-x-3.5 text-slate-300">
          <ExternalLink className="w-5 h-5 text-cyan-400 flex-shrink-0 mt-0.5" />
          <div>
            <div className="flex items-center space-x-2">
              <h4 className="text-sm font-bold text-white mb-0.5">Source & Reverse Search Integration</h4>
              <span className="px-1.5 py-0.5 text-[9px] font-bold rounded bg-cyan-500/10 text-cyan-400 border border-cyan-500/20">Modular</span>
            </div>
            <p className="text-xs leading-relaxed text-slate-400">
              TrueLens reverse-media pipeline adapter is ready to connect Google Vision / TinEye APIs for origin verification without synthetic reverse-search mock data.
            </p>
          </div>
        </div>
      </div>

      {/* Uncertainty Disclaimer Banner */}
      <div className="p-4 rounded-xl bg-slate-950/80 border border-slate-800/80 flex items-start space-x-3 text-xs text-slate-400">
        <HelpCircle className="w-4.5 h-4.5 text-slate-400 flex-shrink-0 mt-0.5" />
        <p className="leading-relaxed">
          <strong className="text-slate-300">Legal & Forensic Disclaimer:</strong> {disclaimer || "This result is an automated forensic assessment based on measurable image metrics and statistical signals, not absolute proof. Always cross-verify critical media through independent source verification."}
        </p>
      </div>
    </div>
  );
}

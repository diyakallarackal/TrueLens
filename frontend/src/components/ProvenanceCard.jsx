import React from 'react';
import { Award, ExternalLink, CheckCircle, XCircle, Clock, ShieldCheck, AlertCircle, Info } from 'lucide-react';

export default function ProvenanceCard({ provenance }) {
  if (!provenance) return null;

  const timeline = provenance.timeline || [];
  const c2pa = provenance.c2pa || {};
  const metaAssess = provenance.metadata_assessment || {};
  const extSearch = provenance.external_search || {};

  const getStatusBadge = (status) => {
    switch (status) {
      case 'detected':
        return <span className="px-2 py-0.5 rounded text-[10px] font-bold bg-emerald-500/10 text-emerald-400 border border-emerald-500/30">Detected</span>;
      case 'not_detected':
        return <span className="px-2 py-0.5 rounded text-[10px] font-bold bg-slate-800 text-slate-400 border border-slate-700">Not detected</span>;
      case 'not_available':
        return <span className="px-2 py-0.5 rounded text-[10px] font-bold bg-amber-500/10 text-amber-400 border border-amber-500/30">Not available</span>;
      default:
        return <span className="px-2 py-0.5 rounded text-[10px] font-bold bg-cyan-500/10 text-cyan-400 border border-cyan-500/30">Not configured</span>;
    }
  };

  return (
    <div className="w-full glass-panel rounded-2xl p-6 border border-slate-800 space-y-6 shadow-xl">
      <div className="flex items-center space-x-2 text-cyan-400 text-xs font-bold uppercase tracking-wider pb-3 border-b border-slate-800">
        <Award className="w-4 h-4" />
        <span>Source & Provenance Verification Suite</span>
      </div>

      {/* Provenance Verification Timeline */}
      {timeline.length > 0 && (
        <div className="space-y-3">
          <h4 className="text-sm font-bold text-white uppercase tracking-wider text-slate-400">
            Provenance Verification Timeline
          </h4>
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-3">
            {timeline.map((step, idx) => (
              <div key={idx} className="p-3.5 rounded-xl bg-slate-900/90 border border-slate-800 space-y-2">
                <div className="flex items-center justify-between">
                  <span className="text-xs font-extrabold text-white">{step.stage}</span>
                  {getStatusBadge(step.status)}
                </div>
                <p className="text-[11px] text-slate-300 leading-relaxed font-medium">
                  {step.label}
                </p>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Grid of Provenance Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {/* Content Credentials Card */}
        <div className={`p-4 rounded-xl border space-y-2.5 ${
          c2pa.has_c2pa
            ? 'bg-emerald-500/10 border-emerald-500/30 text-emerald-300'
            : 'bg-slate-900/80 border-slate-800 text-slate-300'
        }`}>
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-2">
              {c2pa.has_c2pa ? (
                <CheckCircle className="w-4.5 h-4.5 text-emerald-400" />
              ) : (
                <XCircle className="w-4.5 h-4.5 text-slate-500" />
              )}
              <h4 className="text-sm font-bold text-white">Content Credentials (C2PA)</h4>
            </div>
            {getStatusBadge(c2pa.has_c2pa ? 'detected' : 'not_detected')}
          </div>

          <p className="text-xs font-semibold text-slate-200">
            {c2pa.c2pa_status || 'No Content Credentials found'}
          </p>

          {c2pa.has_c2pa && (
            <div className="pt-2 text-xs font-mono space-y-1 text-slate-300 border-t border-emerald-500/20">
              {c2pa.issuer && <div><span className="text-slate-400">Issuer:</span> {c2pa.issuer}</div>}
              {c2pa.claim_generator && <div><span className="text-slate-400">Claim Tool:</span> {c2pa.claim_generator}</div>}
            </div>
          )}

          {!c2pa.has_c2pa && (
            <p className="text-[11px] text-slate-400 pt-1 leading-normal">
              Absence of Content Credentials does NOT mean the media is fake. Many legitimate devices do not embed C2PA manifests.
            </p>
          )}
        </div>

        {/* External Reverse Source Search Card */}
        <div className="p-4 rounded-xl bg-slate-900/80 border border-slate-800 space-y-2.5 text-slate-300">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-2">
              <ExternalLink className="w-4.5 h-4.5 text-cyan-400" />
              <h4 className="text-sm font-bold text-white">External Source Search</h4>
            </div>
            {getStatusBadge(extSearch.status || 'unconfigured')}
          </div>

          <p className="text-xs text-slate-300 font-semibold">
            {extSearch.message || 'External source search is not configured.'}
          </p>

          <p className="text-[11px] text-slate-400 pt-1 leading-normal border-t border-slate-800">
            TrueLens modular suite connects Google Vision and TinEye APIs via environment variables without faking reverse-search matches.
          </p>
        </div>
      </div>

      {/* Explanatory Context Banner */}
      <div className="p-3.5 rounded-xl bg-slate-950/80 border border-slate-800/80 flex items-start space-x-3 text-xs text-slate-400">
        <Info className="w-4 h-4 text-cyan-400 flex-shrink-0 mt-0.5" />
        <p className="leading-relaxed">
          <strong className="text-slate-300">Provenance Context:</strong> Source and provenance information provides additional context. It should be evaluated alongside forensic signals and does not independently prove whether media is authentic.
        </p>
      </div>
    </div>
  );
}

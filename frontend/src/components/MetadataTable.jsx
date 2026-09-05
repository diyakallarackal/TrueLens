import React, { useState } from 'react';
import { Camera, Search, CheckCircle, XCircle, Info } from 'lucide-react';

export default function MetadataTable({ metadata }) {
  const [searchTerm, setSearchTerm] = useState('');

  if (!metadata) return null;

  const { has_exif, raw_tags, camera_make, camera_model, software_detected, has_camera_hardware } = metadata;
  const tagsList = Object.entries(raw_tags || {});

  const filteredTags = tagsList.filter(([k, v]) =>
    k.toLowerCase().includes(searchTerm.toLowerCase()) ||
    String(v).toLowerCase().includes(searchTerm.toLowerCase())
  );

  return (
    <div className="w-full glass-panel rounded-2xl p-6 border border-slate-800 space-y-4 shadow-xl">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-3 border-b border-slate-800">
        <div>
          <div className="flex items-center space-x-2 text-cyan-400 text-xs font-bold uppercase tracking-wider mb-0.5">
            <Camera className="w-4 h-4" />
            <span>Image Header Inspection</span>
          </div>
          <h3 className="text-lg font-bold text-white">
            Metadata & EXIF Information
          </h3>
        </div>

        {/* Quick Search */}
        {has_exif && (
          <div className="relative">
            <Search className="w-4 h-4 text-slate-400 absolute left-3 top-1/2 -translate-y-1/2" />
            <input
              type="text"
              placeholder="Search tags..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="pl-9 pr-4 py-1.5 rounded-xl bg-slate-900 border border-slate-800 text-xs text-white placeholder-slate-500 focus:outline-none focus:border-cyan-500 transition w-full sm:w-48"
            />
          </div>
        )}
      </div>

      {/* Highlights summary pills */}
      <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
        <div className="p-3 rounded-xl bg-slate-900/80 border border-slate-800">
          <span className="text-xs text-slate-400 block mb-1">EXIF Present</span>
          <div className="flex items-center space-x-1.5 font-bold text-sm">
            {has_exif ? (
              <>
                <CheckCircle className="w-4 h-4 text-emerald-400" />
                <span className="text-emerald-400">Yes</span>
              </>
            ) : (
              <>
                <XCircle className="w-4 h-4 text-rose-400" />
                <span className="text-rose-400">Missing</span>
              </>
            )}
          </div>
        </div>

        <div className="p-3 rounded-xl bg-slate-900/80 border border-slate-800">
          <span className="text-xs text-slate-400 block mb-1">Camera Hardware</span>
          <div className="flex items-center space-x-1.5 font-bold text-sm">
            {has_camera_hardware ? (
              <>
                <CheckCircle className="w-4 h-4 text-emerald-400" />
                <span className="text-emerald-400">Detected</span>
              </>
            ) : (
              <>
                <XCircle className="w-4 h-4 text-amber-400" />
                <span className="text-amber-400">None</span>
              </>
            )}
          </div>
        </div>

        <div className="p-3 rounded-xl bg-slate-900/80 border border-slate-800">
          <span className="text-xs text-slate-400 block mb-1">Camera Make & Model</span>
          <span className="text-xs font-semibold text-slate-200 truncate block">
            {camera_make || camera_model ? `${camera_make || ''} ${camera_model || ''}` : 'Not Specified'}
          </span>
        </div>

        <div className="p-3 rounded-xl bg-slate-900/80 border border-slate-800">
          <span className="text-xs text-slate-400 block mb-1">Software Tag</span>
          <span className={`text-xs font-semibold truncate block ${software_detected ? 'text-amber-400 font-bold' : 'text-slate-400'}`}>
            {software_detected || 'None Recorded'}
          </span>
        </div>
      </div>

      {/* Raw EXIF Table */}
      {has_exif && filteredTags.length > 0 ? (
        <div className="max-h-60 overflow-y-auto rounded-xl border border-slate-800 bg-slate-950/60">
          <table className="w-full text-left text-xs">
            <thead className="sticky top-0 bg-slate-900 border-b border-slate-800 text-slate-400 font-semibold">
              <tr>
                <th className="px-4 py-2.5">EXIF Tag</th>
                <th className="px-4 py-2.5">Value</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/60 font-mono text-slate-300">
              {filteredTags.map(([tag, value]) => (
                <tr key={tag} className="hover:bg-slate-900/40">
                  <td className="px-4 py-2 text-cyan-400 font-semibold">{tag}</td>
                  <td className="px-4 py-2 break-all text-slate-200">{String(value)}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      ) : (
        <div className="p-4 text-center rounded-xl bg-slate-950/40 border border-slate-800 text-xs text-slate-400">
          {has_exif ? 'No EXIF tags match search filter.' : 'This image file does not contain standard embedded EXIF metadata tags.'}
        </div>
      )}
    </div>
  );
}

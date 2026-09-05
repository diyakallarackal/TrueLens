import React, { useEffect, useState } from 'react';
import { Play, X, FileCheck, HardDrive, Maximize2, Sparkles } from 'lucide-react';
import { formatBytes } from '../utils/formatters';

export default function ImagePreview({ file, onAnalyze, onReset }) {
  const [previewUrl, setPreviewUrl] = useState(null);
  const [dimensions, setDimensions] = useState(null);

  useEffect(() => {
    if (!file) return;
    const url = URL.createObjectURL(file);
    setPreviewUrl(url);

    const img = new Image();
    img.src = url;
    img.onload = () => {
      setDimensions({ width: img.naturalWidth, height: img.naturalHeight });
    };

    return () => {
      URL.revokeObjectURL(url);
    };
  }, [file]);

  if (!file) return null;

  return (
    <div className="w-full max-w-4xl mx-auto glass-panel rounded-2xl p-6 md:p-8 border border-slate-800 shadow-2xl">
      <div className="flex flex-col md:flex-row items-center gap-6">
        {/* Thumbnail Preview Container */}
        <div className="relative w-full md:w-64 h-64 rounded-xl overflow-hidden bg-slate-950 border border-slate-800 flex items-center justify-center group flex-shrink-0">
          {previewUrl && (
            <img
              src={previewUrl}
              alt="Uploaded file preview"
              className="w-full h-full object-contain p-2"
            />
          )}
          <div className="absolute inset-0 bg-gradient-to-t from-slate-950/80 via-transparent to-transparent opacity-0 group-hover:opacity-100 transition duration-200 flex items-end p-3">
            <span className="text-xs text-slate-300 font-medium truncate">
              {file.name}
            </span>
          </div>
        </div>

        {/* File Metadata & Actions */}
        <div className="flex-1 w-full space-y-4">
          <div>
            <div className="flex items-center space-x-2 text-cyan-400 text-xs font-bold uppercase tracking-wider mb-1">
              <FileCheck className="w-4 h-4" />
              <span>Target Media Ready</span>
            </div>
            <h2 className="text-xl md:text-2xl font-extrabold text-white truncate">
              {file.name}
            </h2>
          </div>

          <div className="grid grid-cols-2 sm:grid-cols-3 gap-3 pt-1">
            <div className="p-3 rounded-lg bg-slate-900/80 border border-slate-800">
              <span className="text-xs text-slate-400 block mb-0.5">File Size</span>
              <span className="text-sm font-semibold text-slate-200">
                {formatBytes(file.size)}
              </span>
            </div>

            <div className="p-3 rounded-lg bg-slate-900/80 border border-slate-800">
              <span className="text-xs text-slate-400 block mb-0.5">Format</span>
              <span className="text-sm font-semibold text-slate-200 uppercase">
                {file.type.replace('image/', '') || 'JPEG'}
              </span>
            </div>

            <div className="p-3 rounded-lg bg-slate-900/80 border border-slate-800 col-span-2 sm:col-span-1">
              <span className="text-xs text-slate-400 block mb-0.5">Resolution</span>
              <span className="text-sm font-semibold text-slate-200">
                {dimensions ? `${dimensions.width} × ${dimensions.height}` : 'Loading...'}
              </span>
            </div>
          </div>

          <div className="flex items-center space-x-3 pt-3">
            <button
              onClick={onAnalyze}
              className="flex-1 flex items-center justify-center space-x-2.5 px-6 py-3.5 rounded-xl bg-gradient-to-r from-cyan-500 to-emerald-500 hover:from-cyan-400 hover:to-emerald-400 text-slate-950 font-extrabold text-base shadow-lg shadow-cyan-500/20 transition duration-150 transform active:scale-[0.99]"
            >
              <Sparkles className="w-5 h-5 fill-slate-950" />
              <span>Analyze Image Signals</span>
            </button>

            <button
              onClick={onReset}
              className="px-4 py-3.5 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-300 hover:text-white font-semibold text-sm border border-slate-700 transition"
              title="Select different image"
            >
              <X className="w-5 h-5" />
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}

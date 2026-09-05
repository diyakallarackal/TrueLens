import React, { useState } from 'react';
import { Eye, Layers, Sliders, Info, Zap } from 'lucide-react';

export default function ElaViewer({ originalImageFile, elaBase64 }) {
  const [viewMode, setViewMode] = useState('ela'); // 'original', 'ela', 'split'
  const [splitPos, setSplitPos] = useState(50); // % position for split slider

  const originalUrl = originalImageFile ? URL.createObjectURL(originalImageFile) : null;

  if (!elaBase64) return null;

  return (
    <div className="w-full glass-panel rounded-2xl p-6 border border-slate-800 space-y-4 shadow-xl">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-3 border-b border-slate-800">
        <div>
          <div className="flex items-center space-x-2 text-cyan-400 text-xs font-bold uppercase tracking-wider mb-0.5">
            <Layers className="w-4 h-4" />
            <span>Forensic Heatmap Inspection</span>
          </div>
          <h3 className="text-lg font-bold text-white">
            Error Level Analysis (ELA) Map
          </h3>
        </div>

        {/* View Mode Controller */}
        <div className="flex items-center p-1 rounded-xl bg-slate-900 border border-slate-800 text-xs font-semibold">
          <button
            onClick={() => setViewMode('ela')}
            className={`px-3 py-1.5 rounded-lg transition ${
              viewMode === 'ela'
                ? 'bg-cyan-500 text-slate-950 font-bold shadow'
                : 'text-slate-400 hover:text-slate-200'
            }`}
          >
            ELA Heatmap
          </button>
          <button
            onClick={() => setViewMode('split')}
            className={`px-3 py-1.5 rounded-lg transition ${
              viewMode === 'split'
                ? 'bg-cyan-500 text-slate-950 font-bold shadow'
                : 'text-slate-400 hover:text-slate-200'
            }`}
          >
            Interactive Split
          </button>
          {originalUrl && (
            <button
              onClick={() => setViewMode('original')}
              className={`px-3 py-1.5 rounded-lg transition ${
                viewMode === 'original'
                  ? 'bg-cyan-500 text-slate-950 font-bold shadow'
                  : 'text-slate-400 hover:text-slate-200'
              }`}
            >
              Original Source
            </button>
          )}
        </div>
      </div>

      {/* Viewer Canvas Container */}
      <div className="relative w-full h-[360px] md:h-[480px] rounded-xl overflow-hidden bg-slate-950 border border-slate-800 flex items-center justify-center select-none group">
        {viewMode === 'ela' && (
          <img
            src={elaBase64}
            alt="Error Level Analysis (ELA) Heatmap"
            className="w-full h-full object-contain p-2"
          />
        )}

        {viewMode === 'original' && originalUrl && (
          <img
            src={originalUrl}
            alt="Original uploaded image"
            className="w-full h-full object-contain p-2"
          />
        )}

        {viewMode === 'split' && originalUrl && (
          <div className="relative w-full h-full flex items-center justify-center p-2">
            {/* ELA Heatmap (Base layer) */}
            <img
              src={elaBase64}
              alt="ELA Map"
              className="absolute inset-0 w-full h-full object-contain p-2"
            />
            {/* Original Image (Clipped layer) */}
            <div
              className="absolute inset-0 overflow-hidden p-2"
              style={{ width: `${splitPos}%` }}
            >
              <img
                src={originalUrl}
                alt="Original Source"
                className="w-full h-full object-contain"
                style={{ width: '100%', maxWidth: 'none' }}
              />
            </div>
            {/* Divider Line */}
            <div
              className="absolute top-0 bottom-0 w-0.5 bg-cyan-400 shadow-lg shadow-cyan-500/50 cursor-ew-resize z-20 flex items-center justify-center"
              style={{ left: `${splitPos}%` }}
            >
              <div className="w-6 h-6 rounded-full bg-cyan-400 text-slate-950 flex items-center justify-center text-[10px] font-black shadow-md">
                ↔
              </div>
            </div>
          </div>
        )}
      </div>

      {/* Interactive Slider Bar for Split Mode */}
      {viewMode === 'split' && (
        <div className="flex items-center space-x-3 px-2">
          <span className="text-xs text-slate-400 font-medium">Original</span>
          <input
            type="range"
            min="0"
            max="100"
            value={splitPos}
            onChange={(e) => setSplitPos(Number(e.target.value))}
            className="flex-1 accent-cyan-400 bg-slate-800 h-1.5 rounded-lg cursor-pointer"
          />
          <span className="text-xs text-cyan-400 font-medium">ELA Heatmap</span>
        </div>
      )}

      {/* Explanation Footer */}
      <div className="p-3.5 rounded-xl bg-slate-900/90 border border-slate-800 flex items-start space-x-3 text-xs text-slate-300">
        <Info className="w-4 h-4 text-cyan-400 flex-shrink-0 mt-0.5" />
        <p>
          <strong className="text-white">Understanding ELA:</strong> Error Level Analysis re-compresses the image as JPEG at Quality 95 to measure compression error rates across regions. Regions with bright, non-uniform highlights indicate different compression histories (e.g. pasted elements or AI post-processing).
        </p>
      </div>
    </div>
  );
}

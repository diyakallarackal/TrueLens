import React, { useState } from 'react';
import { Film, Eye, Layers, Clock, Info, ChevronRight, ChevronLeft } from 'lucide-react';

export default function FrameViewer({ sampledFrames }) {
  const [activeFrameIndex, setActiveFrameIndex] = useState(0);
  const [viewMode, setViewMode] = useState('frame'); // 'frame' | 'ela'

  if (!sampledFrames || sampledFrames.length === 0) return null;

  const currentFrame = sampledFrames[activeFrameIndex] || sampledFrames[0];

  return (
    <div className="w-full glass-panel rounded-2xl p-6 border border-slate-800 space-y-5 shadow-xl">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-3 border-b border-slate-800">
        <div>
          <div className="flex items-center space-x-2 text-cyan-400 text-xs font-bold uppercase tracking-wider mb-0.5">
            <Film className="w-4 h-4" />
            <span>Keyframe Forensic Inspection</span>
          </div>
          <h3 className="text-lg font-bold text-white">
            Representative Sampled Frame Evidence Viewer
          </h3>
        </div>

        {/* View Mode Controller */}
        <div className="flex items-center p-1 rounded-xl bg-slate-900 border border-slate-800 text-xs font-semibold">
          <button
            onClick={() => setViewMode('frame')}
            className={`px-3 py-1.5 rounded-lg transition ${
              viewMode === 'frame'
                ? 'bg-cyan-500 text-slate-950 font-bold shadow'
                : 'text-slate-400 hover:text-slate-200'
            }`}
          >
            Sampled Frame
          </button>
          {currentFrame.ela_base64 && (
            <button
              onClick={() => setViewMode('ela')}
              className={`px-3 py-1.5 rounded-lg transition ${
                viewMode === 'ela'
                  ? 'bg-cyan-500 text-slate-950 font-bold shadow'
                  : 'text-slate-400 hover:text-slate-200'
              }`}
            >
              Frame ELA Heatmap
            </button>
          )}
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 items-center">
        {/* Frame Canvas Viewer */}
        <div className="lg:col-span-2 relative w-full h-[320px] md:h-[400px] rounded-xl overflow-hidden bg-slate-950 border border-slate-800 flex items-center justify-center p-2 group">
          <img
            src={viewMode === 'ela' && currentFrame.ela_base64 ? currentFrame.ela_base64 : currentFrame.frame_base64}
            alt={`Sampled frame ${currentFrame.frame_index}`}
            className="w-full h-full object-contain p-2"
          />

          {/* Timestamp Badge */}
          <div className="absolute top-4 left-4 px-3 py-1 rounded-lg bg-slate-950/80 backdrop-blur-md border border-slate-800 text-xs font-mono text-cyan-300 flex items-center space-x-1.5 shadow">
            <Clock className="w-3.5 h-3.5" />
            <span>{currentFrame.timestamp_sec}s (Frame #{currentFrame.frame_index})</span>
          </div>
        </div>

        {/* Frame Selector & Observation Card */}
        <div className="space-y-4">
          <h4 className="text-sm font-bold text-white uppercase tracking-wider text-slate-400">
            Sampled Timeline Keyframes
          </h4>

          {/* Keyframe Thumbnails Selector */}
          <div className="grid grid-cols-5 gap-2">
            {sampledFrames.map((frame, idx) => (
              <button
                key={idx}
                onClick={() => setActiveFrameIndex(idx)}
                className={`relative rounded-lg overflow-hidden border-2 h-16 bg-slate-950 transition ${
                  activeFrameIndex === idx
                    ? 'border-cyan-400 ring-2 ring-cyan-500/30 scale-[1.05]'
                    : 'border-slate-800 opacity-60 hover:opacity-100'
                }`}
              >
                <img
                  src={frame.frame_base64}
                  alt={`Thumb ${idx}`}
                  className="w-full h-full object-cover"
                />
                <span className="absolute bottom-0 inset-x-0 bg-slate-950/80 text-[9px] font-mono text-center text-slate-300">
                  {frame.timestamp_sec}s
                </span>
              </button>
            ))}
          </div>

          {/* Forensic Observation Box */}
          <div className="p-4 rounded-xl bg-slate-900/90 border border-slate-800 space-y-2">
            <div className="flex items-center space-x-2 text-xs font-bold text-cyan-400">
              <Info className="w-4 h-4" />
              <span>Frame Observations</span>
            </div>
            <p className="text-xs text-slate-300 leading-relaxed font-medium">
              {currentFrame.observations}
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}

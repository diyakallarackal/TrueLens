import React, { useEffect, useState } from 'react';
import { Music, X, Sparkles, FileAudio, Clock, HardDrive, Disc } from 'lucide-react';
import { formatBytes } from '../utils/formatters';

export default function AudioPlayerPreview({ file, onAnalyze, onReset }) {
  const [audioUrl, setAudioUrl] = useState(null);
  const [duration, setDuration] = useState(null);

  useEffect(() => {
    if (!file) return;
    const url = URL.createObjectURL(file);
    setAudioUrl(url);

    const tempAudio = new Audio(url);
    tempAudio.onloadedmetadata = () => {
      if (tempAudio.duration && !isNaN(tempAudio.duration)) {
        setDuration(tempAudio.duration);
      }
    };

    return () => {
      URL.revokeObjectURL(url);
    };
  }, [file]);

  if (!file) return null;

  const ext = file.name.split('.').pop().toUpperCase() || 'AUDIO';

  return (
    <div className="w-full max-w-4xl mx-auto glass-panel rounded-2xl p-6 md:p-8 border border-slate-800 shadow-2xl">
      <div className="flex flex-col md:flex-row items-center gap-6">
        {/* Audio Icon & Wave Graphic */}
        <div className="relative w-full md:w-56 h-48 rounded-xl overflow-hidden bg-slate-950 border border-slate-800 flex flex-col items-center justify-center space-y-3 p-4 flex-shrink-0">
          <div className="p-3 rounded-2xl bg-cyan-500/10 text-cyan-400 border border-cyan-500/20 shadow-lg">
            <Music className="w-8 h-8 stroke-[2]" />
          </div>
          <span className="text-xs font-mono font-bold text-cyan-300 uppercase tracking-widest">
            {ext} TRACK
          </span>
        </div>

        {/* Audio File Specs & Player */}
        <div className="flex-1 w-full space-y-4">
          <div>
            <div className="flex items-center space-x-2 text-cyan-400 text-xs font-bold uppercase tracking-wider mb-1">
              <FileAudio className="w-4 h-4" />
              <span>Target Audio Signal Loaded</span>
            </div>
            <h2 className="text-xl md:text-2xl font-extrabold text-white truncate">
              {file.name}
            </h2>
          </div>

          {/* HTML5 Audio Player */}
          {audioUrl && (
            <div className="p-3 rounded-xl bg-slate-900 border border-slate-800">
              <audio controls src={audioUrl} className="w-full h-10 accent-cyan-400" />
            </div>
          )}

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
                {ext}
              </span>
            </div>

            <div className="p-3 rounded-lg bg-slate-900/80 border border-slate-800 col-span-2 sm:col-span-1">
              <span className="text-xs text-slate-400 block mb-0.5">Duration</span>
              <span className="text-sm font-semibold text-slate-200">
                {duration ? `${duration.toFixed(2)}s` : 'Analyzing...'}
              </span>
            </div>
          </div>

          <div className="flex items-center space-x-3 pt-3">
            <button
              onClick={onAnalyze}
              className="flex-1 flex items-center justify-center space-x-2.5 px-6 py-3.5 rounded-xl bg-gradient-to-r from-cyan-500 to-emerald-500 hover:from-cyan-400 hover:to-emerald-400 text-slate-950 font-extrabold text-base shadow-lg shadow-cyan-500/20 transition duration-150 transform active:scale-[0.99]"
            >
              <Sparkles className="w-5 h-5 fill-slate-950" />
              <span>Analyze Audio Signals</span>
            </button>

            <button
              onClick={onReset}
              className="px-4 py-3.5 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-300 hover:text-white font-semibold text-sm border border-slate-700 transition"
              title="Select different audio"
            >
              <X className="w-5 h-5" />
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}

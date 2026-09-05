import React from 'react';
import { FileImage, Music, Video } from 'lucide-react';

export default function MediaTabs({ activeTab, onTabChange, capabilities }) {
  const isVideoSupported = capabilities?.video_analysis !== false;

  return (
    <div className="flex items-center justify-center p-1.5 rounded-2xl bg-slate-900/90 border border-slate-800 max-w-lg mx-auto shadow-lg">
      <button
        onClick={() => onTabChange('image')}
        className={`flex-1 flex items-center justify-center space-x-2 py-2.5 px-3 sm:px-4 rounded-xl font-extrabold text-xs tracking-wider transition-all duration-200 ${
          activeTab === 'image'
            ? 'bg-gradient-to-r from-cyan-500 to-emerald-500 text-slate-950 shadow-md shadow-cyan-500/20 scale-[1.02]'
            : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/60'
        }`}
      >
        <FileImage className="w-4 h-4" />
        <span>IMAGE</span>
      </button>

      <button
        onClick={() => onTabChange('audio')}
        className={`flex-1 flex items-center justify-center space-x-2 py-2.5 px-3 sm:px-4 rounded-xl font-extrabold text-xs tracking-wider transition-all duration-200 ${
          activeTab === 'audio'
            ? 'bg-gradient-to-r from-cyan-500 to-emerald-500 text-slate-950 shadow-md shadow-cyan-500/20 scale-[1.02]'
            : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/60'
        }`}
      >
        <Music className="w-4 h-4" />
        <span>AUDIO</span>
      </button>

      <button
        onClick={() => isVideoSupported && onTabChange('video')}
        disabled={!isVideoSupported}
        className={`flex-1 flex items-center justify-center space-x-2 py-2.5 px-3 sm:px-4 rounded-xl font-extrabold text-xs tracking-wider transition-all duration-200 ${
          activeTab === 'video'
            ? 'bg-gradient-to-r from-cyan-500 to-emerald-500 text-slate-950 shadow-md shadow-cyan-500/20 scale-[1.02]'
            : isVideoSupported
            ? 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/60'
            : 'text-slate-600 cursor-not-allowed opacity-50'
        }`}
      >
        <Video className="w-4 h-4" />
        <span>VIDEO</span>
      </button>
    </div>
  );
}

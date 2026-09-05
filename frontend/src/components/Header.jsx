import React, { useEffect, useState } from 'react';
import { ShieldCheck, History, Activity, Cpu, AlertCircle } from 'lucide-react';
import { checkHealth } from '../services/api';

export default function Header({ onOpenHistory }) {
  const [health, setHealth] = useState({ status: 'checking', detectors: {} });

  useEffect(() => {
    const fetchHealth = async () => {
      const data = await checkHealth();
      setHealth(data);
    };
    fetchHealth();
    const interval = setInterval(fetchHealth, 30000);
    return () => clearInterval(interval);
  }, []);

  const isHealthy = health.status === 'healthy';

  return (
    <header className="sticky top-0 z-40 w-full glass-panel border-b border-slate-800/80 bg-slate-950/80 backdrop-blur-md px-4 lg:px-8 py-3.5">
      <div className="max-w-7xl mx-auto flex items-center justify-between">
        {/* Brand logo & tagline */}
        <div className="flex items-center space-x-3">
          <div className="p-2 rounded-xl bg-gradient-to-tr from-cyan-600 to-emerald-500 text-slate-950 shadow-lg shadow-cyan-500/20">
            <ShieldCheck className="w-6 h-6 stroke-[2.5]" />
          </div>
          <div>
            <div className="flex items-center space-x-2">
              <span className="text-xl font-extrabold tracking-wider bg-gradient-to-r from-white via-slate-200 to-slate-400 bg-clip-text text-transparent">
                TRUE<span className="text-cyan-400">LENS</span>
              </span>
              <span className="px-2 py-0.5 text-[10px] font-bold tracking-widest uppercase rounded bg-cyan-500/10 text-cyan-400 border border-cyan-500/20">
                FORENSICS
              </span>
            </div>
            <p className="text-xs text-slate-400 font-medium">
              Media Integrity & Forensic Verification Platform
            </p>
          </div>
        </div>

        {/* Status indicators & Actions */}
        <div className="flex items-center space-x-3 sm:space-x-4">
          {/* Engine Capability Badge */}
          <div className="hidden md:flex items-center space-x-2 px-3 py-1.5 rounded-lg bg-slate-900/80 border border-slate-800 text-xs text-slate-300">
            <Cpu className="w-3.5 h-3.5 text-cyan-400" />
            <span>Engine: <strong className="text-white">Multi-Signal PyEngine</strong></span>
          </div>

          {/* Backend Connection Health Dot */}
          <div
            className={`flex items-center space-x-2 px-3 py-1.5 rounded-lg text-xs font-semibold border ${
              isHealthy
                ? 'bg-emerald-500/10 text-emerald-400 border-emerald-500/30'
                : 'bg-rose-500/10 text-rose-400 border-rose-500/30'
            }`}
            title={isHealthy ? 'FastAPI Backend Connected & Healthy' : 'FastAPI Backend Disconnected'}
          >
            <span
              className={`w-2 h-2 rounded-full ${
                isHealthy ? 'bg-emerald-400 animate-pulse' : 'bg-rose-500'
              }`}
            ></span>
            <span className="hidden sm:inline">
              {isHealthy ? 'API Active' : 'API Offline'}
            </span>
          </div>

          {/* History Drawer Trigger Button */}
          <button
            onClick={onOpenHistory}
            className="flex items-center space-x-2 px-3.5 py-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-200 hover:text-white text-xs font-semibold border border-slate-700 transition duration-150 shadow-sm"
          >
            <History className="w-4 h-4 text-cyan-400" />
            <span>Analysis History</span>
          </button>
        </div>
      </div>
    </header>
  );
}

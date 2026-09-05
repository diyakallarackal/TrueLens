import React, { useEffect, useState } from 'react';
import { X, History, Trash2, RefreshCw, FileText, FileImage, Music, Video, Award } from 'lucide-react';
import { getHistory, getHistoryDetail, deleteHistoryItem } from '../services/api';
import { formatDate, getVerdictColor } from '../utils/formatters';

export default function HistoryDrawer({ isOpen, onClose, onSelectReport }) {
  const [historyList, setHistoryList] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const fetchHistory = async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await getHistory(30, 0);
      setHistoryList(data);
    } catch (err) {
      setError('Failed to load analysis history.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (isOpen) {
      fetchHistory();
    }
  }, [isOpen]);

  const handleSelect = async (analysisId) => {
    try {
      const detail = await getHistoryDetail(analysisId);
      onSelectReport(detail);
      onClose();
    } catch (err) {
      alert('Could not fetch report detail.');
    }
  };

  const handleDelete = async (e, analysisId) => {
    e.stopPropagation();
    if (!confirm('Are you sure you want to delete this historical record?')) return;
    try {
      await deleteHistoryItem(analysisId);
      setHistoryList((prev) => prev.filter((item) => item.id !== analysisId));
    } catch (err) {
      alert('Delete failed.');
    }
  };

  const getMediaIcon = (mediaType) => {
    switch (mediaType) {
      case 'video':
        return <Video className="w-3 h-3 text-cyan-400" />;
      case 'audio':
        return <Music className="w-3 h-3 text-amber-400" />;
      default:
        return <FileImage className="w-3 h-3 text-emerald-400" />;
    }
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 flex justify-end bg-slate-950/70 backdrop-blur-sm transition-opacity">
      <div className="w-full max-w-md h-full glass-panel border-l border-slate-800 p-6 flex flex-col justify-between shadow-2xl bg-slate-950/95 overflow-y-auto">
        <div>
          {/* Drawer Header */}
          <div className="flex items-center justify-between pb-4 border-b border-slate-800">
            <div className="flex items-center space-x-2">
              <History className="w-5 h-5 text-cyan-400" />
              <h3 className="text-lg font-extrabold text-white">Analysis History</h3>
            </div>
            <div className="flex items-center space-x-2">
              <button
                onClick={fetchHistory}
                className="p-1.5 rounded-lg bg-slate-900 text-slate-400 hover:text-white transition"
                title="Refresh history list"
              >
                <RefreshCw className={`w-4 h-4 ${loading ? 'animate-spin' : ''}`} />
              </button>
              <button
                onClick={onClose}
                className="p-1.5 rounded-lg bg-slate-900 text-slate-400 hover:text-white transition"
              >
                <X className="w-5 h-5" />
              </button>
            </div>
          </div>

          {/* List Content */}
          <div className="py-4 space-y-3">
            {loading && historyList.length === 0 && (
              <p className="text-xs text-slate-400 text-center py-8">Loading persistent database records...</p>
            )}

            {error && (
              <p className="text-xs text-rose-400 text-center py-4">{error}</p>
            )}

            {!loading && historyList.length === 0 && (
              <div className="text-center py-12 space-y-2">
                <FileText className="w-8 h-8 text-slate-600 mx-auto" />
                <p className="text-sm font-semibold text-slate-400">No Past Evaluations</p>
                <p className="text-xs text-slate-500">
                  Analyzed images, audio, and video will automatically persist to SQLite database history.
                </p>
              </div>
            )}

            {historyList.map((item) => {
              const style = getVerdictColor(item.verdict, item.risk_score);
              return (
                <div
                  key={item.id}
                  onClick={() => handleSelect(item.id)}
                  className="p-3.5 rounded-xl bg-slate-900/80 hover:bg-slate-900 border border-slate-800 hover:border-cyan-500/40 cursor-pointer transition flex items-center justify-between group"
                >
                  <div className="space-y-1 flex-1 pr-3 truncate">
                    <div className="flex flex-wrap items-center gap-1.5">
                      <span className={`px-2 py-0.5 rounded text-[10px] font-bold border ${style.badge}`}>
                        {item.verdict}
                      </span>
                      <span className="text-[11px] font-bold text-slate-300">
                        {item.risk_score}/100
                      </span>
                      <span className="px-1.5 py-0.5 rounded text-[9px] font-bold uppercase bg-slate-800 text-slate-400 border border-slate-700 flex items-center space-x-1">
                        {getMediaIcon(item.media_type)}
                        <span>{item.media_type || 'image'}</span>
                      </span>
                      <span className="px-1.5 py-0.5 rounded text-[9px] font-semibold bg-cyan-500/10 text-cyan-400 border border-cyan-500/20 flex items-center space-x-0.5">
                        <Award className="w-2.5 h-2.5" />
                        <span>PROVENANCE</span>
                      </span>
                    </div>
                    <h4 className="text-xs font-semibold text-white truncate">{item.filename}</h4>
                    <span className="text-[10px] text-slate-400 block">{formatDate(item.timestamp)}</span>
                  </div>

                  <div className="flex items-center space-x-1 opacity-80 group-hover:opacity-100">
                    <button
                      onClick={(e) => handleDelete(e, item.id)}
                      className="p-1.5 rounded-lg hover:bg-rose-500/20 text-slate-500 hover:text-rose-400 transition"
                      title="Delete record"
                    >
                      <Trash2 className="w-4 h-4" />
                    </button>
                  </div>
                </div>
              );
            })}
          </div>
        </div>

        <div className="pt-4 border-t border-slate-800 text-center text-[11px] text-slate-500">
          TrueLens Persistent SQLite History Storage
        </div>
      </div>
    </div>
  );
}

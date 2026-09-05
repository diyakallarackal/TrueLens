import React, { useState, useRef } from 'react';
import { Video, UploadCloud, AlertCircle } from 'lucide-react';

const ALLOWED_VIDEO_TYPES = ['video/mp4', 'video/quicktime', 'video/webm', 'video/x-msvideo', 'video/x-matroska', 'video/avi', 'video/mkv'];
const MAX_VIDEO_SIZE_MB = 100;

export default function VideoDropzone({ onFileSelected }) {
  const [isDragActive, setIsDragActive] = useState(false);
  const [errorMessage, setErrorMessage] = useState(null);
  const fileInputRef = useRef(null);

  const validateAndSelectFile = (file) => {
    setErrorMessage(null);
    if (!file) return;

    const isVideo = file.type.startsWith('video/') || ALLOWED_VIDEO_TYPES.includes(file.type.toLowerCase()) || /\.(mp4|mov|webm|avi|mkv)$/i.test(file.name);
    if (!isVideo) {
      setErrorMessage('Unsupported video format. Please upload an MP4, MOV, WebM, AVI, or MKV video file.');
      return;
    }

    if (file.size > MAX_VIDEO_SIZE_MB * 1024 * 1024) {
      setErrorMessage(`Video file size exceeds maximum threshold of ${MAX_VIDEO_SIZE_MB}MB.`);
      return;
    }

    onFileSelected(file);
  };

  const handleDragOver = (e) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragActive(true);
  };

  const handleDragLeave = (e) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragActive(false);
  };

  const handleDrop = (e) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragActive(false);

    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      validateAndSelectFile(e.dataTransfer.files[0]);
    }
  };

  const handleFileChange = (e) => {
    if (e.target.files && e.target.files[0]) {
      validateAndSelectFile(e.target.files[0]);
    }
  };

  return (
    <div className="w-full max-w-4xl mx-auto">
      <div
        onDragOver={handleDragOver}
        onDragLeave={handleDragLeave}
        onDrop={handleDrop}
        onClick={() => fileInputRef.current?.click()}
        className={`relative cursor-pointer rounded-2xl border-2 border-dashed p-8 md:p-12 text-center transition-all duration-200 ${
          isDragActive
            ? 'border-cyan-400 bg-cyan-500/10 scale-[1.01]'
            : 'border-slate-700/80 hover:border-cyan-500/50 bg-slate-900/60 hover:bg-slate-900/90'
        }`}
      >
        <input
          type="file"
          ref={fileInputRef}
          onChange={handleFileChange}
          accept="video/mp4,video/quicktime,video/webm,video/avi,video/mkv,.mp4,.mov,.webm,.avi,.mkv"
          className="hidden"
        />

        <div className="flex flex-col items-center justify-center space-y-4">
          <div className="p-4 rounded-2xl bg-cyan-500/10 text-cyan-400 border border-cyan-500/20 shadow-lg shadow-cyan-500/5">
            <Video className="w-10 h-10 stroke-[1.8]" />
          </div>

          <div>
            <h3 className="text-lg md:text-xl font-bold text-slate-100 mb-1">
              Drag & Drop Video for Frame & Motion Forensics
            </h3>
            <p className="text-sm text-slate-400">
              or <span className="text-cyan-400 font-semibold underline underline-offset-4">browse video picker</span>
            </p>
          </div>

          <div className="flex flex-wrap items-center justify-center gap-2 pt-2 text-xs text-slate-400 font-medium">
            <span className="px-2.5 py-1 rounded-md bg-slate-800 border border-slate-700">MP4</span>
            <span className="px-2.5 py-1 rounded-md bg-slate-800 border border-slate-700">MOV</span>
            <span className="px-2.5 py-1 rounded-md bg-slate-800 border border-slate-700">WebM</span>
            <span className="px-2.5 py-1 rounded-md bg-slate-800 border border-slate-700">AVI</span>
            <span className="px-2.5 py-1 rounded-md bg-slate-800 border border-slate-700">MKV</span>
            <span className="text-slate-400">· Max 100MB</span>
          </div>
        </div>
      </div>

      {errorMessage && (
        <div className="mt-4 p-4 rounded-xl bg-rose-500/10 border border-rose-500/30 flex items-center space-x-3 text-rose-400 text-sm">
          <AlertCircle className="w-5 h-5 flex-shrink-0" />
          <span>{errorMessage}</span>
        </div>
      )}
    </div>
  );
}

import React, { useState, useRef } from 'react';
import { Music, UploadCloud, AlertCircle } from 'lucide-react';

const ALLOWED_AUDIO_TYPES = ['audio/wav', 'audio/x-wav', 'audio/mp3', 'audio/mpeg', 'audio/m4a', 'audio/mp4', 'audio/flac', 'audio/x-flac', 'audio/ogg'];
const MAX_AUDIO_SIZE_MB = 50;

export default function AudioDropzone({ onFileSelected }) {
  const [isDragActive, setIsDragActive] = useState(false);
  const [errorMessage, setErrorMessage] = useState(null);
  const fileInputRef = useRef(null);

  const validateAndSelectFile = (file) => {
    setErrorMessage(null);
    if (!file) return;

    const isAudio = file.type.startsWith('audio/') || ALLOWED_AUDIO_TYPES.includes(file.type.toLowerCase()) || /\.(wav|mp3|m4a|flac|ogg)$/i.test(file.name);
    if (!isAudio) {
      setErrorMessage('Unsupported audio format. Please upload a WAV, MP3, M4A, or FLAC audio file.');
      return;
    }

    if (file.size > MAX_AUDIO_SIZE_MB * 1024 * 1024) {
      setErrorMessage(`Audio file size exceeds maximum threshold of ${MAX_AUDIO_SIZE_MB}MB.`);
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
          accept="audio/wav,audio/mp3,audio/mpeg,audio/m4a,audio/flac,audio/ogg,.wav,.mp3,.m4a,.flac,.ogg"
          className="hidden"
        />

        <div className="flex flex-col items-center justify-center space-y-4">
          <div className="p-4 rounded-2xl bg-cyan-500/10 text-cyan-400 border border-cyan-500/20 shadow-lg shadow-cyan-500/5">
            <Music className="w-10 h-10 stroke-[1.8]" />
          </div>

          <div>
            <h3 className="text-lg md:text-xl font-bold text-slate-100 mb-1">
              Drag & Drop Audio for Voice / Acoustic Forensics
            </h3>
            <p className="text-sm text-slate-400">
              or <span className="text-cyan-400 font-semibold underline underline-offset-4">browse audio picker</span>
            </p>
          </div>

          <div className="flex flex-wrap items-center justify-center gap-2 pt-2 text-xs text-slate-400 font-medium">
            <span className="px-2.5 py-1 rounded-md bg-slate-800 border border-slate-700">WAV</span>
            <span className="px-2.5 py-1 rounded-md bg-slate-800 border border-slate-700">MP3</span>
            <span className="px-2.5 py-1 rounded-md bg-slate-800 border border-slate-700">M4A</span>
            <span className="px-2.5 py-1 rounded-md bg-slate-800 border border-slate-700">FLAC</span>
            <span className="text-slate-400">· Max 50MB</span>
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

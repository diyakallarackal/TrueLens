import React, { useEffect, useState } from 'react';
import Header from './components/Header';
import MediaTabs from './components/MediaTabs';
import Dropzone from './components/Dropzone';
import AudioDropzone from './components/AudioDropzone';
import VideoDropzone from './components/VideoDropzone';
import ImagePreview from './components/ImagePreview';
import AudioPlayerPreview from './components/AudioPlayerPreview';
import VideoPlayerPreview from './components/VideoPlayerPreview';
import ProcessingState from './components/ProcessingState';
import VerdictBanner from './components/VerdictBanner';
import ElaViewer from './components/ElaViewer';
import SpectrogramViewer from './components/SpectrogramViewer';
import FrameViewer from './components/FrameViewer';
import SignalCard from './components/SignalCard';
import MetadataTable from './components/MetadataTable';
import ProvenanceCard from './components/ProvenanceCard';
import WhatWeFound from './components/WhatWeFound';
import Recommendations from './components/Recommendations';
import HistoryDrawer from './components/HistoryDrawer';
import AiExplanation from './components/AiExplanation';
import { analyzeImage, analyzeAudio, analyzeVideo, getCapabilities } from './services/api';
import { AlertTriangle, RefreshCw, Sparkles, ShieldCheck } from 'lucide-react';

export default function App() {
  const [mediaType, setMediaType] = useState('image'); // 'image' | 'audio' | 'video'
  const [selectedFile, setSelectedFile] = useState(null);
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [analysisResult, setAnalysisResult] = useState(null);
  const [apiError, setApiError] = useState(null);
  const [isHistoryOpen, setIsHistoryOpen] = useState(false);
  const [capabilities, setCapabilities] = useState({
    image_analysis: true,
    audio_analysis: true,
    video_analysis: true,
    content_credentials: true,
    metadata_extraction: true,
    external_reverse_search: false,
  });

  useEffect(() => {
    const fetchCap = async () => {
      const data = await getCapabilities();
      setCapabilities(data);
    };
    fetchCap();
  }, []);

  const handleTabChange = (tab) => {
    if (tab === mediaType) return;
    setMediaType(tab);
    setSelectedFile(null);
    setAnalysisResult(null);
    setApiError(null);
  };

  const handleFileSelected = (file) => {
    setSelectedFile(file);
    setAnalysisResult(null);
    setApiError(null);
  };

  const handleReset = () => {
    setSelectedFile(null);
    setAnalysisResult(null);
    setApiError(null);
  };

  const handleStartAnalysis = async () => {
    if (!selectedFile) return;
    setIsAnalyzing(true);
    setApiError(null);

    try {
      let data;
      if (mediaType === 'video') {
        data = await analyzeVideo(selectedFile);
      } else if (mediaType === 'audio') {
        data = await analyzeAudio(selectedFile);
      } else {
        data = await analyzeImage(selectedFile);
      }
      setAnalysisResult(data);
    } catch (err) {
      console.error('Analysis error:', err);
      const msg = err.response?.data?.detail || err.message || 'Failed to analyze media file.';
      setApiError(msg);
    } finally {
      setIsAnalyzing(false);
    }
  };

  const handleSelectHistoryReport = (report) => {
    setAnalysisResult(report);
    setSelectedFile(null);
    if (report.media_type) {
      setMediaType(report.media_type);
    }
    setApiError(null);
    window.scrollTo({ top: 0, behavior: 'smooth' });
  };

  const isAudioReport = analysisResult?.media_type === 'audio';
  const isVideoReport = analysisResult?.media_type === 'video';

  return (
    <div className="min-h-screen bg-[#0b0f19] text-slate-100 flex flex-col selection:bg-cyan-500 selection:text-slate-950 font-sans">
      {/* Navbar Header */}
      <Header onOpenHistory={() => setIsHistoryOpen(true)} />

      {/* Main Content Area */}
      <main className="flex-1 max-w-7xl w-full mx-auto px-4 lg:px-8 py-8 space-y-8">
        {/* Media Selector Tabs (IMAGE / AUDIO / VIDEO) */}
        {!analysisResult && !isAnalyzing && (
          <MediaTabs
            activeTab={mediaType}
            onTabChange={handleTabChange}
            capabilities={capabilities}
          />
        )}

        {/* State 1: No file selected & no active result -> Dropzone Hero */}
        {!selectedFile && !analysisResult && !isAnalyzing && (
          <section className="py-6 space-y-8">
            <div className="text-center max-w-3xl mx-auto space-y-4">
              <div className="inline-flex items-center space-x-2 px-3.5 py-1.5 rounded-full bg-cyan-500/10 text-cyan-400 border border-cyan-500/20 text-xs font-extrabold uppercase tracking-widest">
                <ShieldCheck className="w-4 h-4" />
                <span>Verify before you trust</span>
              </div>
              <h1 className="text-3xl sm:text-5xl font-black text-white tracking-tight leading-tight">
                {mediaType === 'video'
                  ? 'Inspect Video Files for Deepfakes & Generative Manipulation'
                  : mediaType === 'audio'
                  ? 'Inspect Audio Files for Voice Cloning & Acoustic Synthesis'
                  : 'Inspect Images for AI Generation & Digital Alterations'}
              </h1>
              <p className="text-sm sm:text-base text-slate-400 max-w-2xl mx-auto leading-relaxed">
                {mediaType === 'video'
                  ? 'TrueLens evaluates sampled frame ELA compression, optical flow motion continuity, 2D FFT spectral grid anomalies, and extracted audio track forensics.'
                  : mediaType === 'audio'
                  ? 'TrueLens evaluates STFT spectral flatness, centroid variation, zero-crossing rates, RMS energy, and C2PA Content Credentials to detect potential voice synthesis.'
                  : 'TrueLens evaluates metadata integrity, Error Level Analysis (ELA) compression maps, 2D FFT spectral grid anomalies, and sensor noise variance to provide transparent risk assessments.'}
              </p>
            </div>

            {mediaType === 'video' ? (
              <VideoDropzone onFileSelected={handleFileSelected} />
            ) : mediaType === 'audio' ? (
              <AudioDropzone onFileSelected={handleFileSelected} />
            ) : (
              <Dropzone onFileSelected={handleFileSelected} />
            )}
          </section>
        )}

        {/* State 2: Target File Selected -> Ready Preview */}
        {selectedFile && !analysisResult && !isAnalyzing && (
          mediaType === 'video' ? (
            <VideoPlayerPreview
              file={selectedFile}
              onAnalyze={handleStartAnalysis}
              onReset={handleReset}
            />
          ) : mediaType === 'audio' ? (
            <AudioPlayerPreview
              file={selectedFile}
              onAnalyze={handleStartAnalysis}
              onReset={handleReset}
            />
          ) : (
            <ImagePreview
              file={selectedFile}
              onAnalyze={handleStartAnalysis}
              onReset={handleReset}
            />
          )
        )}

        {/* State 3: Active Forensic Pipeline Loading */}
        {isAnalyzing && (
          <ProcessingState file={selectedFile} />
        )}

        {/* Error Alert View */}
        {apiError && (
          <div className="w-full max-w-4xl mx-auto p-5 rounded-2xl bg-rose-500/10 border border-rose-500/30 text-rose-300 space-y-3">
            <div className="flex items-center space-x-3">
              <AlertTriangle className="w-6 h-6 text-rose-400 flex-shrink-0" />
              <h3 className="text-base font-bold text-white">Forensic Engine Error</h3>
            </div>
            <p className="text-xs text-rose-300 font-mono bg-slate-950/60 p-3 rounded-xl border border-rose-500/20">
              {apiError}
            </p>
            <button
              onClick={handleReset}
              className="px-4 py-2 rounded-xl bg-slate-900 hover:bg-slate-800 text-xs font-semibold text-white border border-slate-700 transition"
            >
              Try Another File
            </button>
          </div>
        )}

        {/* State 4: Complete Analysis Results Dashboard */}
        {analysisResult && !isAnalyzing && (
          <section className="space-y-8 animate-fadeIn">
            {/* Top Action Bar */}
            <div className="flex items-center justify-between">
              <h2 className="text-xl font-bold text-white flex items-center space-x-2">
                <Sparkles className="w-5 h-5 text-cyan-400" />
                <span>
                  {isVideoReport
                    ? 'Video Forensic Analysis Dashboard'
                    : isAudioReport
                    ? 'Audio Forensic Analysis Dashboard'
                    : 'Image Forensic Analysis Dashboard'}
                </span>
              </h2>

              <button
                onClick={handleReset}
                className="flex items-center space-x-2 px-4 py-2 rounded-xl bg-cyan-500 hover:bg-cyan-400 text-slate-950 text-xs font-extrabold shadow-lg shadow-cyan-500/20 transition"
              >
                <RefreshCw className="w-3.5 h-3.5" />
                <span>Analyze New File</span>
              </button>
            </div>

            {/* Verdict & Score Summary Header */}
            <VerdictBanner result={analysisResult} />

            {/* GenAI Evidence Explanation Card */}
            <AiExplanation
              explanation={analysisResult.explanation}
              verdict={analysisResult.verdict}
              riskScore={analysisResult.risk_score}
            />

            {/* Media Specific Heatmap / Frame Evidence Viewers */}
            {isVideoReport ? (
              <FrameViewer sampledFrames={analysisResult.sampled_frames} />
            ) : isAudioReport ? (
              <SpectrogramViewer spectrogramBase64={analysisResult.spectrogram_base64} />
            ) : (
              <ElaViewer
                originalImageFile={selectedFile}
                elaBase64={analysisResult.ela_heatmap_base64}
              />
            )}

            {/* Forensic Signals Breakdown Grid */}
            <div className="space-y-4">
              <h3 className="text-lg font-bold text-white">Forensic Signal Indicators</h3>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {analysisResult.signals?.map((sig) => (
                  <SignalCard key={sig.id} signal={sig} />
                ))}
              </div>
            </div>

            {/* WHAT WE FOUND Summary Box */}
            {analysisResult.provenance?.what_we_found && (
              <WhatWeFound observations={analysisResult.provenance.what_we_found} />
            )}

            {/* C2PA Provenance & Source Traceability Suite */}
            {analysisResult.provenance && (
              <ProvenanceCard provenance={analysisResult.provenance} />
            )}

            {/* Metadata Inspector (Image) */}
            {!isAudioReport && !isVideoReport && analysisResult.metadata && (
              <MetadataTable metadata={analysisResult.metadata} />
            )}

            {/* Action Guidance & Disclaimer */}
            <Recommendations
              recommendation={analysisResult.recommendation}
              disclaimer={analysisResult.disclaimer}
              riskScore={analysisResult.risk_score}
            />
          </section>
        )}
      </main>

      {/* Persistent History Modal Drawer */}
      <HistoryDrawer
        isOpen={isHistoryOpen}
        onClose={() => setIsHistoryOpen(false)}
        onSelectReport={handleSelectHistoryReport}
      />

      {/* Footer */}
      <footer className="w-full border-t border-slate-800/80 py-6 text-center text-xs text-slate-500">
        <p>TrueLens Media Verification Platform · Multi-Signal Image, Audio & Video Forensics with Source Traceability</p>
      </footer>
    </div>
  );
}

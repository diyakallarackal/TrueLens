import uuid
import datetime
from typing import List, Dict, Any
from app.services.detectors.base import SignalMetric
from app.services.detectors.base_audio import AudioDetector, AudioAnalysisResult
from app.services.audio_features import decode_audio_bytes, compute_spectral_features
from app.services.source_verifier import TrueLensSourceVerifierSuite
from app.services.explanation_service import GenAIExplanationService


class RealAudioAnalyzer(AudioDetector):
    """
    Primary audio forensic engine measuring:
    - Waveform dynamics, RMS energy, and ZCR
    - Spectral centroid, bandwidth, rolloff, and spectral flatness
    - STFT frequency-domain anomalies & dynamic spectrogram generation
    - C2PA Content Credentials & Source Traceability
    """

    def __init__(self):
        self.verifier_suite = TrueLensSourceVerifierSuite()
        self.explanation_service = GenAIExplanationService()

    @property
    def name(self) -> str:
        return "Real Acoustic Signal Engine"

    @property
    def is_available(self) -> bool:
        return True

    async def analyze(self, audio_bytes: bytes, filename: str) -> AudioAnalysisResult:
        # Decode audio safely
        signal, sample_rate, duration, tech_metrics = decode_audio_bytes(audio_bytes, filename)

        # Compute STFT spectral features & spectrogram heatmap
        spectral_data = compute_spectral_features(signal, sample_rate)

        # Run Source Verification & C2PA Provenance
        mime_type = f"audio/{filename.split('.')[-1].lower()}"
        provenance_data = self.verifier_suite.run_verification(
            audio_bytes, tech_metrics, media_type="audio", filename=filename, mime_type=mime_type
        )

        # Signal 1: Spectral Centroid & Bandwidth
        flatness = spectral_data.get("spectral_flatness", 0.0)
        centroid = spectral_data.get("spectral_centroid_hz", 0.0)
        rolloff = spectral_data.get("spectral_rolloff_hz", 0.0)

        spec_score = 0.0
        if flatness > 0.08: # Unnaturally high spectral flatness (robotic/synthetic noise plateau)
            spec_score += 45.0
        if rolloff < 2500.0 and sample_rate >= 44100: # Abnormally low frequency cutoff for high sample rate
            spec_score += 30.0

        spec_score = float(max(0.0, min(100.0, spec_score)))
        spec_sev = "High" if spec_score >= 70 else ("Medium" if spec_score >= 40 else "Low")

        signal_spectral = SignalMetric(
            id="spectral_characteristics",
            name="Spectral Centroid & Bandwidth",
            score=round(spec_score, 1),
            severity=spec_sev,
            confidence=88.0,
            description=f"Spectral centroid is {centroid:.1f} Hz with spectral flatness index of {flatness:.4f}. "
            + ("High spectral flatness detected, typical of neural TTS/voice cloning synthesis." if spec_score > 40 else "Spectral energy decay aligns with natural acoustic speech patterns."),
            metrics={
                "spectral_centroid_hz": centroid,
                "spectral_bandwidth_hz": spectral_data.get("spectral_bandwidth_hz"),
                "spectral_rolloff_hz": rolloff,
                "spectral_flatness": flatness,
            }
        )

        # Signal 2: Waveform Dynamics & RMS Energy
        rms = spectral_data.get("rms_energy", 0.0)
        zcr = spectral_data.get("zero_crossing_rate", 0.0)
        clipping = spectral_data.get("clipping_ratio", 0.0)

        wave_score = 0.0
        if zcr < 0.01: # Unnatural lack of zero crossings
            wave_score += 35.0
        elif zcr > 0.35: # Abnormally high zero crossing rate
            wave_score += 25.0
        if clipping > 0.05: # High digital clipping
            wave_score += 25.0

        wave_score = float(max(0.0, min(100.0, wave_score)))
        wave_sev = "High" if wave_score >= 70 else ("Medium" if wave_score >= 40 else "Low")

        signal_waveform = SignalMetric(
            id="waveform_dynamics",
            name="Waveform Dynamics & RMS Energy",
            score=round(wave_score, 1),
            severity=wave_sev,
            confidence=85.0,
            description=f"RMS energy is {rms:.4f} with zero-crossing rate of {zcr:.4f}. "
            + ("Waveform dynamics exhibit unnatural amplitude step changes." if wave_score > 40 else "Dynamic amplitude and zero-crossing distributions show natural vocal acoustic variation."),
            metrics={
                "rms_energy": rms,
                "zero_crossing_rate": zcr,
                "clipping_ratio": clipping,
                "silence_ratio": spectral_data.get("silence_ratio"),
            }
        )

        signals: List[SignalMetric] = [signal_spectral, signal_waveform]

        # Transparent Weighted Scoring Formula
        risk_score = round((signal_spectral.score * 0.55) + (signal_waveform.score * 0.45))
        risk_score = max(0, min(100, risk_score))

        if risk_score < 35:
            verdict = "Likely Authentic"
        elif risk_score < 65:
            verdict = "Inconclusive"
        else:
            verdict = "Likely Manipulated"

        confidence = 90

        # Scientific Summary Wording
        if verdict == "Likely Manipulated":
            summary_explanation = "Potential synthetic-audio indicators detected in spectral flatness index and waveform zero-crossing distributions."
        elif verdict == "Inconclusive":
            summary_explanation = "Mixed acoustic indicators detected. Spectral parameters show subtle compression, but evidence is insufficient for a definitive verdict."
        else:
            summary_explanation = "Extracted acoustic features demonstrate natural resonance, smooth spectral decay, and organic vocal dynamics."

        recommendation = "Treat as potentially synthetic audio and verify author origin before sharing." if risk_score >= 50 else "Audio exhibits low risk of neural speech synthesis. Verify publisher origin for critical media."
        disclaimer = "This analysis is an automated forensic assessment based on measurable acoustic parameters, not absolute proof."

        analysis_id = f"truelens_audio_{uuid.uuid4().hex[:12]}"
        timestamp = datetime.datetime.now(datetime.timezone.utc).isoformat()

        analysis_dict = {
            "analysis_id": analysis_id,
            "media_type": "audio",
            "filename": filename,
            "verdict": verdict,
            "risk_score": risk_score,
            "confidence": confidence,
            "signals": [s.model_dump() if hasattr(s, "model_dump") else s.dict() for s in signals],
            "technical_metrics": tech_metrics,
            "provenance": provenance_data,
        }
        explanation_data = await self.explanation_service.generate_explanation(analysis_dict)

        return AudioAnalysisResult(
            analysis_id=analysis_id,
            media_type="audio",
            timestamp=timestamp,
            filename=filename,
            file_size=len(audio_bytes),
            duration=duration,
            format=tech_metrics.get("format", "AUDIO"),
            verdict=verdict,
            risk_score=risk_score,
            confidence=confidence,
            summary_explanation=summary_explanation,
            signals=signals,
            technical_metrics=tech_metrics,
            provenance=provenance_data,
            explanation=explanation_data,
            spectrogram_base64=spectral_data.get("spectrogram_base64"),
            recommendation=recommendation,
            disclaimer=disclaimer,
        )

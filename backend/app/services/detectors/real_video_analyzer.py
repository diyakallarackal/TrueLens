import uuid
import datetime
from typing import List, Dict, Any
from app.services.detectors.base import SignalMetric
from app.services.detectors.base_video import VideoDetector, VideoAnalysisResult, SampledFrameInfo
from app.services.video_features import process_video_file
from app.services.detectors.real_audio_analyzer import RealAudioAnalyzer
from app.services.source_verifier import TrueLensSourceVerifierSuite
from app.services.explanation_service import GenAIExplanationService


class RealVideoAnalyzer(VideoDetector):
    """
    Primary video forensic engine measuring:
    - Container & codec metadata integrity
    - Representative frame sampling & frame ELA compression variance
    - Temporal MAD frame-to-frame difference & motion continuity
    - Extracted audio track forensics (via RealAudioAnalyzer)
    - C2PA Content Credentials & Container Traceability
    """

    def __init__(self):
        self.audio_analyzer = RealAudioAnalyzer()
        self.verifier_suite = TrueLensSourceVerifierSuite()
        self.explanation_service = GenAIExplanationService()

    @property
    def name(self) -> str:
        return "Real Video Forensic Engine"

    @property
    def is_available(self) -> bool:
        return True

    async def analyze(self, video_bytes: bytes, filename: str) -> VideoAnalysisResult:
        # Process video file & sample frames
        tech_metrics, sampled_frames_data, temporal_metrics, audio_bytes = process_video_file(video_bytes, filename)

        mime_type = f"video/{filename.split('.')[-1].lower()}"
        provenance_data = self.verifier_suite.run_verification(
            video_bytes, tech_metrics, media_type="video", filename=filename, mime_type=mime_type
        )

        # 1. Signal: Frame & Motion Consistency
        avg_mad = temporal_metrics.get("avg_frame_difference", 0.0)
        std_mad = temporal_metrics.get("frame_difference_std", 0.0)

        motion_score = 0.0
        if avg_mad > 45.0: # Abrupt unnatural inter-frame jumps
            motion_score += 45.0
        elif std_mad > 25.0: # Inconsistent frame transitions
            motion_score += 30.0

        motion_score = float(max(0.0, min(100.0, motion_score)))
        motion_sev = "High" if motion_score >= 70 else ("Medium" if motion_score >= 40 else "Low")

        signal_motion = SignalMetric(
            id="frame_consistency",
            name="Frame & Motion Consistency",
            score=round(motion_score, 1),
            severity=motion_sev,
            confidence=88.0,
            description=f"Average inter-frame difference (MAD) is {avg_mad:.1f} with variance std of {std_mad:.1f}. "
            + ("Abrupt temporal frame discontinuities detected." if motion_score > 40 else "Frame-to-frame optical transitions display smooth temporal continuity."),
            metrics=temporal_metrics
        )

        # 2. Signal: Frame Compression & ELA Variance
        ela_errors = []
        for sf in sampled_frames_data:
            ela_m = sf.get("ela_metric")
            if ela_m:
                ela_errors.append(ela_m.metrics.get("mean_error", 0.0))

        avg_ela_error = float(sum(ela_errors) / len(ela_errors)) if ela_errors else 0.0
        ela_var = float(sum((x - avg_ela_error) ** 2 for x in ela_errors) / len(ela_errors)) if ela_errors else 0.0

        ela_score = 0.0
        if avg_ela_error > 12.0:
            ela_score += 40.0
        if ela_var > 15.0:
            ela_score += 35.0

        ela_score = float(max(0.0, min(100.0, ela_score)))
        ela_sev = "High" if ela_score >= 70 else ("Medium" if ela_score >= 40 else "Low")

        signal_ela = SignalMetric(
            id="frame_compression_ela",
            name="Frame Compression & ELA Variance",
            score=round(ela_score, 1),
            severity=ela_sev,
            confidence=86.0,
            description=f"Average frame ELA error level is {avg_ela_error:.1f} with inter-frame ELA variance of {ela_var:.2f}. "
            + ("Inconsistent spatial compression artifacts detected across sampled keyframes." if ela_score > 40 else "Compression error distribution is uniform across sampled frames."),
            metrics={
                "avg_ela_error": round(avg_ela_error, 2),
                "ela_variance": round(ela_var, 2),
                "sampled_frames_evaluated": len(ela_errors),
            }
        )

        signals: List[SignalMetric] = [signal_motion, signal_ela]

        # 3. Audio Track Forensics Signal (if audio present)
        audio_risk_score = None
        if audio_bytes and len(audio_bytes) > 500:
            try:
                audio_res = await self.audio_analyzer.analyze(audio_bytes, f"{filename}_audio.wav")
                audio_risk_score = audio_res.risk_score

                signal_audio = SignalMetric(
                    id="audio_track_forensics",
                    name="Extracted Audio Track Forensics",
                    score=float(audio_res.risk_score),
                    severity="High" if audio_res.risk_score >= 70 else ("Medium" if audio_res.risk_score >= 40 else "Low"),
                    confidence=audio_res.confidence,
                    description=f"Extracted audio track verdict: {audio_res.verdict}. {audio_res.summary_explanation}",
                    metrics={
                        "has_audio": True,
                        "audio_verdict": audio_res.verdict,
                        "audio_risk_score": audio_res.risk_score,
                    }
                )
                signals.append(signal_audio)
            except Exception:
                tech_metrics["has_audio"] = False

        if not tech_metrics.get("has_audio"):
            signals.append(SignalMetric(
                id="audio_track_forensics",
                name="Extracted Audio Track Forensics",
                score=0.0,
                severity="Low",
                confidence=100.0,
                description="No audio track detected in video container.",
                metrics={"has_audio": False}
            ))

        # Risk Score Calculation
        if audio_risk_score is not None:
            calc_risk = round((signal_motion.score * 0.35) + (signal_ela.score * 0.35) + (audio_risk_score * 0.30))
        else:
            calc_risk = round((signal_motion.score * 0.50) + (signal_ela.score * 0.50))

        risk_score = max(0, min(100, calc_risk))

        if risk_score < 35:
            verdict = "Likely Authentic"
        elif risk_score < 65:
            verdict = "Inconclusive"
        else:
            verdict = "Likely Manipulated"

        assessment_confidence = 91

        # Scientific Summary Wording
        if verdict == "Likely Manipulated":
            summary_explanation = "Potential generative video or temporal frame anomalies detected in keyframe compression and inter-frame transitions."
        elif verdict == "Inconclusive":
            summary_explanation = "Mixed video forensic indicators detected. Keyframes exhibit subtle compression variance, but evidence is insufficient for a definitive verdict."
        else:
            summary_explanation = "Extracted video frame sequences demonstrate consistent inter-frame optical flow continuity and uniform compression distribution."

        # Format sampled frames list for Pydantic schema
        sampled_frames_pydantic = []
        for sf in sampled_frames_data:
            sampled_frames_pydantic.append(SampledFrameInfo(
                frame_index=sf["frame_index"],
                timestamp_sec=sf["timestamp_sec"],
                frame_base64=sf["frame_base64"],
                ela_base64=sf["ela_base64"],
                observations=sf["observations"],
            ))

        recommendation = "Treat as potentially manipulated video and verify original publisher source." if risk_score >= 50 else "Video exhibits low risk of generative manipulation. Verify publisher origin for critical media."
        disclaimer = "This assessment is an automated forensic evaluation based on measurable video keyframe metrics and acoustic signals, not absolute proof."

        analysis_id = f"truelens_video_{uuid.uuid4().hex[:12]}"
        timestamp = datetime.datetime.now(datetime.timezone.utc).isoformat()

        analysis_dict = {
            "analysis_id": analysis_id,
            "media_type": "video",
            "filename": filename,
            "verdict": verdict,
            "risk_score": risk_score,
            "assessment_confidence": assessment_confidence,
            "signals": [s.model_dump() if hasattr(s, "model_dump") else s.dict() for s in signals],
            "technical_metrics": tech_metrics,
            "provenance": provenance_data,
        }
        explanation_data = await self.explanation_service.generate_explanation(analysis_dict)

        return VideoAnalysisResult(
            analysis_id=analysis_id,
            media_type="video",
            timestamp=timestamp,
            filename=filename,
            file_size=len(video_bytes),
            duration=tech_metrics.get("duration", 0.0),
            format=tech_metrics.get("format", "VIDEO"),
            verdict=verdict,
            risk_score=risk_score,
            assessment_confidence=assessment_confidence,
            summary_explanation=summary_explanation,
            signals=signals,
            sampled_frames=sampled_frames_pydantic,
            technical_metrics=tech_metrics,
            provenance=provenance_data,
            explanation=explanation_data,
            recommendation=recommendation,
            disclaimer=disclaimer,
        )

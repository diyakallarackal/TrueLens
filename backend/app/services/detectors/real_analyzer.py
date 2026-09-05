import io
import uuid
import datetime
import math
from typing import List, Dict, Any
from PIL import Image

from app.services.detectors.base import ImageDetector, AnalysisResult, SignalMetric, ImageDimensions
from app.services.exif_parser import extract_exif_data, analyze_exif_signals
from app.services.ela import perform_ela
from app.services.noise_analysis import analyze_noise_residuals
from app.services.frequency import analyze_fft_spectrum


from app.services.source_verifier import TrueLensSourceVerifierSuite
from app.services.explanation_service import GenAIExplanationService


class RealImageAnalyzer(ImageDetector):
    """
    Primary image detection engine executing multi-signal image forensics:
    - EXIF & Camera Hardware integrity / Software tags
    - Error Level Analysis (ELA) & Compression Variance
    - High-Pass Noise Residual & RGB Channel Correlation
    - 2D Fast Fourier Transform (FFT) Spectral Grid Artifacts
    """

    def __init__(self):
        self.verifier_suite = TrueLensSourceVerifierSuite()
        self.explanation_service = GenAIExplanationService()

    @property
    def name(self) -> str:
        return "Real Forensic Signal Engine"

    @property
    def is_available(self) -> bool:
        return True

    async def analyze(self, image_bytes: bytes, filename: str) -> AnalysisResult:
        # Load image via Pillow safely
        try:
            pil_img = Image.open(io.BytesIO(image_bytes))
            pil_img.verify()  # Integrity check
            # Re-open after verify as verify modifies internal state
            pil_img = Image.open(io.BytesIO(image_bytes))
        except Exception as e:
            raise ValueError(f"Corrupted or unsupported image file: {str(e)}")

        img_format = pil_img.format or "UNKNOWN"
        w, h = pil_img.size
        
        # Calculate aspect ratio string
        gcd_val = math.gcd(w, h)
        aspect_str = f"{w // gcd_val}:{h // gcd_val}" if gcd_val > 0 else f"{w}:{h}"
        dimensions = ImageDimensions(width=w, height=h, aspect_ratio=aspect_str)

        # 1. EXIF & Metadata analysis
        metadata_dict = extract_exif_data(pil_img)
        exif_signal = analyze_exif_signals(pil_img, metadata_dict)

        # 2. Error Level Analysis (ELA)
        ela_signal, ela_base64 = perform_ela(pil_img)

        # 3. High-Pass Noise Residual & Channel Correlation
        noise_signal = analyze_noise_residuals(pil_img)

        # 4. 2D FFT Frequency Spectrum Analysis
        fft_signal = analyze_fft_spectrum(pil_img)

        # 5. Provenance & Source Traceability Verification
        mime_type = f"image/{img_format.lower()}"
        provenance_data = self.verifier_suite.run_verification(
            image_bytes, metadata_dict, media_type="image", filename=filename, mime_type=mime_type
        )

        signals: List[SignalMetric] = [
            exif_signal,
            ela_signal,
            fft_signal,
            noise_signal,
        ]

        # Transparent Weighted Risk Scoring Formula
        weights = {
            "exif_software_tag": 0.35,
            "error_level_analysis": 0.25,
            "fft_spectral_grid": 0.22,
            "noise_residual": 0.18,
        }

        total_weighted_score = sum(sig.score * weights.get(sig.id, 0.25) for sig in signals)
        total_weights = sum(weights.get(sig.id, 0.25) for sig in signals)
        
        calculated_risk = round(total_weighted_score / total_weights) if total_weights > 0 else 0
        risk_score = max(0, min(100, calculated_risk))

        # Dynamic Verdict Determination
        if risk_score < 35:
            verdict = "Likely Authentic"
        elif risk_score < 65:
            verdict = "Inconclusive"
        else:
            verdict = "Likely Manipulated"

        # Calculate Confidence level
        confidence_base = 85.0
        if metadata_dict.get("has_exif"):
            confidence_base += 5.0
        if img_format.upper() in ["JPEG", "JPG"]:
            confidence_base += 4.0
        confidence = min(98, round(confidence_base))

        # Plain-language Summary Explanation
        explanation_parts = []
        high_severity_signals = [s for s in signals if s.severity == "High"]
        
        if verdict == "Likely Manipulated":
            if high_severity_signals:
                sig_names = ", ".join([s.name for s in high_severity_signals])
                explanation_parts.append(f"High risk forensic anomalies detected in: {sig_names}.")
            else:
                explanation_parts.append("Multiple forensic signals indicate digital alteration or synthetic image generation.")
        elif verdict == "Inconclusive":
            explanation_parts.append("Mixed forensic indicators detected. Some parameters exhibit subtle compression or structural anomalies, but evidence is insufficient for a definitive verdict.")
        else:
            explanation_parts.append("Forensic signals show consistent natural image characteristics, hardware camera metadata, and smooth spectral decay.")

        summary_explanation = " ".join(explanation_parts)

        recommendation = "Treat as potentially manipulated and verify the source before sharing." if risk_score >= 50 else "Image exhibits low risk of artificial manipulation. Verify publisher origin for critical media."
        disclaimer = "This analysis is an automated forensic assessment based on measurable image metrics and statistical signals, not absolute proof."

        analysis_id = f"truelens_{uuid.uuid4().hex[:12]}"
        timestamp = datetime.datetime.now(datetime.timezone.utc).isoformat()

        analysis_dict = {
            "analysis_id": analysis_id,
            "media_type": "image",
            "filename": filename,
            "verdict": verdict,
            "risk_score": risk_score,
            "confidence": confidence,
            "signals": [s.model_dump() if hasattr(s, "model_dump") else s.dict() for s in signals],
            "metadata": metadata_dict,
            "provenance": provenance_data,
        }
        explanation_data = await self.explanation_service.generate_explanation(analysis_dict)

        return AnalysisResult(
            analysis_id=analysis_id,
            media_type="image",
            timestamp=timestamp,
            filename=filename,
            file_size=len(image_bytes),
            dimensions=dimensions,
            format=img_format,
            verdict=verdict,
            risk_score=risk_score,
            confidence=confidence,
            summary_explanation=summary_explanation,
            signals=signals,
            ela_heatmap_base64=ela_base64,
            metadata=metadata_dict,
            provenance=provenance_data,
            explanation=explanation_data,
            recommendation=recommendation,
            disclaimer=disclaimer,
        )

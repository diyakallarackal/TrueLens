import os
import json
import urllib.request
from typing import Dict, List, Any, Optional


class LocalEvidenceExplainer:
    """
    Deterministic evidence-grounded explanation engine.
    Generates structured human-readable explanations derived strictly from actual forensic signals,
    metadata, and provenance fields, without inventing facts or claiming certainty.
    """

    def generate_explanation(self, analysis_data: Dict[str, Any]) -> Dict[str, Any]:
        verdict = analysis_data.get("verdict", "Inconclusive")
        risk_score = analysis_data.get("risk_score", 0)
        media_type = analysis_data.get("media_type", "image").capitalize()
        signals = analysis_data.get("signals", [])
        provenance = analysis_data.get("provenance", {})
        metadata = analysis_data.get("metadata", {})
        tech_metrics = analysis_data.get("technical_metrics", {})

        # 1. Summary statement
        summary_parts = [
            f"TrueLens evaluated {len(signals)} forensic signal indicators for this {media_type.lower()} file, yielding a manipulation risk score of {risk_score}/100 ({verdict})."
        ]

        high_sev = [s for s in signals if s.get("severity") in ["High", "Critical"]]
        if verdict == "Likely Manipulated":
            if high_sev:
                sig_names = ", ".join([s.get("name") for s in high_sev])
                summary_parts.append(f"Significant risk anomalies were identified in: {sig_names}.")
            else:
                summary_parts.append("Elevated risk scores across multiple forensic signals indicate potential digital alteration or synthetic generation.")
        elif verdict == "Inconclusive":
            summary_parts.append("Forensic signals present subtle structural or compression anomalies, but evidence is insufficient for a definitive verdict.")
        else:
            summary_parts.append("Calculated forensic indicators align with expected organic media characteristics.")

        summary = " ".join(summary_parts)

        # 2. Key findings from actual signals & metadata
        key_findings = []
        for s in signals:
            score = s.get("score", 0)
            name = s.get("name", "Signal")
            desc = s.get("description", "")
            if score >= 40:
                key_findings.append(f"{name} (Score: {score}/100): {desc}")
            elif score == 0 and s.get("id") == "audio_track_forensics" and not tech_metrics.get("has_audio", True):
                key_findings.append("No audio track was detected in the video container.")

        if metadata.get("has_camera_hardware"):
            make = metadata.get("camera_make") or ""
            model = metadata.get("camera_model") or ""
            key_findings.append(f"Header verification: Genuine camera hardware tags present ({make} {model}).".strip())
        elif metadata.get("software_detected"):
            key_findings.append(f"Header verification: Editing software signature detected ({metadata.get('software_detected')}).")

        if not key_findings:
            key_findings.append(f"All calculated {media_type.lower()} forensic signals registered low risk scores.")

        # 3. Limitations & Missing Evidence
        limitations = []
        c2pa_info = provenance.get("c2pa", {})
        if not c2pa_info.get("has_c2pa"):
            limitations.append("No Content Credentials (C2PA) manifest was detected in the media header.")
        else:
            limitations.append(f"C2PA manifest detected (Issuer: {c2pa_info.get('issuer', 'Signed manifest')}).")

        ext_search = provenance.get("external_search", {})
        if ext_search.get("status") == "unconfigured":
            limitations.append("External reverse source search is not configured.")

        limitations.append("Forensic signal scores represent statistical risk indicators rather than absolute proof of authenticity or synthetic generation.")

        # 4. Recommendation
        if risk_score >= 50:
            recommendation = f"Treat as potentially manipulated {media_type.lower()} media. Verify original publisher origin before relying on or sharing this file."
        elif verdict == "Inconclusive":
            recommendation = f"Evidence is inconclusive. Seek the original source or additional independent verification for critical {media_type.lower()} media."
        else:
            recommendation = f"Available evidence does not indicate strong signs of artificial manipulation, but this automated assessment cannot guarantee absolute authenticity."

        return {
            "provider": "Deterministic Evidence Explainer (Local Fallback)",
            "summary": summary,
            "key_findings": key_findings[:5], # Top findings
            "limitations": limitations,
            "recommendation": recommendation,
        }


class GenAIExplanationService:
    """
    GenAI Evidence Explanation Service.
    Attempts remote LLM explanation using strictly grounded prompts if API keys are set.
    Falls back gracefully to LocalEvidenceExplainer if unconfigured or on error.
    """

    def __init__(self):
        self.local_explainer = LocalEvidenceExplainer()
        self.google_api_key = os.getenv("GOOGLE_API_KEY") or os.getenv("GEMINI_API_KEY")

    @property
    def is_genai_configured(self) -> bool:
        return bool(self.google_api_key and len(self.google_api_key.strip()) > 0)

    async def generate_explanation(self, analysis_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generates an evidence-grounded explanation from the analysis JSON.
        """
        if not self.is_genai_configured:
            return self.local_explainer.generate_explanation(analysis_data)

        # Execute remote Gemini LLM call with strict prompt safety grounding
        try:
            url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={self.google_api_key}"
            
            prompt_text = f"""
System instruction: You are an evidence explanation assistant for a media-forensics application named TrueLens. Explain ONLY the evidence provided in the analysis data below. Do not invent facts. Do not infer an external source that is not present. Do not claim certainty. Treat forensic signals as indicators rather than proof. Clearly mention uncertainty and missing evidence.

Analysis Data:
{json.dumps(analysis_data, indent=2)}

Respond with JSON format strictly matching this structure:
{{
  "summary": "2-3 sentence overview of why TrueLens reached this verdict",
  "key_findings": ["Factual bullet point 1", "Factual bullet point 2"],
  "limitations": ["Missing evidence or uncertainty 1", "Unconfigured search notice"],
  "recommendation": "Concise recommended next action"
}}
"""
            req_payload = {
                "contents": [{"parts": [{"text": prompt_text}]}],
                "generationConfig": {"responseMimeType": "application/json"}
            }

            data_bytes = json.dumps(req_payload).encode("utf-8")
            req = urllib.request.Request(url, data=data_bytes, headers={"Content-Type": "application/json"})
            
            with urllib.request.urlopen(req, timeout=10) as response:
                if response.status == 200:
                    resp_body = json.loads(response.read().decode("utf-8"))
                    text_out = resp_body["candidates"][0]["content"]["parts"][0]["text"]
                    parsed = json.loads(text_out)
                    parsed["provider"] = "Gemini GenAI Explanation Provider"
                    return parsed
        except Exception:
            # Fallback to local explainer if remote API times out or fails
            pass

        return self.local_explainer.generate_explanation(analysis_data)

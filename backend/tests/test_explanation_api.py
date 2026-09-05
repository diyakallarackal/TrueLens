import pytest
import io
import os
import sys
import numpy as np
import scipy.io.wavfile as wavfile
from PIL import Image, ImageDraw
from fastapi.testclient import TestClient

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.main import app
from app.services.explanation_service import GenAIExplanationService, LocalEvidenceExplainer

client = TestClient(app)


def create_test_image_bytes():
    img = Image.new("RGB", (200, 200), color=(100, 150, 200))
    buf = io.BytesIO()
    img.save(buf, format="JPEG")
    return buf.getvalue()


def create_test_wav_bytes(duration_sec=0.5, sample_rate=16000):
    t = np.linspace(0, duration_sec, int(sample_rate * duration_sec), endpoint=False)
    audio_signal = (0.5 * np.sin(2 * np.pi * 440 * t) * 32767).astype(np.int16)
    buf = io.BytesIO()
    wavfile.write(buf, sample_rate, audio_signal)
    return buf.getvalue()


def test_capabilities_includes_explanation():
    response = client.get("/api/capabilities")
    assert response.status_code == 200
    data = response.json()
    assert data["genai_explanation"] is True
    assert "genai_explanation_provider" in data


def test_local_explainer_directly():
    explainer = LocalEvidenceExplainer()
    mock_data = {
        "verdict": "Likely Authentic",
        "risk_score": 15,
        "media_type": "image",
        "signals": [
            {"id": "exif", "name": "EXIF Metadata", "score": 10, "severity": "Low", "description": "Clean camera tags"}
        ],
        "metadata": {"has_camera_hardware": True, "camera_make": "Canon"},
        "provenance": {"c2pa": {"has_c2pa": False}, "external_search": {"status": "unconfigured"}},
    }
    explanation = explainer.generate_explanation(mock_data)
    assert "summary" in explanation
    assert "key_findings" in explanation
    assert "limitations" in explanation
    assert "recommendation" in explanation
    assert explanation["provider"] == "Deterministic Evidence Explainer (Local Fallback)"


def test_image_analysis_includes_explanation():
    img_bytes = create_test_image_bytes()
    response = client.post(
        "/api/analyze",
        files={"file": ("explain_test.jpg", img_bytes, "image/jpeg")}
    )
    assert response.status_code == 200
    data = response.json()
    assert "explanation" in data
    assert data["explanation"] is not None
    assert "summary" in data["explanation"]
    assert "key_findings" in data["explanation"]
    assert len(data["explanation"]["key_findings"]) > 0


def test_audio_analysis_includes_explanation():
    wav_bytes = create_test_wav_bytes()
    response = client.post(
        "/api/analyze/audio",
        files={"file": ("explain_test.wav", wav_bytes, "audio/wav")}
    )
    assert response.status_code == 200
    data = response.json()
    assert "explanation" in data
    assert data["explanation"] is not None
    assert "summary" in data["explanation"]
    assert "recommendation" in data["explanation"]

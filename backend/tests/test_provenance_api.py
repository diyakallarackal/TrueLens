import pytest
import io
import os
import sys
import numpy as np
import scipy.io.wavfile
from PIL import Image
from fastapi.testclient import TestClient

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.main import app

client = TestClient(app)


def create_image_bytes():
    img = Image.new("RGB", (150, 150), color=(80, 120, 180))
    buf = io.BytesIO()
    img.save(buf, format="JPEG")
    return buf.getvalue()


def create_wav_bytes():
    t = np.linspace(0, 1.0, 44100, endpoint=False)
    sig = (0.5 * np.sin(2 * np.pi * 440 * t) * 32767).astype(np.int16)
    buf = io.BytesIO()
    scipy.io.wavfile.write(buf, 44100, sig)
    return buf.getvalue()


def test_capabilities_endpoint_phase4():
    res = client.get("/api/capabilities")
    assert res.status_code == 200
    data = res.json()
    assert data["image_analysis"] is True
    assert data["audio_analysis"] is True
    assert data["video_analysis"] is True
    assert data["content_credentials"] is True
    assert data["metadata_extraction"] is True
    assert data["external_reverse_search"] is False


def test_image_metadata_extraction():
    img_bytes = create_image_bytes()
    res = client.post("/api/analyze", files={"file": ("photo.jpg", img_bytes, "image/jpeg")})
    assert res.status_code == 200
    data = res.json()
    assert "provenance" in data
    prov = data["provenance"]
    assert "timeline" in prov
    assert "what_we_found" in prov
    assert len(prov["what_we_found"]) >= 2
    assert "metadata_assessment" in prov


def test_audio_metadata_extraction():
    wav_bytes = create_wav_bytes()
    res = client.post("/api/analyze/audio", files={"file": ("speech.wav", wav_bytes, "audio/wav")})
    assert res.status_code == 200
    data = res.json()
    assert "provenance" in data
    prov = data["provenance"]
    assert prov["metadata_assessment"]["has_metadata"] is True
    assert "44100 Hz" in prov["metadata_assessment"]["sample_rate"]


def test_missing_metadata_handling():
    # PNG created without EXIF
    img = Image.new("RGB", (50, 50), color=(50, 50, 50))
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    res = client.post("/api/analyze", files={"file": ("plain.png", buf.getvalue(), "image/png")})
    assert res.status_code == 200
    data = res.json()
    meta_assess = data["provenance"]["metadata_assessment"]
    assert meta_assess["camera_make"] == "Not available"
    assert meta_assess["camera_model"] == "Not available"


def test_c2pa_absent():
    img_bytes = create_image_bytes()
    res = client.post("/api/analyze", files={"file": ("noc2pa.jpg", img_bytes, "image/jpeg")})
    assert res.status_code == 200
    data = res.json()
    c2pa_info = data["provenance"]["c2pa"]
    assert c2pa_info["has_c2pa"] is False
    assert c2pa_info["c2pa_status"] == "No Content Credentials found"


def test_external_reverse_search_unconfigured():
    img_bytes = create_image_bytes()
    res = client.post("/api/analyze", files={"file": ("test.jpg", img_bytes, "image/jpeg")})
    assert res.status_code == 200
    data = res.json()
    ext_info = data["provenance"]["external_search"]
    assert ext_info["status"] == "unconfigured"
    assert ext_info["message"] == "External source search is not configured."
    assert ext_info["matches_found"] == 0
    assert len(ext_info["matches"]) == 0


def test_unified_response_schema():
    img_bytes = create_image_bytes()
    res = client.post("/api/analyze", files={"file": ("unified.jpg", img_bytes, "image/jpeg")})
    assert res.status_code == 200
    data = res.json()
    assert "analysis_id" in data
    assert "media_type" in data
    assert "verdict" in data
    assert "risk_score" in data
    assert "signals" in data
    assert "provenance" in data
    assert "recommendation" in data
    assert "disclaimer" in data


def test_phase1_image_regression():
    img_bytes = create_image_bytes()
    res = client.post("/api/analyze", files={"file": ("phase1.jpg", img_bytes, "image/jpeg")})
    assert res.status_code == 200
    assert len(res.json()["signals"]) == 4


def test_phase2_audio_regression():
    wav_bytes = create_wav_bytes()
    res = client.post("/api/analyze/audio", files={"file": ("phase2.wav", wav_bytes, "audio/wav")})
    assert res.status_code == 200
    assert len(res.json()["signals"]) >= 2

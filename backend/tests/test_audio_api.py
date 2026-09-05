import pytest
import io
import os
import sys
import numpy as np
import scipy.io.wavfile
from PIL import Image, ImageDraw
from fastapi.testclient import TestClient

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.main import app

client = TestClient(app)


def create_test_wav_bytes(duration_sec=1.5, sample_rate=44100, freq=440.0):
    t = np.linspace(0, duration_sec, int(sample_rate * duration_sec), endpoint=False)
    # Generate 440 Hz sine wave + slight harmonics
    audio_data = 0.5 * np.sin(2 * np.pi * freq * t) + 0.1 * np.sin(2 * np.pi * 880 * t)
    pcm_data = (audio_data * 32767).astype(np.int16)
    
    buf = io.BytesIO()
    scipy.io.wavfile.write(buf, sample_rate, pcm_data)
    return buf.getvalue()


def create_test_image_bytes():
    img = Image.new("RGB", (200, 200), color=(100, 150, 200))
    buf = io.BytesIO()
    img.save(buf, format="JPEG")
    return buf.getvalue()


def test_capabilities_endpoint():
    response = client.get("/api/capabilities")
    assert response.status_code == 200
    data = response.json()
    assert data["image_analysis"] is True
    assert data["audio_analysis"] is True
    assert data["video_analysis"] is True
    assert data["content_credentials"] is True


def test_analyze_valid_wav_audio():
    wav_bytes = create_test_wav_bytes()
    response = client.post(
        "/api/analyze/audio",
        files={"file": ("speech_sample.wav", wav_bytes, "audio/wav")}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["media_type"] == "audio"
    assert data["filename"] == "speech_sample.wav"
    assert data["verdict"] in ["Likely Authentic", "Likely Manipulated", "Inconclusive"]
    assert 0 <= data["risk_score"] <= 100
    assert len(data["signals"]) >= 2
    assert "spectrogram_base64" in data
    assert data["spectrogram_base64"].startswith("data:image/png;base64,")
    assert "technical_metrics" in data
    assert "provenance" in data


def test_analyze_invalid_corrupted_audio():
    bad_bytes = b"NOT_REAL_AUDIO_DATA_BYTES_999"
    response = client.post(
        "/api/analyze/audio",
        files={"file": ("corrupt.wav", bad_bytes, "audio/wav")}
    )
    assert response.status_code == 400
    assert "detail" in response.json()


def test_audio_and_image_history_persistence():
    # 1. Analyze image
    img_res = client.post(
        "/api/analyze",
        files={"file": ("reg_img.jpg", create_test_image_bytes(), "image/jpeg")}
    )
    assert img_res.status_code == 200
    img_id = img_res.json()["analysis_id"]

    # 2. Analyze audio
    aud_res = client.post(
        "/api/analyze/audio",
        files={"file": ("reg_aud.wav", create_test_wav_bytes(), "audio/wav")}
    )
    assert aud_res.status_code == 200
    aud_id = aud_res.json()["analysis_id"]

    # 3. Retrieve history list
    hist_res = client.get("/api/history")
    assert hist_res.status_code == 200
    items = hist_res.json()
    assert len(items) >= 2
    
    ids = [i["id"] for i in items]
    assert img_id in ids
    assert aud_id in ids

    # 4. Verify detail retrieval for audio
    detail_res = client.get(f"/api/history/{aud_id}")
    assert detail_res.status_code == 200
    assert detail_res.json()["media_type"] == "audio"


def test_image_analysis_regression():
    img_bytes = create_test_image_bytes()
    response = client.post(
        "/api/analyze",
        files={"file": ("regression_test.jpg", img_bytes, "image/jpeg")}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["verdict"] in ["Likely Authentic", "Likely Manipulated", "Inconclusive"]
    assert len(data["signals"]) == 4

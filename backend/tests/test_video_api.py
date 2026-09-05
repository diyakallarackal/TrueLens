import pytest
import io
import os
import sys
import tempfile
import numpy as np
import cv2
from PIL import Image
from fastapi.testclient import TestClient

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.main import app

client = TestClient(app)


def create_test_mp4_bytes(duration_sec=2, fps=30, width=160, height=120):
    """
    Creates a valid MP4 video binary in-memory using OpenCV VideoWriter.
    """
    temp_fd, temp_path = tempfile.mkstemp(suffix=".mp4")
    os.close(temp_fd)
    
    try:
        fourcc = cv2.VideoWriter_fourcc(*"mp4v")
        out = cv2.VideoWriter(temp_path, fourcc, fps, (width, height))
        total_frames = int(duration_sec * fps)

        for i in range(total_frames):
            # Create animated frame with moving rectangle
            frame = np.zeros((height, width, 3), dtype=np.uint8)
            frame[:, :] = (i * 2 % 255, 100, 150)
            x_pos = int((i * 4) % (width - 20))
            cv2.rectangle(frame, (x_pos, 20), (x_pos + 20, 60), (0, 255, 200), -1)
            out.write(frame)

        out.release()

        with open(temp_path, "rb") as f:
            return f.read()
    finally:
        if os.path.exists(temp_path):
            os.remove(temp_path)


def create_test_image_bytes():
    img = Image.new("RGB", (200, 200), color=(120, 180, 220))
    buf = io.BytesIO()
    img.save(buf, format="JPEG")
    return buf.getvalue()


def test_video_capabilities():
    response = client.get("/api/capabilities")
    assert response.status_code == 200
    data = response.json()
    assert data["image_analysis"] is True
    assert data["audio_analysis"] is True
    assert data["video_analysis"] is True
    assert data["content_credentials"] is True


def test_analyze_valid_mp4_video():
    mp4_bytes = create_test_mp4_bytes()
    response = client.post(
        "/api/analyze/video",
        files={"file": ("test_clip.mp4", mp4_bytes, "video/mp4")}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["media_type"] == "video"
    assert data["filename"] == "test_clip.mp4"
    assert data["verdict"] in ["Likely Authentic", "Likely Manipulated", "Inconclusive"]
    assert 0 <= data["risk_score"] <= 100
    assert "assessment_confidence" in data
    assert len(data["signals"]) >= 2
    assert len(data["sampled_frames"]) > 0
    assert "technical_metrics" in data
    assert data["technical_metrics"]["width"] == 160
    assert data["technical_metrics"]["height"] == 120


def test_analyze_corrupted_video():
    bad_bytes = b"CORRUPTED_VIDEO_HEADER_DATA_12345"
    response = client.post(
        "/api/analyze/video",
        files={"file": ("bad_video.mp4", bad_bytes, "video/mp4")}
    )
    assert response.status_code == 400
    assert "detail" in response.json()


def test_video_history_persistence():
    mp4_bytes = create_test_mp4_bytes()
    res = client.post(
        "/api/analyze/video",
        files={"file": ("history_video.mp4", mp4_bytes, "video/mp4")}
    )
    assert res.status_code == 200
    video_id = res.json()["analysis_id"]

    # Check history list
    hist_res = client.get("/api/history")
    assert hist_res.status_code == 200
    items = hist_res.json()
    ids = [i["id"] for i in items]
    assert video_id in ids

    # Check history detail
    detail_res = client.get(f"/api/history/{video_id}")
    assert detail_res.status_code == 200
    assert detail_res.json()["media_type"] == "video"


def test_full_media_suite_regression():
    # Test Image
    img_res = client.post(
        "/api/analyze",
        files={"file": ("reg_img.jpg", create_test_image_bytes(), "image/jpeg")}
    )
    assert img_res.status_code == 200
    assert img_res.json()["verdict"] in ["Likely Authentic", "Likely Manipulated", "Inconclusive"]

    # Test Capabilities
    cap_res = client.get("/api/capabilities")
    assert cap_res.status_code == 200
    assert cap_res.json()["video_analysis"] is True

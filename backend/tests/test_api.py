import pytest
import io
import os
import sys
from PIL import Image, ImageDraw
from fastapi.testclient import TestClient

# Add backend directory to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.main import app
from app.services.detectors.real_analyzer import RealImageAnalyzer

client = TestClient(app)


def create_test_image_bytes(format="JPEG", color=(200, 100, 50), size=(300, 300)):
    img = Image.new("RGB", size, color=color)
    draw = ImageDraw.Draw(img)
    draw.rectangle([50, 50, 150, 150], fill=(50, 200, 100))
    draw.line([0, 0, 300, 300], fill=(255, 255, 255), width=3)
    buf = io.BytesIO()
    img.save(buf, format=format)
    return buf.getvalue()


def test_health_endpoint():
    response = client.get("/api/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "real_analyzer" in data["detectors"]


def test_analyze_valid_jpeg():
    img_bytes = create_test_image_bytes(format="JPEG")
    response = client.post(
        "/api/analyze",
        files={"file": ("test_image.jpg", img_bytes, "image/jpeg")}
    )
    assert response.status_code == 200
    data = response.json()
    assert "analysis_id" in data
    assert data["filename"] == "test_image.jpg"
    assert data["verdict"] in ["Likely Authentic", "Likely Manipulated", "Inconclusive"]
    assert 0 <= data["risk_score"] <= 100
    assert len(data["signals"]) == 4
    assert data["ela_heatmap_base64"] is not None
    assert data["ela_heatmap_base64"].startswith("data:image/png;base64,")


def test_analyze_corrupted_file():
    bad_bytes = b"NOT_AN_IMAGE_DATA_12345"
    response = client.post(
        "/api/analyze",
        files={"file": ("bad.jpg", bad_bytes, "image/jpeg")}
    )
    assert response.status_code == 400
    assert "detail" in response.json()


def test_history_endpoints():
    # Perform an analysis first
    img_bytes = create_test_image_bytes()
    res1 = client.post(
        "/api/analyze",
        files={"file": ("history_test.jpg", img_bytes, "image/jpeg")}
    )
    assert res1.status_code == 200
    analysis_id = res1.json()["analysis_id"]

    # Test list history
    res2 = client.get("/api/history")
    assert res2.status_code == 200
    history_list = res2.json()
    assert len(history_list) >= 1

    # Test detail history
    res3 = client.get(f"/api/history/{analysis_id}")
    assert res3.status_code == 200
    assert res3.json()["analysis_id"] == analysis_id

    # Test delete history
    res4 = client.delete(f"/api/history/{analysis_id}")
    assert res4.status_code == 200
    assert res4.json()["status"] == "deleted"

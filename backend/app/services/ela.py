import io
import base64
from typing import Tuple
import numpy as np
import cv2
from PIL import Image
from app.services.detectors.base import SignalMetric


def perform_ela(pil_image: Image.Image, quality: int = 95) -> Tuple[SignalMetric, str]:
    """
    Performs Error Level Analysis (ELA) by re-compressing the image as JPEG 
    at a set quality level and computing localized compression error differences.
    
    Returns:
        (SignalMetric, ela_heatmap_base64_png)
    """
    # Convert original image to RGB NumPy array
    rgb_orig = np.array(pil_image.convert("RGB"))
    
    # Save to memory buffer as JPEG with specified quality
    buffer = io.BytesIO()
    pil_image.convert("RGB").save(buffer, format="JPEG", quality=quality)
    buffer.seek(0)
    
    # Load re-compressed image back
    recompressed_pil = Image.open(buffer)
    rgb_recompressed = np.array(recompressed_pil)
    
    # Compute absolute pixel difference
    diff = cv2.absdiff(rgb_orig, rgb_recompressed).astype(np.float32)
    
    # Compute mean channel error map
    error_map = np.mean(diff, axis=2) # 2D array (H, W)
    
    mean_error = float(np.mean(error_map))
    max_error = float(np.max(error_map))
    std_error = float(np.std(error_map))
    
    # Divide image into 4x4 region blocks and measure error variance across blocks
    h, w = error_map.shape
    bh, bw = max(1, h // 4), max(1, w // 4)
    block_means = []
    for r in range(4):
        for c in range(4):
            block = error_map[r * bh : (r + 1) * bh, c * bw : (c + 1) * bw]
            if block.size > 0:
                block_means.append(float(np.mean(block)))
                
    block_variance = float(np.var(block_means)) if block_means else 0.0
    
    # Score calculation
    # High error variance between regions or high mean error indicates inconsistent compression history (editing/splicing or synthetic generation)
    score = 0.0
    if mean_error > 8.0:
        score += min(50.0, (mean_error - 8.0) * 4.0)
    if block_variance > 2.0:
        score += min(50.0, block_variance * 8.0)
        
    score = float(max(0.0, min(100.0, score)))
    
    severity = "Low"
    if score >= 70:
        severity = "High"
    elif score >= 40:
        severity = "Medium"
        
    description = (
        f"Error Level Analysis shows average error level of {mean_error:.1f} and block error variance of {block_variance:.2f}. "
        + ("Significant non-uniform compression artifacts detected." if score > 50 else "Compression error distribution is relatively uniform across regions.")
    )
    
    # Generate visual ELA Heatmap image
    # Scale difference map for visualization (multiplier 15-20 brings out subtle ELA details)
    scaled_diff = np.clip(error_map * 15.0, 0, 255).astype(np.uint8)
    
    # Apply JET colormap for a striking digital-forensics heatmap visual
    heatmap_bgr = cv2.applyColorMap(scaled_diff, cv2.COLORMAP_JET)
    
    # Convert BGR to PNG Base64 string
    _, png_buf = cv2.imencode(".png", heatmap_bgr)
    ela_base64 = "data:image/png;base64," + base64.b64encode(png_buf).decode("utf-8")
    
    metric = SignalMetric(
        id="error_level_analysis",
        name="Error Level Analysis (ELA)",
        score=round(score, 1),
        severity=severity,
        confidence=88.0,
        description=description,
        metrics={
            "mean_error": round(mean_error, 2),
            "max_error": round(max_error, 2),
            "std_error": round(std_error, 2),
            "block_variance": round(block_variance, 2),
            "resaved_quality": quality
        }
    )
    
    return metric, ela_base64

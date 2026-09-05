import numpy as np
import cv2
from PIL import Image
from app.services.detectors.base import SignalMetric


def analyze_noise_residuals(pil_image: Image.Image) -> SignalMetric:
    """
    Analyzes high-pass noise residual characteristics, sensor pattern noise,
    and RGB inter-channel noise correlation.
    """
    rgb_arr = np.array(pil_image.convert("RGB")).astype(np.float32)
    gray_arr = cv2.cvtColor(rgb_arr.astype(np.uint8), cv2.COLOR_RGB2GRAY).astype(np.float32)
    
    # Isolate high-frequency noise residual via 3x3 median filter subtraction
    blurred = cv2.medianBlur(gray_arr.astype(np.uint8), 3).astype(np.float32)
    residual = gray_arr - blurred
    
    noise_std = float(np.std(residual))
    noise_mean = float(np.mean(np.abs(residual)))
    
    # Calculate RGB channel-wise noise residuals & inter-channel correlation
    r_chan, g_chan, b_chan = rgb_arr[:, :, 0], rgb_arr[:, :, 1], rgb_arr[:, :, 2]
    r_res = r_chan - cv2.medianBlur(r_chan.astype(np.uint8), 3).astype(np.float32)
    g_res = g_chan - cv2.medianBlur(g_chan.astype(np.uint8), 3).astype(np.float32)
    b_res = b_chan - cv2.medianBlur(b_chan.astype(np.uint8), 3).astype(np.float32)
    
    # Correlation coefficients between channels
    rg_corr = float(np.corrcoef(r_res.flatten(), g_res.flatten())[0, 1]) if np.std(r_res) > 0 and np.std(g_res) > 0 else 0.0
    gb_corr = float(np.corrcoef(g_res.flatten(), b_res.flatten())[0, 1]) if np.std(g_res) > 0 and np.std(b_res) > 0 else 0.0
    rb_corr = float(np.corrcoef(r_res.flatten(), b_res.flatten())[0, 1]) if np.std(r_res) > 0 and np.std(b_res) > 0 else 0.0
    
    avg_channel_corr = float((rg_corr + gb_corr + rb_corr) / 3.0)
    
    # Compute global Laplacian sharpness variance
    laplacian_var = float(cv2.Laplacian(gray_arr.astype(np.uint8), cv2.CV_64F).var())
    
    # Scoring calculation
    # Real camera sensors show consistent noise std (typically > 1.5) and high channel correlation (> 0.4)
    score = 0.0
    
    if noise_std < 1.2:  # Abnormally smooth/noise-free (typical of AI latent generation)
        score += 45.0
    elif noise_std > 8.0: # Abnormally noisy/synthetic grain
        score += 25.0
        
    if avg_channel_corr < 0.25:  # Low inter-channel noise correlation
        score += 35.0
        
    if laplacian_var < 50.0:  # Excessive smoothness / blur
        score += 20.0
        
    score = float(max(0.0, min(100.0, score)))
    
    severity = "Low"
    if score >= 70:
        severity = "High"
    elif score >= 40:
        severity = "Medium"
        
    description = (
        f"High-frequency noise standard deviation is {noise_std:.2f} with inter-channel noise correlation of {avg_channel_corr:.2f}. "
        + ("Low sensor noise residuals and decoupled channel noise detected." if score > 45 else "Noise distribution aligns with standard physical camera sensor profiles.")
    )
    
    return SignalMetric(
        id="noise_residual",
        name="Noise Residual & Channel Correlation",
        score=round(score, 1),
        severity=severity,
        confidence=82.0,
        description=description,
        metrics={
            "noise_std": round(noise_std, 2),
            "noise_mean": round(noise_mean, 2),
            "channel_correlation_avg": round(avg_channel_corr, 3),
            "rg_correlation": round(rg_corr, 3),
            "gb_correlation": round(gb_corr, 3),
            "rb_correlation": round(rb_corr, 3),
            "laplacian_variance": round(laplacian_var, 1),
        }
    )

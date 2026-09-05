import numpy as np
import cv2
from PIL import Image
from app.services.detectors.base import SignalMetric


def analyze_fft_spectrum(pil_image: Image.Image) -> SignalMetric:
    """
    Computes 2D Fast Fourier Transform (FFT) log magnitude spectrum 
    to detect periodic lattice grid spikes and spectral anomalies common in AI generation.
    """
    gray_arr = np.array(pil_image.convert("L")).astype(np.float32)
    h, w = gray_arr.shape
    
    # 2D FFT & shift origin to center
    fft_coeffs = np.fft.fft2(gray_arr)
    fft_shifted = np.fft.fftshift(fft_coeffs)
    magnitude = np.log(1.0 + np.abs(fft_shifted))
    
    cy, cx = h // 2, w // 2
    r = min(h, w) // 4  # Radius threshold for high-frequency region
    
    # Create radial distance mask
    y_grid, x_grid = np.ogrid[:h, :w]
    dist_from_center = np.sqrt((y_grid - cy) ** 2 + (x_grid - cx) ** 2)
    
    low_freq_mask = dist_from_center <= r
    high_freq_mask = (dist_from_center > r) & (dist_from_center <= r * 2)
    
    low_freq_energy = float(np.sum(magnitude[low_freq_mask])) if np.sum(low_freq_mask) > 0 else 1.0
    high_freq_energy = float(np.sum(magnitude[high_freq_mask])) if np.sum(high_freq_mask) > 0 else 0.0
    
    spectral_ratio = float(high_freq_energy / low_freq_energy) if low_freq_energy > 0 else 0.0
    
    # Peak prominence detection in high-frequency spectral domain
    high_freq_values = magnitude[high_freq_mask]
    if len(high_freq_values) > 0:
        high_freq_mean = np.mean(high_freq_values)
        high_freq_max = np.max(high_freq_values)
        peak_prominence = float(high_freq_max / (high_freq_mean + 1e-6))
    else:
        high_freq_mean = 0.0
        high_freq_max = 0.0
        peak_prominence = 1.0
        
    # Score calculation
    # High spectral peak prominence indicates periodic lattice grid artifacts from neural upsampling
    score = 0.0
    if peak_prominence > 2.2:
        score += min(60.0, (peak_prominence - 2.2) * 35.0)
        
    if spectral_ratio < 0.05:  # Unnaturally low high-frequency spectral content (overly smooth AI render)
        score += 30.0
    elif spectral_ratio > 0.4:  # Excessive high-frequency spectral energy noise
        score += 25.0
        
    score = float(max(0.0, min(100.0, score)))
    
    severity = "Low"
    if score >= 70:
        severity = "High"
    elif score >= 40:
        severity = "Medium"
        
    description = (
        f"2D FFT spectral peak prominence ratio is {peak_prominence:.2f} with high-frequency energy ratio of {spectral_ratio:.3f}. "
        + ("Periodic grid spikes detected in frequency spectrum, typical of neural upsampling layers." if score > 50 else "Frequency spectrum displays smooth natural isotropic decay without periodic grid artifacts.")
    )
    
    return SignalMetric(
        id="fft_spectral_grid",
        name="Frequency Domain (2D FFT) Grid Artifacts",
        score=round(score, 1),
        severity=severity,
        confidence=85.0,
        description=description,
        metrics={
            "peak_prominence": round(peak_prominence, 2),
            "spectral_ratio": round(spectral_ratio, 4),
            "high_freq_mean": round(float(high_freq_mean), 2),
            "high_freq_max": round(float(high_freq_max), 2),
        }
    )

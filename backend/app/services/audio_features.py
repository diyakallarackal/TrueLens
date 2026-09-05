import io
import base64
import numpy as np
import scipy.signal
import scipy.io.wavfile
import cv2
from typing import Dict, Any, Tuple, Optional

try:
    import soundfile as sf
    SF_AVAILABLE = True
except ImportError:
    SF_AVAILABLE = False

try:
    import mutagen
    MUTAGEN_AVAILABLE = True
except ImportError:
    MUTAGEN_AVAILABLE = False


def decode_audio_bytes(audio_bytes: bytes, filename: str) -> Tuple[np.ndarray, int, float, Dict[str, Any]]:
    """
    Decodes audio buffer into (signal_float32, sample_rate, duration_seconds, technical_metrics).
    Supports WAV, MP3, FLAC, M4A gracefully.
    """
    signal = None
    sample_rate = 44100
    duration = 0.0
    tech_metrics: Dict[str, Any] = {
        "sample_rate": 44100,
        "channels": 1,
        "bitrate_kbps": None,
        "codec": None,
        "duration_seconds": 0.0,
        "format": filename.split(".")[-1].upper() if "." in filename else "AUDIO",
    }

    # Extract metadata tags via Mutagen if available
    if MUTAGEN_AVAILABLE:
        try:
            mut_obj = mutagen.File(io.BytesIO(audio_bytes))
            if mut_obj and mut_obj.info:
                info = mut_obj.info
                tech_metrics["sample_rate"] = getattr(info, "sample_rate", 44100)
                tech_metrics["channels"] = getattr(info, "channels", 1)
                tech_metrics["duration_seconds"] = round(getattr(info, "length", 0.0), 2)
                bitrate = getattr(info, "bitrate", None)
                if bitrate:
                    tech_metrics["bitrate_kbps"] = round(bitrate / 1000)
                tech_metrics["codec"] = getattr(info, "codec", None) or mut_obj.__class__.__name__
        except Exception:
            pass

    # Try SoundFile decoding first (WAV, FLAC, OGG, etc.)
    if SF_AVAILABLE:
        try:
            data, sr = sf.read(io.BytesIO(audio_bytes))
            sample_rate = sr
            if data.ndim > 1:
                tech_metrics["channels"] = data.shape[1]
                signal = np.mean(data, axis=1) # Convert to mono float for spectral analysis
            else:
                tech_metrics["channels"] = 1
                signal = data
            duration = float(len(signal) / sample_rate)
            tech_metrics["sample_rate"] = sample_rate
            tech_metrics["duration_seconds"] = round(duration, 2)
            return signal.astype(np.float32), sample_rate, duration, tech_metrics
        except Exception:
            pass

    # Fallback 1: Scipy wavfile reader
    try:
        sr, data = scipy.io.wavfile.read(io.BytesIO(audio_bytes))
        sample_rate = sr
        if data.ndim > 1:
            tech_metrics["channels"] = data.shape[1]
            signal = np.mean(data, axis=1)
        else:
            tech_metrics["channels"] = 1
            signal = data
            
        # Normalize int data to float [-1.0, 1.0]
        if np.issubdtype(signal.dtype, np.integer):
            max_val = np.iinfo(signal.dtype).max
            signal = signal.astype(np.float32) / (max_val if max_val > 0 else 1.0)
        else:
            signal = signal.astype(np.float32)
            
        duration = float(len(signal) / sample_rate)
        tech_metrics["sample_rate"] = sample_rate
        tech_metrics["duration_seconds"] = round(duration, 2)
        return signal, sample_rate, duration, tech_metrics
    except Exception:
        pass

    # Fallback 2: Direct raw PCM float interpret if valid length
    if len(audio_bytes) > 44:
        raw_pcm = np.frombuffer(audio_bytes[44:], dtype=np.int16)
        if len(raw_pcm) > 1000:
            signal = raw_pcm.astype(np.float32) / 32768.0
            duration = float(len(signal) / 44100)
            tech_metrics["duration_seconds"] = round(duration, 2)
            return signal, 44100, duration, tech_metrics

    raise ValueError("Unsupported or corrupted audio format. Could not decode audio stream.")


def compute_spectral_features(signal: np.ndarray, sample_rate: int) -> Dict[str, Any]:
    """
    Computes spectral centroid, spectral bandwidth, spectral rolloff, 
    spectral flatness, RMS energy, and ZCR using SciPy signal processing.
    """
    if len(signal) == 0:
        raise ValueError("Audio signal contains no samples.")

    # 1. Time-domain metrics
    rms_energy = float(np.sqrt(np.mean(signal ** 2)))
    zcr = float(np.mean(np.abs(np.diff(np.sign(signal))) > 0)) if len(signal) > 1 else 0.0
    clipping_ratio = float(np.mean(np.abs(signal) >= 0.99))
    silence_ratio = float(np.mean(np.abs(signal) < 0.005))

    # 2. Short-Time Fourier Transform (STFT)
    nperseg = min(1024, max(256, len(signal) // 4))
    f, t, Zxx = scipy.signal.stft(signal, fs=sample_rate, nperseg=nperseg)
    mag = np.abs(Zxx) # Shape: (freq_bins, time_frames)

    # Frame-wise spectral centroid
    mag_sum = np.sum(mag, axis=0) + 1e-10
    f_col = f[:, np.newaxis]
    centroid_per_frame = np.sum(f_col * mag, axis=0) / mag_sum
    spectral_centroid = float(np.mean(centroid_per_frame))

    # Frame-wise spectral bandwidth
    diff_sq = (f_col - centroid_per_frame) ** 2
    bandwidth_per_frame = np.sqrt(np.sum(diff_sq * mag, axis=0) / mag_sum)
    spectral_bandwidth = float(np.mean(bandwidth_per_frame))

    # Spectral Rolloff (85th percentile frequency)
    cumulative_energy = np.cumsum(mag, axis=0)
    total_energy_per_frame = cumulative_energy[-1, :]
    rolloff_freqs = []
    for col_idx in range(mag.shape[1]):
        target = 0.85 * total_energy_per_frame[col_idx]
        cutoff_bin = np.where(cumulative_energy[:, col_idx] >= target)[0]
        if len(cutoff_bin) > 0:
            rolloff_freqs.append(f[cutoff_bin[0]])
        else:
            rolloff_freqs.append(f[-1])
    spectral_rolloff = float(np.mean(rolloff_freqs)) if rolloff_freqs else 0.0

    # Spectral Flatness (Geometric Mean / Arithmetic Mean)
    log_mag = np.log(mag + 1e-10)
    geom_mean = np.exp(np.mean(log_mag, axis=0))
    arith_mean = np.mean(mag, axis=0) + 1e-10
    flatness_per_frame = geom_mean / arith_mean
    spectral_flatness = float(np.mean(flatness_per_frame))

    # Dynamic Spectrogram Image Generation
    log_mag_db = 20 * np.log10(mag + 1e-6)
    min_db, max_db = np.min(log_mag_db), np.max(log_mag_db)
    norm_db = (log_mag_db - min_db) / ((max_db - min_db) + 1e-6)
    spec_img = (norm_db * 255).astype(np.uint8)
    
    # Flip vertically so low frequencies are at bottom, then apply VIRIDIS colormap
    spec_img_flipped = np.flipud(spec_img)
    spec_img_resized = cv2.resize(spec_img_flipped, (600, 240), interpolation=cv2.INTER_CUBIC)
    colormap_img = cv2.applyColorMap(spec_img_resized, cv2.COLORMAP_VIRIDIS)
    
    _, png_buf = cv2.imencode(".png", colormap_img)
    spectrogram_base64 = "data:image/png;base64," + base64.b64encode(png_buf).decode("utf-8")

    return {
        "rms_energy": round(rms_energy, 4),
        "zero_crossing_rate": round(zcr, 4),
        "clipping_ratio": round(clipping_ratio, 4),
        "silence_ratio": round(silence_ratio, 4),
        "spectral_centroid_hz": round(spectral_centroid, 1),
        "spectral_bandwidth_hz": round(spectral_bandwidth, 1),
        "spectral_rolloff_hz": round(spectral_rolloff, 1),
        "spectral_flatness": round(spectral_flatness, 4),
        "spectrogram_base64": spectrogram_base64,
    }

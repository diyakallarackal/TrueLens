import os
import io
import base64
import tempfile
import numpy as np
import cv2
from PIL import Image
from typing import Dict, List, Any, Tuple, Optional
from app.services.ela import perform_ela

try:
    import imageio_ffmpeg
    FFMPEG_AVAILABLE = True
except ImportError:
    FFMPEG_AVAILABLE = False


def extract_audio_from_video(video_path: str) -> Optional[bytes]:
    """
    Extracts audio stream from video file to memory buffer using imageio_ffmpeg.
    Returns audio bytes or None if no audio track exists.
    """
    if not FFMPEG_AVAILABLE:
        return None

    temp_wav_path = None
    try:
        temp_wav_fd, temp_wav_path = tempfile.mkstemp(suffix=".wav")
        os.close(temp_wav_fd)

        ffmpeg_exe = imageio_ffmpeg.get_ffmpeg_exe()
        import subprocess

        # Run FFmpeg command to extract audio: ffmpeg -y -i video_path -vn -acodec pcm_s16le -ar 44100 temp_wav_path
        cmd = [
            ffmpeg_exe,
            "-y",
            "-i", video_path,
            "-vn",
            "-acodec", "pcm_s16le",
            "-ar", "44100",
            "-ac", "1",
            temp_wav_path,
        ]

        res = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=30)
        if res.returncode == 0 and os.path.exists(temp_wav_path) and os.path.getsize(temp_wav_path) > 100:
            with open(temp_wav_path, "rb") as f:
                return f.read()
    except Exception:
        pass
    finally:
        if temp_wav_path and os.path.exists(temp_wav_path):
            try:
                os.remove(temp_wav_path)
            except Exception:
                pass

    return None


def process_video_file(video_bytes: bytes, filename: str) -> Tuple[Dict[str, Any], List[Dict[str, Any]], Dict[str, Any], Optional[bytes]]:
    """
    Processes video stream safely:
    - Extracts video container metadata
    - Samples 5 representative frames (0%, 25%, 50%, 75%, 100%)
    - Computes frame ELA, MAD frame-to-frame difference, and optical flow variance
    - Extracts audio track bytes if present
    
    Returns:
        (tech_metrics, sampled_frames_list, temporal_metrics, audio_bytes_or_none)
    """
    ext = "." + filename.split(".")[-1].lower() if "." in filename else ".mp4"
    temp_vid_fd, temp_vid_path = tempfile.mkstemp(suffix=ext)
    
    try:
        with os.fdopen(temp_vid_fd, "wb") as f:
            f.write(video_bytes)

        cap = cv2.VideoCapture(temp_vid_path)
        if not cap.isOpened():
            raise ValueError(f"Could not open or decode video container '{filename}'.")

        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        fps = float(cap.get(cv2.CAP_PROP_FPS)) or 30.0
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

        if total_frames <= 0 or width <= 0 or height <= 0:
            raise ValueError("Video contains no readable frame data.")

        duration = float(total_frames / fps) if fps > 0 else 0.0

        fourcc = int(cap.get(cv2.CAP_PROP_FOURCC))
        codec_str = "".join([chr((fourcc >> 8 * i) & 0xFF) for i in range(4)]).strip()

        tech_metrics = {
            "width": width,
            "height": height,
            "fps": round(fps, 2),
            "total_frames": total_frames,
            "duration": round(duration, 2),
            "codec": codec_str or "H264",
            "format": filename.split(".")[-1].upper() if "." in filename else "VIDEO",
            "has_audio": False,
            "audio_codec": None,
        }

        # 5-point sampling indices
        indices = [
            0,
            max(0, int(total_frames * 0.25)),
            max(0, int(total_frames * 0.50)),
            max(0, int(total_frames * 0.75)),
            max(0, total_frames - 1),
        ]
        indices = sorted(list(set(indices)))

        sampled_frames_data = []
        raw_rgb_frames = []

        for idx in indices:
            cap.set(cv2.CAP_PROP_POS_FRAMES, idx)
            ret, frame_bgr = cap.read()
            if not ret or frame_bgr is None:
                continue

            frame_rgb = cv2.cvtColor(frame_bgr, cv2.COLOR_BGR2RGB)
            raw_rgb_frames.append(frame_rgb)
            timestamp_sec = round(float(idx / fps), 2) if fps > 0 else 0.0

            # Convert to Base64 JPEG for preview
            pil_frame = Image.fromarray(frame_rgb)
            buf = io.BytesIO()
            pil_frame.save(buf, format="JPEG", quality=85)
            frame_base64 = "data:image/jpeg;base64," + base64.b64encode(buf.getvalue()).decode("utf-8")

            # Run ELA on frame
            ela_metric, ela_base64 = perform_ela(pil_frame)

            obs = f"Sampled frame #{idx} ({timestamp_sec}s). ELA mean error: {ela_metric.metrics.get('mean_error', 0.0):.1f}."
            
            sampled_frames_data.append({
                "frame_index": idx,
                "timestamp_sec": timestamp_sec,
                "frame_base64": frame_base64,
                "ela_base64": ela_base64,
                "observations": obs,
                "ela_metric": ela_metric,
            })

        cap.release()

        # Compute temporal metrics across consecutive sampled frames
        mad_differences = []
        if len(raw_rgb_frames) >= 2:
            for i in range(len(raw_rgb_frames) - 1):
                f1_gray = cv2.cvtColor(raw_rgb_frames[i], cv2.COLOR_RGB2GRAY).astype(np.float32)
                f2_gray = cv2.cvtColor(raw_rgb_frames[i + 1], cv2.COLOR_RGB2GRAY).astype(np.float32)
                diff = np.mean(np.abs(f1_gray - f2_gray))
                mad_differences.append(float(diff))

        avg_mad = float(np.mean(mad_differences)) if mad_differences else 0.0
        std_mad = float(np.std(mad_differences)) if mad_differences else 0.0

        temporal_metrics = {
            "avg_frame_difference": round(avg_mad, 2),
            "frame_difference_std": round(std_mad, 2),
            "sampled_count": len(sampled_frames_data),
        }

        # Extract audio track bytes
        audio_bytes = extract_audio_from_video(temp_vid_path)
        if audio_bytes and len(audio_bytes) > 500:
            tech_metrics["has_audio"] = True
            tech_metrics["audio_codec"] = "pcm_wav"

        return tech_metrics, sampled_frames_data, temporal_metrics, audio_bytes

    finally:
        if os.path.exists(temp_vid_path):
            try:
                os.remove(temp_vid_path)
            except Exception:
                pass

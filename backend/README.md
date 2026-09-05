# TrueLens Backend

FastAPI multi-signal media forensic verification engine for Images, Audio, and Video.

## Features & Architecture
- **Multi-Signal Image Forensics**: EXIF metadata, ELA compression heatmaps, High-Pass noise residuals, 2D FFT spectral grid.
- **Audio Acoustics Forensics**: STFT spectral flatness, centroid, zero-crossing rate, RMS energy dynamics, dynamic spectrogram generator.
- **Video Forensics**: 5-point frame sampler, inter-frame MAD motion continuity, keyframe ELA compression variance, demuxed audio forensics.
- **Provenance Suite**: C2PA Content Credentials inspector, metadata extractor, modular reverse search provider.
- **Evidence Explainer**: Grounded GenAI explanation layer with deterministic local fallback.

## Running Backend

```bash
# Install Python dependencies
pip install -r requirements.txt

# Launch FastAPI development server
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000
```

API Documentation available at `http://127.0.0.1:8000/docs`.

## Running Pytest Suite

```bash
python -m pytest tests/
```

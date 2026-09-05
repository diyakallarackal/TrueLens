import io
from typing import Dict, Any, Tuple
from PIL import Image, ExifTags
from app.services.detectors.base import SignalMetric


# Common AI generation software & parameter keyphrases
AI_SOFTWARE_SIGNATURES = [
    "stable diffusion",
    "midjourney",
    "dall-e",
    "dalle",
    "automatic1111",
    "comfyui",
    "novelai",
    "c2pa",
    "adobe firefly",
    "photoshop",
    "gimp",
    "generation parameters",
    "negative prompt",
    "steps:",
    "sampler:",
    "cfg scale:",
    "seed:",
]

CAMERA_HARDWARE_TAGS = [
    "Make",
    "Model",
    "FNumber",
    "ExposureTime",
    "ISOSpeedRatings",
    "FocalLength",
    "LensModel",
    "DateTimeOriginal",
]

STANDARD_AI_RESOLUTIONS = {
    (512, 512),
    (768, 768),
    (1024, 1024),
    (512, 768),
    (768, 512),
    (896, 1152),
    (1152, 896),
    (1024, 1536),
    (1536, 1024),
}


def extract_exif_data(pil_image: Image.Image) -> Dict[str, Any]:
    """
    Extracts raw EXIF tags from a Pillow Image safely without crashing.
    """
    metadata: Dict[str, Any] = {
        "has_exif": False,
        "raw_tags": {},
        "software_detected": None,
        "camera_make": None,
        "camera_model": None,
        "has_camera_hardware": False,
    }

    try:
        exif_raw = pil_image.getexif()
        if exif_raw:
            metadata["has_exif"] = True
            for tag_id, value in exif_raw.items():
                tag_name = ExifTags.TAGS.get(tag_id, str(tag_id))
                # Format string values cleanly
                if isinstance(value, bytes):
                    try:
                        value = value.decode("utf-8", errors="ignore").strip()
                    except Exception:
                        value = str(value)
                metadata["raw_tags"][tag_name] = str(value)

            # Check standard tag shortcuts
            metadata["camera_make"] = metadata["raw_tags"].get("Make")
            metadata["camera_model"] = metadata["raw_tags"].get("Model")
            metadata["software_detected"] = metadata["raw_tags"].get("Software")

            # Check camera hardware tags presence
            has_camera_tags = any(tag in metadata["raw_tags"] for tag in CAMERA_HARDWARE_TAGS)
            metadata["has_camera_hardware"] = has_camera_tags

    except Exception:
        # Never crash if EXIF extraction fails
        metadata["has_exif"] = False

    return metadata


def analyze_exif_signals(pil_image: Image.Image, metadata: Dict[str, Any]) -> SignalMetric:
    """
    Evaluates metadata consistency and software traces.
    """
    w, h = pil_image.size
    raw_tags_str = " ".join([f"{k}:{v}" for k, v in metadata.get("raw_tags", {}).items()]).lower()
    
    found_ai_keywords = []
    for sig in AI_SOFTWARE_SIGNATURES:
        if sig in raw_tags_str:
            found_ai_keywords.append(sig)

    has_camera = metadata.get("has_camera_hardware", False)
    has_exif = metadata.get("has_exif", False)
    is_standard_ai_res = (w, h) in STANDARD_AI_RESOLUTIONS or (h, w) in STANDARD_AI_RESOLUTIONS

    # Score logic
    score = 0.0
    confidence = 85.0
    severity = "Low"
    description_parts = []

    if found_ai_keywords:
        score += 85.0
        severity = "High"
        description_parts.append(f"Detected software/AI markers in metadata: {', '.join(found_ai_keywords[:3])}.")
    
    if not has_camera and not has_exif:
        score += 25.0
        description_parts.append("Image lacks standard camera hardware EXIF metadata.")
    elif has_camera:
        score = max(0.0, score - 30.0)
        description_parts.append(f"Genuine camera metadata present ({metadata.get('camera_make', '')} {metadata.get('camera_model', '')}).")

    if is_standard_ai_res and not has_camera:
        score += 20.0
        description_parts.append(f"Image dimensions ({w}x{h}) match standard AI generator output baselines.")

    # Clamp score to [0, 100]
    score = float(max(0.0, min(100.0, score)))

    if score >= 70:
        severity = "High"
    elif score >= 40:
        severity = "Medium"

    if not description_parts:
        description_parts.append("Metadata structure shows no obvious synthetic markers.")

    return SignalMetric(
        id="exif_software_tag",
        name="Metadata & Camera Integrity",
        score=round(score, 1),
        severity=severity,
        confidence=confidence,
        description=" ".join(description_parts),
        metrics={
            "has_exif": has_exif,
            "has_camera_hardware": has_camera,
            "ai_keywords_found": found_ai_keywords,
            "camera_make": metadata.get("camera_make"),
            "camera_model": metadata.get("camera_model"),
            "is_standard_ai_resolution": is_standard_ai_res,
        }
    )

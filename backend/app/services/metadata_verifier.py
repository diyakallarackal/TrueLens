from typing import Dict, Any, Optional


class MetadataVerifier:
    """
    Media-specific metadata verifier for Images, Audio, and Video.
    Extracts genuine metadata fields or explicitly marks them as 'Not available'.
    Never interprets missing metadata as proof of manipulation.
    """

    def verify_image_metadata(self, metadata: Dict[str, Any], filename: str, file_size: int) -> Dict[str, Any]:
        has_exif = metadata.get("has_exif", False)
        has_camera = metadata.get("has_camera_hardware", False)
        camera_make = metadata.get("camera_make") or "Not available"
        camera_model = metadata.get("camera_model") or "Not available"
        software = metadata.get("software_detected") or "Not available"
        raw_tags = metadata.get("raw_tags", {})

        gps_info = "Not available"
        if "GPSInfo" in raw_tags or any("GPS" in k for k in raw_tags.keys()):
            gps_info = "GPS coordinates present in EXIF header"

        summary_parts = []
        if has_camera and camera_make != "Not available":
            summary_parts.append(f"Genuine camera hardware tags found ({camera_make} {camera_model}).")
        elif not has_exif:
            summary_parts.append("Image header lacks embedded EXIF tags.")

        if software != "Not available":
            summary_parts.append(f"Software tag detected in header ({software}).")

        return {
            "has_metadata": has_exif,
            "has_camera_hardware": has_camera,
            "camera_make": camera_make,
            "camera_model": camera_model,
            "software_detected": software,
            "gps_info": gps_info,
            "hardware_signature": f"Camera ({camera_make} {camera_model})" if has_camera else "Software/Header Only",
            "summary": " ".join(summary_parts) if summary_parts else "Standard image metadata extracted.",
        }

    def verify_audio_metadata(self, tech_metrics: Dict[str, Any], filename: str, file_size: int) -> Dict[str, Any]:
        codec = tech_metrics.get("codec") or "Not available"
        sample_rate = f"{tech_metrics.get('sample_rate')} Hz" if tech_metrics.get("sample_rate") else "Not available"
        channels = tech_metrics.get("channels") or "Not available"
        bitrate = f"{tech_metrics.get('bitrate_kbps')} kbps" if tech_metrics.get("bitrate_kbps") else "Not available"
        duration = f"{tech_metrics.get('duration_seconds')}s" if tech_metrics.get("duration_seconds") else "Not available"

        summary_parts = [f"Audio stream decoded: {codec}, {sample_rate}, {channels} channel(s)."]
        if bitrate != "Not available":
            summary_parts.append(f"Bitrate: {bitrate}.")

        return {
            "has_metadata": bool(tech_metrics.get("sample_rate")),
            "codec": codec,
            "sample_rate": sample_rate,
            "channels": channels,
            "bitrate": bitrate,
            "duration": duration,
            "hardware_signature": "Audio Stream Header",
            "summary": " ".join(summary_parts),
        }

    def verify_video_metadata(self, tech_metrics: Dict[str, Any], filename: str, file_size: int) -> Dict[str, Any]:
        codec = tech_metrics.get("codec") or "Not available"
        fps = f"{tech_metrics.get('fps')} FPS" if tech_metrics.get("fps") else "Not available"
        dimensions = f"{tech_metrics.get('width')}x{tech_metrics.get('height')}" if tech_metrics.get("width") else "Not available"
        duration = f"{tech_metrics.get('duration')}s" if tech_metrics.get("duration") else "Not available"
        has_audio = tech_metrics.get("has_audio", False)
        audio_codec = tech_metrics.get("audio_codec") if has_audio else "No audio track detected"

        summary_parts = [f"Video stream container decoded: {dimensions}, {fps}, {codec}."]
        if has_audio:
            summary_parts.append(f"Embedded audio stream present ({audio_codec}).")
        else:
            summary_parts.append("No embedded audio track detected.")

        return {
            "has_metadata": bool(tech_metrics.get("width")),
            "codec": codec,
            "fps": fps,
            "dimensions": dimensions,
            "duration": duration,
            "has_audio_track": has_audio,
            "audio_codec": audio_codec,
            "hardware_signature": "Video Container Header",
            "summary": " ".join(summary_parts),
        }
